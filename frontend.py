#!/usr/bin/env python
"""
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from email import message
import logging
from typing import Dict
import os
import re

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,

)
import backend as m



# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard_set_1 = [
    ['Generate IP', 'Generate list'],
    ['Remove IP'],
    ['Done'],
]

reply_keyboard_set_2 = [
    ['Device name', 'Mac', 'Description'],
    ['Who is in charge', 'Serial number'],
    ['READY', 'Back']
]

markup_set_1 = ReplyKeyboardMarkup(reply_keyboard_set_1, one_time_keyboard=True)
markup_set_2 = ReplyKeyboardMarkup(reply_keyboard_set_2, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> int:
    """Start the parser"""
    global path
    global ip_config
    global chat_ids
    global subnet

    chat_ids = set()
    subnet = '192.168.4.0/24'
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    path = f'{cur_dir}/external_dir/reserved_list.csv'
    ip_config ={
        'Device name': '',
        'Mac': '',
        'Description': '',
        'Who is in charge': '',
        'Serial number': ''
    } 
    update.message.reply_text(f"Hello, {update.message.chat.first_name}", reply_markup=markup_set_1)

    return CHOOSING


def button_back(update: Update, context: CallbackContext):
    update.message.reply_text('Main menu', reply_markup=markup_set_1)

    return CHOOSING


def generate_ip_menu(update: Update, context: CallbackContext) -> int:
    """Menu select buttons.""" 
    update.message.reply_text(
        'Optional for get IP \n' 
        'Input your Device name, Mac, Description, Who is in charge, Serial number. ',
        reply_markup=markup_set_2
        )

    return TYPING_CHOICE


def select_ip_config(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about ip config."""
    text = update.message.text
    context.user_data['choice'] = text 
    update.message.reply_text(f'Input {text}', reply_markup=markup_set_2)

    return TYPING_REPLY 

def generate_list_menu(update: Update, context: CallbackContext) -> int:
    """Menu for create list with busy ip address."""
    global path
    global subnet
    chat_id = update.message.chat.id
    m.generate_list(path, subnet)
    update.message.reply_text('Your IP list', reply_markup=markup_set_1)
    context.bot.send_document(chat_id=chat_id, document=open(path, 'rb'))

    return CHOOSING

def remove_ip_menu(update: Update, context: CallbackContext) -> int:
    """Menu for remove from IP list."""
    context.user_data['choice'] = 'remove_ip'
    update.message.reply_text('Input your IP for del')

    return TYPING_REPLY


def received_information_to_csv(update: Update, context: CallbackContext) -> int:
    """  receive iformation from user   """
    user_data = context.user_data
    text = update.message.text

    if 'choice' in user_data.keys():
        category = user_data['choice']
        user_data[category] = text
        del user_data['choice']
    if category in ip_config.keys():
        ip_config[category] = text
        
        update.message.reply_text(
        f"{facts_to_str(user_data)}", reply_markup=markup_set_2)

    if 'remove_ip' in user_data.keys():
        remove_ip(update, context)
        return CHOOSING
    
    return TYPING_CHOICE


def remove_ip(update: Update, context: CallbackContext):
    """ remove choise IP """
    global path
    pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    ip = context.user_data.pop('remove_ip')
    if re.findall(pattern, ip):
        fb_remove_ip = m.remove_ip(path, ip)
        update.message.reply_text(f"{fb_remove_ip} {ip}", reply_markup=markup_set_1)
    else:
        update.message.reply_text(f" {ip} Not valid, try again", reply_markup=markup_set_1)
        
    return CHOOSING


def get_ip(update: Update, context: CallbackContext) -> int:
    """get free IP adres """
    global path
    global subnet
    global ip_config
    result_ip = m.generate_ip(path, subnet, ip_config)
    update.message.reply_text(f'Your IP: {result_ip}', reply_markup=markup_set_1)

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    """End the parser."""
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']
    update.message.reply_text(
        f"Have a nice day! Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )
    user_data.clear()

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    updater = Updater('5107682330:AAG1_B4pRtjZgliRdYQugT_YFqwHj2H51mg') 
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex(r'^Generate list$'), generate_list_menu), 
                MessageHandler(Filters.regex(r'^Generate IP$'), generate_ip_menu),
                MessageHandler(Filters.regex(r'^Remove IP$'), remove_ip_menu)
            ],
            TYPING_CHOICE: [
                MessageHandler(Filters.regex(r'^(Device name|Mac|Description|Who is in charge|Serial number)$'), select_ip_config),
                MessageHandler(Filters.regex(r'^READY$'), get_ip),
                MessageHandler(Filters.regex(r'^Back$'), button_back),
            ],
            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex(r'^Done$')), received_information_to_csv)
            ],
        },
        fallbacks=[MessageHandler(Filters.regex(r'^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)


    updater.start_polling()


    updater.idle()


if __name__ == '__main__':
    main()

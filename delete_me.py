#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
Code was copyed from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot2.py
"""

import logging
from os import path
import pandas as pd
from typing import Dict

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ['Get IP list', 'Get new IP'],
    ['Remove IP']
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(
        "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
        "Why don't you tell me something about yourself?",
        reply_markup=markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    ##text = update.message.text
    #context.user_data['choice'] = text
    #update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')

    return TYPING_REPLY

def remove_ip(update: Update, context: CallbackContext)->int:
    '''
    Removes ip from reserved list.
    '''
    global path
    text = update.message.text
    df=pd.read_csv(path)
    if ip in df['IP']:
        df.drop(df[df["IP"]==ip].index, inplace=True)
        df.to_csv(path, index=False)
    else:
        print('No such IP')

def received_information(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    #del user_data['choice']

    update.message.reply_text(
        f"{Filters.command}"
        "Neat! Just so you know, this is what you already told me:"
        f"{facts_to_str(user_data)} You can tell me more, or change your opinion"
        " on something.",
        reply_markup=markup,
    )

    return CHOOSING


def done(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    chat_ids = set()
    subnet = '192.168.4.0/24'
    path = '/home/andrey/Documents/generate_ip/reserved_list.csv'
    #generate_list(reserved_list_path, subnet)
    #generate_ip(path,subnet)
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5102543900:AAH1DBhEobhE5E2L07B3b4mfKkZRJtqO004")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Get IP list)$'), regular_choice
                ),
                MessageHandler(
                    Filters.regex('^(Get new IP)$'), regular_choice
                ),
                MessageHandler(
                    Filters.regex('^(Remove IP)$'), regular_choice
                ),
            ],
            #TYPING_CHOICE: [
            #    MessageHandler(
            #        Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
            #    )
            #],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command == "Remove IP" | Filters.regex('^Done$')),
                    remove_ip,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
# generate_ip
Telegram bot. Generates next free ip from Cognitive's Moscow office network and adds it into a reserved list. Removes reserved ips from list. Generates list of current reserved ips with description.
main.py - модуль, где реализованы функции для сохранения, поиска и удаленя свободных/занятых ip адресов в csv - файл reserved_list.csv
delete_me.py - попытка сделать телеграм - бота с меню, который будет пользоваться модулем main.py как бекэндом.

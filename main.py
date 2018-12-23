# -*- coding: utf-8 -*-

# Telegram libraries
import telegram
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler

# Config libraries
from functions import TOKEN, yaml

# commands
from functions import start, give_chat_id, send_log, send_errors, scrape_notices

bot = telegram.Bot(TOKEN)

with open('config/settings.yaml') as yaml_config:
	config_map = yaml.load(yaml_config)

def logging_message(bot, update):
	message_id = update.message.message_id #ID MESSAGGI\O
	user = update.message.from_user # Restituisce un oggetto Telegram.User
	chat = update.message.chat # Restituisce un oggetto Telegram.Chat
	text = update.message.text #Restituisce il testo del messaggio
	date = update.message.date #Restituisce la data dell'invio del messaggio
	message = "\n___ID MESSAGE: " 	+ str(message_id) + "____\n" + \
			  "___INFO USER___\n" + \
			  "user_id:" 			+ str(user.id) + "\n" + \
			  "user_name:" 			+ str(user.username) + "\n" + \
			  "user_firstlastname:" + str(user.first_name) + " " + str(user.last_name) + "\n" + \
			  "___INFO CHAT___\n" + \
			  "chat_id:" 			+ str(chat.id) + "\n" + \
			  "chat_type:" 			+ str(chat.type)+"\n" + "chat_title:" + str(chat.title) + "\n" + \
			  "___TESTO___\n" + \
			  "text:" 				+ str(text) + \
			  "date:" 				+ str(date) + \
			  "\n_____________\n"

	log_tmp = open("logs/logs.txt","a+")
	log_tmp.write("\n"+message)


def main():
	updater = Updater(TOKEN, request_kwargs={'read_timeout': 20, 'connect_timeout': 20})
	dp = updater.dispatcher
	dp.add_handler(MessageHandler(Filters.all, logging_message),1)

	dp.add_handler(CommandHandler('start', start))

  # devs commands
	dp.add_handler(CommandHandler('chatid',give_chat_id))
	dp.add_handler(CommandHandler('send_log', send_log))
	dp.add_handler(CommandHandler('errors', send_errors))


	#JobQueue
	j = updater.job_queue
	j.run_repeating(scrape_notices, interval=30, first=0) # job_news

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
    main()

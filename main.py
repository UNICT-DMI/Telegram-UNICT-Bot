# -*- coding: utf-8 -*-

# Telegram libraries
import telegram
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, CallbackQueryHandler

# Config libraries
from functions import TOKEN, yaml

# commands
from functions import start
from module.dev_functions import logging_message, give_chat_id, send_log, send_errors
from module.scraper_notices import scrape_notices
from module.callback_functions import callback_handle

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telegram.Bot(TOKEN)

with open('config/settings.yaml') as yaml_config:
	config_map = yaml.load(yaml_config)

def main():
	updater = Updater(TOKEN, request_kwargs={'read_timeout': 20, 'connect_timeout': 20})
	dp = updater.dispatcher
	dp.add_handler(MessageHandler(Filters.all, logging_message),1)

	dp.add_handler(CommandHandler('start', start))

	dp.add_handler(CallbackQueryHandler(callback_handle))

  # devs commands
	dp.add_handler(CommandHandler('chatid',give_chat_id))
	dp.add_handler(CommandHandler('send_log', send_log))
	dp.add_handler(CommandHandler('errors', send_errors))


	#JobQueue
	j = updater.job_queue
	j.run_repeating(scrape_notices, interval=config_map["news_interval"], first=0) # job_news

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
    main()

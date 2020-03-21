# -*- coding: utf-8 -*-

# Telegram libraries
import telegram
import traceback

from telegram import Update, Bot
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, CallbackQueryHandler, CallbackContext

# Config libraries
from functions import TOKEN, config_map

# commands
from functions import start
from module.dev_functions import logging_message, give_chat_id, send_logfile, clear_logfile, post_and_clear_logs
from module.scraper_notices import scrape_notices
from module.callback_functions import callback_handle

import logging

def setup_logging(logs_file):
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()

    file_handler = logging.FileHandler("{}.log".format(logs_file))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.INFO)

def main():
    setup_logging("logfile")

    logging.info("Initialization...")

    bot = telegram.Bot(TOKEN)

    updater = Updater(TOKEN, use_context=True) # request_kwargs={'read_timeout': 20, 'connect_timeout': 20}, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.all, logging_message),1)

    # start command
    dp.add_handler(CommandHandler('start', start))

    # callback handlers
    dp.add_handler(CallbackQueryHandler(callback_handle))

      # devs commands
    dp.add_handler(CommandHandler('chatid',give_chat_id))
    dp.add_handler(CommandHandler('send_logfile', send_logfile))
    dp.add_handler(CommandHandler('clear_logfile', clear_logfile))

    # dp.add_handler(CommandHandler('send_log', send_log))
    # dp.add_handler(CommandHandler('errors', send_errors))

    #JobQueue
    j = updater.job_queue

    j.run_repeating(post_and_clear_logs, interval=config_map["logfile_reset_interval_minutes"] * 60, first=0) # logfile reset
    j.run_repeating(scrape_notices, interval=config_map["news_interval"], first=0) # job_news

    logging.info("Scraping jobs started")

    updater.start_polling()
    # updater.idle()

if __name__ == '__main__':
    main()

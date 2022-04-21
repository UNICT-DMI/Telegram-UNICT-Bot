import logging

from telegram.ext import Updater, Filters, MessageHandler, CommandHandler, CallbackQueryHandler

# Config libraries
from functions import TOKEN, config_map

# commands
from functions import start
from module.dev_functions import logging_message, give_chat_id, send_logfile, clear_logfile, post_and_clear_logs
from module.callback_functions import callback_handle
from module.update import update_tick


def setup_logging(logs_file: str):
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

    updater = Updater(TOKEN)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.all, logging_message), 1)

    # start command
    dp.add_handler(CommandHandler('start', start))

    # callback handlers
    dp.add_handler(CallbackQueryHandler(callback_handle))

    # devs commands
    dp.add_handler(CommandHandler('chatid', give_chat_id))
    dp.add_handler(CommandHandler('send_logfile', send_logfile))
    dp.add_handler(CommandHandler('clear_logfile', clear_logfile))

    # dp.add_handler(CommandHandler('send_log', send_log))
    # dp.add_handler(CommandHandler('errors', send_errors))

    # JobQueue
    j = updater.dispatcher.job_queue

    j.run_repeating(post_and_clear_logs, interval=config_map["logfile_reset_interval_minutes"] * 60,
                    first=5)  # logfile reset
    j.run_repeating(update_tick, interval=config_map["update_interval"], first=5)  # job_news

    logging.info("Scraping jobs started")

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

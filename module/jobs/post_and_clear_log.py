"""Post and clear job"""
import logging
from datetime import datetime
from telegram.ext import CallbackContext
from module.data import config_map, CLEAR_LOGFILE_TEXT


def post_and_clear_log_job(context: CallbackContext) -> None:
    """Called by a scheduled job.
    Sends the logfile in the chat and then clears it by overwriting it with an empty file.

    Args:
        context: context passed by the job
    """
    logging.info("Automatic sending current logfile into the group...")

    try:
        with open("logfile.log", "rb") as logfile:
            context.bot.sendDocument(
                chat_id=config_map["log_group_chatid"],
                document=logfile,
                filename=f"unict-bot_logfile_({datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}",
                caption="Automatically generated logfile",
            )
    except FileNotFoundError:
        logging.info("No logfile found")

    logging.info("Deleting current logfile...")

    with open("logfile.log", "w", encoding="utf-8"):  # overwrite the logfile with an empty file
        pass

    context.bot.sendMessage(chat_id=config_map["log_group_chatid"], text=CLEAR_LOGFILE_TEXT)

"""/clear_logfile command"""
import logging
from telegram import Update
from telegram.ext import CallbackContext
from module.data import config_map, CLEAR_LOGFILE_TEXT


def clear_logfile_cmd(update: Update, context: CallbackContext) -> None:
    """Called by the /clear_logfile command.
    Overwrites the logfile with an empty file.
    The command can only be invoked from the group indicated by the log_group_chatid.

    Args:
        update: update event
        _: context passed by the handler
    """
    # only the log channel can clear the log file
    if update.message.chat_id != config_map["log_group_chatid"]:
        return

    logging.info("Clearing logfile...")
    with open("logfile.log", "w", encoding="utf-8"):  # overwrite the logfile with an empty file
        pass
    context.bot.send_message(chat_id=config_map["log_group_chatid"], text=CLEAR_LOGFILE_TEXT)

"""/send_logfile command"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext
from module.data import config_map


def send_logfile_cmd(update: Update, context: CallbackContext) -> None:
    """Called by the /send_logfile command.
    Sends the logfile in the chat.
    The command can only be invoked from the group indicated by the log_group_chatid.

    Args:
        update: update event
        context: context passed by the handler
    """
    # only the log channel can request the log file
    if update.message.chat_id != config_map["log_group_chatid"]:
        return

    logging.info("Sending logfile...")
    with open("logfile.log", "rb") as logfile:
        context.bot.sendDocument(
            chat_id=config_map["log_group_chatid"],
            document=logfile,
            filename=f"unict-bot_logfile_({datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}",
        )

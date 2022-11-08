"""/start command"""
from telegram import Update
from telegram.ext import CallbackContext
from module.data import START_TEXT


def start_cmd(update: Update, _: CallbackContext) -> None:
    """Called by the /start command.
    Sends a welcome message to the user.

    Args:
        update: update event
        _: context passed by the handler
    """
    update.message.reply_text(START_TEXT)

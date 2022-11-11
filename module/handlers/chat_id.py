"""/chatid command"""
from telegram import Update
from telegram.ext import CallbackContext


def chat_id_cmd(update: Update, _: CallbackContext) -> None:
    """Called by the /chatid command.
    Sends the chat id of the chat where the command is invoked.

    Args:
        update: update event
        _: context passed by the handler
    """
    update.message.reply_text(str(update.message.chat_id))

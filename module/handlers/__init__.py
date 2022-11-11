"""Handlers module"""
from telegram import BotCommand
from telegram.ext import (
    Updater,
    Dispatcher,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
)
from .start import start_cmd
from .chat_id import chat_id_cmd
from .log import log_msg
from .send_logfile import send_logfile_cmd
from .clear_logfile import clear_logfile_cmd


def set_commands(updater: Updater) -> None:
    """Adds the list of commands with their description to the bot

    Args:
        updater: supplied Updater
    """
    commands = [
        BotCommand("start", "presentazione iniziale del bot"),
        BotCommand("chatid", "ottieni la chat id corrente"),
    ]
    updater.bot.set_my_commands(commands=commands)


def add_handlers(dp: Dispatcher) -> None:
    """Add all the handlers to the dispatcher.
    They will be called when the corresponding update event is received.

    Args:
        dp: event dispatcher
    """
    # Logging
    dp.add_handler(MessageHandler(Filters.all, log_msg), 1)

    # Commands
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("chatid", chat_id_cmd))

    # Dev and debug
    dp.add_handler(CommandHandler("send_logfile", send_logfile_cmd))
    dp.add_handler(CommandHandler("clear_logfile", clear_logfile_cmd))

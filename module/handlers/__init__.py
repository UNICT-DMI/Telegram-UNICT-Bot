"""Handlers module"""
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    Filters,
    JobQueue,
    CallbackQueryHandler,
)
from module.data import config_map
from module.scraping.update import update_tick
from .start import start_cmd
from .chat_id import chat_id_cmd
from .log import log_msg
from .send_logfile import send_logfile_cmd
from .clear_logfile import clear_logfile_cmd
from .post_and_clear_log import post_and_clear_log_job
from .callback_functions import callback_handle


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

    # Admin approve/reject callbacks
    dp.add_handler(CallbackQueryHandler(callback_handle))


def add_jobs(job_queue: JobQueue) -> None:
    """Add all the jobs to the job queue.
    They will be called periodically.

    Args:
        job_queue: job queue
    """
    # logfile reset
    job_queue.run_repeating(
        post_and_clear_log_job, interval=config_map["logfile_reset_interval_minutes"] * 60, first=5
    )
    # job_news
    job_queue.run_repeating(update_tick, interval=config_map["update_interval"], first=5)

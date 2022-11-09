"""Enqueue notices for a given channel"""
import time
import logging
import traceback
from telegram.ext import CallbackContext
from telegram.error import BadRequest, Unauthorized, TelegramError, RetryAfter
from module.data import config_map
from .notice import Notice


def send_notice(context: CallbackContext, chat_id: "str | int", notice: Notice):
    """Try to send the notice to the given chat_id, retrying if necessary
    after a delay up to the maximum number of retries specified in the config.

    Args:
        context: context passed by the handler
        chat_id: chat_id to send the message to
        notice_message: message to send
    """
    logging.info("Call send_notice(%s, %s, %s)", context, chat_id, notice)

    sent = False
    tries = 0

    while not sent and tries < config_map["max_connection_tries"]:
        try:
            context.bot.sendMessage(chat_id=chat_id, text=notice.formatted_message, parse_mode="HTML")
            sent = True
            logging.info("Notice sent to %s", chat_id)
        except RetryAfter as err:
            logging.warning("Retry after error encountered, retrying in 30 seconds")
            time.sleep(err.retry_after)
            tries += 1
            continue
        except (BadRequest, Unauthorized, TelegramError):
            logging.exception("Exception on call enqueue_notice(%s)", context)
            logging.exception(traceback.format_exc())

import time
import logging
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.error import BadRequest, Unauthorized, TelegramError, RetryAfter

from module.data import config_map

# TODO: make the approve system work
def enqueue_notice(
    context: CallbackContext, page_data, notices_data, full_url, link_content, approval_group_chatid=None
):
    logging.info(
        "Call enqueue_notice(%s, %s, %s, %s, %s, %s)",
        context,
        page_data,
        notices_data,
        full_url,
        link_content,
        approval_group_chatid,
    )

    try:
        if approval_group_chatid:
            # TODO: Implement this
            # If the channel is filtered, send a request to the approval group

            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Accetta ✔", callback_data="news,approved,{},{}".format()),
                        InlineKeyboardButton("Rifiuta ❌", callback_data="news,rejected,{},{}".format()),
                    ]
                ]
            )

            context.bot.sendMessage(
                chat_id=approval_group_chatid,
                text=notice_message,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        else:
            # Otherwise send a direct message on each channel

            notice_message = format_notice_message(page_data["label"], clear_url(full_url), link_content)

            for channel in page_data["channels"]:
                send_notice(context, channel, notice_message)

    except (BadRequest, Unauthorized, TelegramError):
        logging.exception("Exception on call enqueue_notice(%s)", context)
        logging.exception(traceback.format_exc())


def clear_url(url: str) -> str:
    # Remove trailing slashes, added concatenating base URLs with local hrefs
    url = url.replace("it//", "it/")
    return url


def format_notice_message(label: str, url: str, link_content) -> str:
    message = f"<b>[{label}]</b>\n{url}\n<b>{link_content[0]}</b>\n{format_content(link_content[1])}"
    return message


# Message formatting
def format_content(content: str) -> str:
    max_len = config_map["max_messages_length"]

    # If message content is too long, cut it and add a footer
    if len(content) > max_len:
        split_index = max_len - 1

        while content[split_index] != " ":
            split_index = split_index - 1

        content = f"{content[:split_index]}{config_map['max_length_footer']}"

    return content


def send_notice(context: CallbackContext, chat_id: int, notice_message: str):
    """Try to send the notice to the given chat_id, retrying if necessary
    after a delay up to the maximum number of retries specified in the config.

    Args:
        context: context passed by the handler
        chat_id: chat_id to send the message to
        notice_message: message to send
    """
    logging.info("Call send_notice(%s, %s, %s)", context, chat_id, notice_message)

    sent = False
    tries = 0

    while not sent and tries < config_map["max_connection_tries"]:
        try:
            context.bot.sendMessage(chat_id=chat_id, text=notice_message, parse_mode="HTML")
            sent = True
            logging.info("Notice sent to %s", chat_id)
        except RetryAfter as err:
            logging.warning("Retry after error encountered, retrying in 30 seconds")
            time.sleep(err.retry_after)
            tries += 1
            continue

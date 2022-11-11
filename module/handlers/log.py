"""log handler"""
from telegram import Update
from telegram.ext import CallbackContext


def log_msg(update: Update, _: CallbackContext) -> None:
    """Called by each message received by the bot.
    Logs the message in the logfile.

    Args:
        update: update event
        _: context passed by the handler
    """
    try:
        message_id = update.message.message_id  # ID MESSAGGI\O
        user = update.message.from_user  # Restituisce un oggetto Telegram.User
        chat = update.message.chat  # Restituisce un oggetto Telegram.Chat
        text = update.message.text  # Restituisce il testo del messaggio
        date = update.message.date  # Restituisce la data dell'invio del messaggio
        message = (
            f"\n___ID MESSAGE: {message_id}____\n"
            "___INFO USER___\n"
            f"user_id: {user.id}\n"
            f"user_name: {user.username}\n"
            f"user_firstlastname: {user.first_name} {user.last_name}\n"
            "___INFO CHAT___\n"
            f"chat_id: {chat.id}\n"
            f"chat_type: {chat.type}\n"
            f"chat_title: {chat.title}\n"
            "___TESTO___\n"
            f"text: {text}"
            f"date: {date}"
            "\n_____________\n"
        )

        with open("logs/logs.txt", "a+", encoding="utf-8") as log:
            log.write(message)
    except (FileNotFoundError, FileExistsError):
        pass

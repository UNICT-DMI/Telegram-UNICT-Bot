import logging
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext

from module.config import load_configurations

config_map = load_configurations()


def logging_message(update: Update, context: CallbackContext):
    try:
        message_id = update.message.message_id  # ID MESSAGGI\O
        user = update.message.from_user  # Restituisce un oggetto Telegram.User
        chat = update.message.chat  # Restituisce un oggetto Telegram.Chat
        text = update.message.text  # Restituisce il testo del messaggio
        date = update.message.date  # Restituisce la data dell'invio del messaggio
        message = "\n___ID MESSAGE: " + str(message_id) + "____\n" + \
                  "___INFO USER___\n" + \
                  "user_id:" + str(user.id) + "\n" + \
                  "user_name:" + str(user.username) + "\n" + \
                  "user_firstlastname:" + str(user.first_name) + " " + str(user.last_name) + "\n" + \
                  "___INFO CHAT___\n" + \
                  "chat_id:" + str(chat.id) + "\n" + \
                  "chat_type:" + str(chat.type) + "\n" + "chat_title:" + str(chat.title) + "\n" + \
                  "___TESTO___\n" + \
                  "text:" + str(text) + \
                  "date:" + str(date) + \
                  "\n_____________\n"

        log_tmp = open("logs/logs.txt", "a+")
        log_tmp.write("\n" + message)
    except Exception:
        pass


# Devs Commands
def generate_current_logfile_name():
    "unict-bot_logfile_({})".format(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))


def give_chat_id(update: Update, context: CallbackContext):
    update.message.reply_text(str(update.message.chat_id))


def send_logfile(update: Update, context: CallbackContext):
    logging.info("Sending logfile...")

    if config_map['log_group_chatid'] != 0 and update.message.chat_id == config_map['log_group_chatid']:
        context.bot.sendDocument(chat_id=config_map['log_group_chatid'],
                                 document=open('logfile.log', 'rb'),
                                 filename=generate_current_logfile_name())


def clear_logfile(update: Update, context: CallbackContext):
    logging.info("Clearing logfile...")

    if config_map['log_group_chatid'] != 0 and update.message.chat_id == config_map['log_group_chatid']:
        open('logfile.log', 'w').close()

        context.bot.sendMessage(chat_id=config_map['log_group_chatid'], text="Logfile has been cleared")


def post_and_clear_logs(context):
    logging.info("Automatic sending current logfile into the group...")

    try:
        context.bot.sendDocument(
            chat_id=config_map['log_group_chatid'],
            document=open('logfile.log', 'rb'),
            filename=generate_current_logfile_name(),
            caption="Automatically generated logfile",
        )
    except FileNotFoundError:
        logging.info("No logfile found")

    logging.info("Deleting current logfile...")

    # os.remove("logfile.log")
    open('logfile.log', 'w').close()

    context.bot.sendMessage(chat_id=config_map['log_group_chatid'], text="Logfile has been automatically cleared")

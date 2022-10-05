# Telegram
from telegram import Update
from telegram.ext import CallbackContext

from module.config import load_configurations

# Token and config
config_map = load_configurations()

# Token of your telegram bot that you created from @BotFather, write it on token.conf
TOKEN = config_map["token"]


# This function split the message into 2 or more messages in case of message length > 3000
def send_message(context: CallbackContext, chat_id: int, message: str):
    msg = ""
    rows = message.split('\n')
    for row in rows:
        if row.strip() == "" and len(msg) > 3000:
            context.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode='Markdown')
            msg = ""
        else:
            msg += row + "\n"
    context.bot.sendMessage(chat_id=chat_id, text=msg, parse_mode='Markdown')


# Commands
def start(update: Update, context: CallbackContext):
    context.bot.sendMessage(chat_id=update.message.chat_id,
                            text="Benvenuto! Questo bot è stato realizzato dagli studenti di Informatica al fine di "
                                 "suppotare gli studenti dell'Università di Catania! Per scoprire cosa puoi fare usa "
                                 "/help")

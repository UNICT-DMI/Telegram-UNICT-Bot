# -*- coding: utf-8 -*-

# Telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)

import yaml

# Token and config
with open('config/settings.yaml', 'r') as yaml_config:
    config_map = yaml.load(yaml_config, Loader=yaml.SafeLoader)

# Token of your telegram bot that you created from @BotFather, write it on token.conf
TOKEN = config_map["token"]

# This function split the message into 2 or more messages in case of message length > 3000
def send_message(context:CallbackContext, chaitd, messaggio):
    msg = ""
    righe = messaggio.split('\n')
    for riga in righe:
        if riga.strip() == "" and len(msg) > 3000:
            context.bot.sendMessage(chat_id=chaitd, text=msg, parse_mode='Markdown')
            msg = ""
        else:
            msg += riga + "\n"
    context.bot.sendMessage(chat_id=chaitd, text=msg, parse_mode='Markdown')

# Commands
def start(update: Update, context: CallbackContext):
    context.bot.sendMessage(chat_id=update.message.chat_id, text="Benvenuto! Questo bot è stato realizzato dagli studenti di Informatica al fine di suppotare gli studenti dell'Università di Catania! Per scoprire cosa puoi fare usa /help")

# -*- coding: utf-8 -*-

# Telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)

# System libraries
import os
import requests
import yaml
import logging
from urllib.request import urlopen
from bs4 import BeautifulSoup

from module.scraper_notices import scrape_notices

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Token
with open('config/settings.yaml', 'r') as yaml_config:
    config_map = yaml.load(yaml_config)

# Token of your telegram bot that you created from @BotFather, write it on token.conf
TOKEN = config_map["token"]
news = ""

# This function split the message into 2 or more messages in case of message length > 3000
def send_message(bot, update, messaggio):
    msg = ""
    righe = messaggio.split('\n')
    for riga in righe:
        if riga.strip() == "" and len(msg) > 3000:
            bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode='Markdown')
            msg = ""
        else:
            msg += riga + "\n"
    bot.sendMessage(chat_id=update.message.chat_id, text=msg, parse_mode='Markdown')


# Commands
def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Benvenuto! Questo bot è stato realizzato dagli studenti di Informatica al fine di suppotare gli studenti dell'Università di Catania! Per scoprire cosa puoi fare usa /help")


# Devs Commands
def give_chat_id(bot, update):
    update.message.reply_text(str(update.message.chat_id))

def send_log(bot, update):
    if(config_map['dev_group_chatid'] != 0 and update.message.chat_id == config_map['dev_group_chatid']):
        bot.sendDocument(chat_id=config_map['dev_group_chatid'], document=open('logs/logs.txt', 'rb'))

def send_errors(bot, update):
    if(config_map['dev_group_chatid'] != 0 and update.message.chat_id == config_map['dev_group_chatid']):
        bot.sendDocument(chat_id=config_map['dev_group_chatid'], document=open('logs/errors.txt', 'rb'))

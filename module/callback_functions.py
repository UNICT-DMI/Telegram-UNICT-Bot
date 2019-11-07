import yaml

from module.scraper_notices import spam_news_direct

import telegram
from telegram import Update
from telegram.ext import CallbackContext

with open('config/settings.yaml', 'r') as yaml_config:
    config_map = yaml.load(yaml_config, Loader=yaml.SafeLoader)
    notices_urls = config_map["notices_urls"]

def callback_handle(update: Update, context: CallbackContext):
    query = update.callback_query
    query_data = query.data.split(":")

    callback_type = query_data[0]

    # check callback data type
    if callback_type == "news":
        result = query_data[1]
        dep_name = query_data[2]
        page_name = query_data[3]
        channel_folder = query_data[4]
        notice_disk_id = query_data[5]

        # reconstruct the file path using query data
        notice_filename = "{}/in_approvazione/{}_{}.dat".format(channel_folder, page_name, notice_disk_id)
        notice_text = open(notice_filename).read()

        result_message = "rifiutato ❌"

        # if the news has been approved, change result message and broadcast it to the news channel
        if result == "approved":
            page = notices_urls[dep_name]["pages"][page_name]

            for channel in page["channels"]:
                spam_news_direct(context.bot, notice_text, channel)

            result_message = "approvato ✔"

        try:
            context.bot.edit_message_text(text="<b>L'avviso è stato {}</b>:\n\n{}".format(result_message, notice_text),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id,
                            parse_mode='HTML')
        except:
            pass

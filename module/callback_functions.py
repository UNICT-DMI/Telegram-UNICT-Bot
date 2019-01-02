from module.scraper_notices import spam_news_direct

def callback_handle(bot, update):
    query = update.callback_query
    query_data = query.data.split(":")

    callback_type = query_data[0]

    if callback_type == "news":
        result = query_data[1]
        channel = query_data[2]
        channel_folder = query_data[3]
        notice_disk_id = query_data[4]

        notice_filename = "{}/in_approvazione/{}_{}.dat".format(channel_folder, channel, notice_disk_id)
        notice_text = open(notice_filename).read()

        result_message = "rifiutato ❌"

        if result == "approved":
            spam_news_direct(bot, notice_text, channel)

            result_message = "approvato ✔"

        bot.edit_message_text(text="<b>L'avviso è stato {}</b>:\n\n{}".format(result_message, notice_text),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode='HTML')


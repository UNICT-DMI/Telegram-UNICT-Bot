from module.scraper_notices import spam_news_direct

def callback_handle(bot, update):
    query = update.callback_query
    query_data = query.data.split(":")

    callback_type = query_data[0]

    # check callback data type
    if callback_type == "news":
        result = query_data[1]
        channel = query_data[2]
        channel_folder = query_data[3]
        notice_disk_id = query_data[4]

        # reconstruct the file path using query data
        notice_filename = "{}/in_approvazione/{}_{}.dat".format(channel_folder, channel, notice_disk_id)
        notice_text = open(notice_filename).read()

        result_message = "rifiutato ❌"

        # if the news has been approved, change result message and broadcast it to the news channel
        if result == "approved":
            spam_news_direct(bot, notice_text, channel)

            result_message = "approvato ✔"

        bot.edit_message_text(text="<b>L'avviso è stato {}</b>:\n\n{}".format(result_message, notice_text),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          parse_mode='HTML')


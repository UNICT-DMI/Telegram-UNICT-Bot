import requests
import bs4
import ast
import os
import copy
import yaml
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

with open('config/settings.yaml', 'r') as yaml_config:
    config_map = yaml.load(yaml_config)
    notices_urls = config_map["notices_urls"]
    approve_group_chatid = config_map["approve_group_chatid"]

def get_links(label, url):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, 'html.parser')

    result = soup.select("span.field-content a")

    return [
        { label: link.get('href') }
        for link in result if "/docenti/" not in link.get('href')
    ]

def get_content(url):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, "html.parser")

    title = soup.find("h1", attrs={"class": "page-title"}).get_text()
    content = soup.find("div", attrs={"class": "field-item even"}).get_text()

    return title, content

def pull_pending_notice(file_name):
    if os.path.isfile(file_name):
        data = []

        with open(file_name, 'r') as fr:
            data = fr.read().splitlines(True)

        with open(file_name, 'w') as fw:
            fw.writelines(data[1:])

        if len(data) > 0:
            return ast.literal_eval(data[0])
    return None

def get_notice_content(notice_dict, base_url, archive_p, notice_p):
    label = list(notice_dict.keys())[0]
    url = "%s%s" % (base_url, notice_dict[label])

    title, content = get_content(url)
    formatted_notice = '<b>[%s]</b>\n%s\n<b>%s</b>\n%s' % (label, url, title, content)

    with open(archive_p, 'a') as fw:
        fw.write('%s\n' % notice_dict)

    with open(archive_p, 'r') as fr:
        data = fr.read().splitlines(True)

        if len(data) > 50:
            with open(archive_p, 'w') as fw:
                fw.writelines(data[1:])
    
    with open(notice_p, 'w') as fw:
        fw.write(formatted_notice)

def spam_news(bot, notice_p, channel):
    if os.path.isfile(notice_p):
        message = open(notice_p).read()
        if message != "":
            try:
                bot.sendMessage(chat_id=channel, text=message, parse_mode='HTML')
            except Exception as error:
                open("logs/errors.txt", "a+").write("{} {}\n".format(error, channel))
        os.remove(notice_p)

def spam_news_direct(bot, notice_message, channel):
    if notice_message != "":
        try:
            bot.sendMessage(chat_id=channel, text=notice_message, parse_mode='HTML')
        except Exception as error:
            open("logs/errors.txt", "a+").write("{} {}\n".format(error, channel))

def send_news_approve_message(bot, notice_p, channel_folder, pending_approval_folder, channel, group_chatid):
    if os.path.isfile(notice_p):
        notice_message = open(notice_p).read()

        if notice_message != "":
            try:
                notice_disk_id = time.clock()
                approving_notice_filename = "{}/{}/{}_{}.dat".format(channel_folder, pending_approval_folder, channel, notice_disk_id)

                if not os.path.exists(os.path.dirname(approving_notice_filename)):
                    try:
                        os.makedirs(os.path.dirname(approving_notice_filename))
                    except OSError as exc: 
                        if exc.errno != errno.EEXIST:
                            raise

                with open(approving_notice_filename, 'w') as fw:
                    fw.writelines(notice_message[0:])

                keyboard_markup = [
                    [InlineKeyboardButton("Accetta", callback_data="news:approved:{}:{}:{}".format(channel, channel_folder, notice_disk_id)),
                    InlineKeyboardButton("Rifiuta", callback_data="news:rejected:{}:{}:{}".format(channel, channel_folder, notice_disk_id))]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard_markup)

                bot.sendMessage(chat_id=group_chatid, text=notice_message, parse_mode='HTML', reply_markup=reply_markup)
            except Exception as error:
                open("logs/errors.txt", "a+").write("send_news_approve_message: {} {}\n".format(error, channel))
        os.remove(notice_p)


def scrape_notices(bot, job):
    notices_urls_cp = copy.deepcopy(notices_urls)

    for i in notices_urls_cp:
        ch = notices_urls_cp[i]["channel"].replace("@", "")

        # handle multi-channel but same department
        if i.find("_") > -1:
            folder = i[0:i.find("_")]
        else:
            folder = i

        pending_path = "data/avvisi/"+str(folder)+"/"+str(ch)+"_avvisi_in_sospeso.dat"
        archive_path = "data/avvisi/"+str(folder)+"/"+str(ch)+"_avvisi.dat"
        notice_path = "data/avvisi/"+str(folder)+"/"+str(ch)+"_avviso.dat"

        base_url = notices_urls_cp[i]["urls"][list(notices_urls_cp[i]["urls"])[0]]
        base_url = base_url[:base_url.find(".unict.it")] + ".unict.it"

        if not os.path.exists("data/avvisi/"+str(folder)+"/"):
            os.makedirs("data/avvisi/"+str(folder)+"/")

        pending_notice = pull_pending_notice(pending_path)

        if pending_notice:
            get_notice_content(pending_notice, base_url, archive_path, notice_path)
        else:
            notices = []

            for label, url in notices_urls_cp[i]["urls"].items():
                notices.extend(get_links(label, url))

            with open(pending_path, 'a+') as pending_file_handle:
                if os.path.isfile(archive_path):
                    with open(archive_path, 'r') as archive_file_handle:
                        archive_notices = archive_file_handle.read()

                        for notice in notices:
                            if str(notice) not in archive_notices:
                                pending_file_handle.write("%s\n" % notice)
                else:
                    for notice in notices:
                        pending_file_handle.write("%s\n" % notice)

            pending_notice = pull_pending_notice(pending_path)
            if pending_notice:
                get_notice_content(pending_notice, base_url, archive_path, notice_path)
        
        send_news_approve_message(bot, notice_path, "data/avvisi/"+str(folder), "in_approvazione", notices_urls[i]["channel"], approve_group_chatid)
        # spam_news(bot, notice_path, notices_urls[i]["channel"])

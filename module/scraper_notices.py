import requests
import bs4
import ast
import os
import copy
import yaml
import time
import re
import telegram
import logging
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

with open('config/settings.yaml', 'r') as yaml_config:
    config_map = yaml.load(yaml_config, Loader=yaml.SafeLoader)
    notices_urls = config_map["notices_urls"]

def get_links(label, url):
    # logging.info("Call get_links({}, {})".format(label, url))

    try:
        time.sleep(1) # delay to avoid "Max retries exceeds" for too many requests
        req = requests.get(url)
        soup = bs4.BeautifulSoup(req.content, 'html.parser')

        result = soup.select("span.field-content a")

        if (len(result) == 0):
            result = soup.select("strong.field-content a")

        return [
            { label: link.get('href') }
            for link in result if "/docenti/" not in link.get('href')
        ]
    except Exception as e:
        # open("logs/errors.txt", "a+").write("{}\n".format(e))

        logging.exception("Exception on call get_links({}, {})".format(label, url))
        logging.exception(traceback.format_exc())

        return None

def get_content(url):
    # logging.info("Call get_content({})".format(url))

    try:
        time.sleep(1) # delay to avoid "Max retries exceeds" for too many requests
        req = requests.get(url)
        soup = bs4.BeautifulSoup(req.content, "html.parser")

        table_content = ""
        table = soup.find('table')

        if table is not None:
            table_body = table.find('tbody')

            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                for c in cols:
                    table_content += c + "\t"
                table_content +="\n"

            table.decompose() # remove table from content

        title = soup.find("h1", attrs={"class": "page-title"})
        content = soup.find("div", attrs={"class": "field-item even"})
        prof = soup.find("a", attrs={"class": "more-link"})

        if title is not None and content is not None:
            title = title.get_text()
            content = content.get_text()

            content.strip() # trimming
            content += "\n"
            content += table_content

            if prof is not None:
                title = "[" +prof.get_text().replace("Vai alla scheda del prof. ", "") + "]\n" + title
        else:
            return None,None

        title = "\n"+title

        return title, content
    except Exception as e:
        # open("logs/errors.txt", "a+").write("{}\n".format(e))

        logging.exception("Exception on call get_content({})".format(url))
        logging.exception(traceback.format_exc())

        return None,None

def pull_pending_notice(file_name):
    logging.info("Call pull_pending_notice({})".format(file_name))

    try:
        if os.path.isfile(file_name):
            data = []

            with open(file_name, 'r') as fr:
                data = fr.read().splitlines(True)

            with open(file_name, 'w') as fw:
                fw.writelines(data[1:])

            if len(data) > 0:
                return ast.literal_eval(data[0])
        return None
    except Exception as e:
        logging.exception("Exception on call pull_pending_notice({})".format(file_name))
        logging.exception(traceback.format_exc())

        return None

def format_content(content):
    # logging.info("Call format_content({})".format(content))

    try:
        max_len = config_map["max_messages_length"]

        if len(content) > max_len:
            split_index = max_len - 1

            while content[split_index] != ' ':
                split_index = split_index - 1

            content = "{}{}".format(content[:split_index], config_map["max_length_footer"])

        return content
    except Exception as e:
        logging.exception("Exception on call format_content({})".format(content))
        logging.exception(traceback.format_exc())

        return None

def get_notice_content(notice_dict, base_url, archive_p, notice_p):
    # logging.info("Call get_notice_content({}, {}, {}, {})".format(notice_dict, base_url, archive_p, notice_p))

    try:
        label = list(notice_dict.keys())[0]

        post_url = notice_dict[label]
        if not post_url.startswith("/"):
            post_url = "/"+post_url

        url = "%s%s" % (base_url, post_url)

        title, content = get_content(url)

        if title is not None:
            content = format_content(content)

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
    except Exception as e:
        logging.exception("Exception on call get_notice_content({}, {}, {}, {})".format(notice_dict, base_url, archive_p, notice_p))
        logging.exception(traceback.format_exc())

def spam_news(context: CallbackContext, notice_p, channels):
    logging.info("Call spam_news({}, {}, {})".format(context, notice_p, channels))

    try:
        if os.path.isfile(notice_p):
            message = open(notice_p).read()
            if message != "":
                try:
                    for channel in channels:
                        context.bot.sendMessage(chat_id=channel, text=message, parse_mode='HTML')
                except Exception as error:
                    # open("logs/errors.txt", "a+").write("{} {}\n".format(error, channel))

                    logging.exception("Exception while sending message in channel on call spam_news({}, {}, {})".format(context, notice_p, channels))
                    logging.exception(traceback.format_exc())

            os.remove(notice_p)
    except Exception as e:
        logging.exception("Exception on call spam_news({}, {}, {})".format(context, notice_p, channels))
        logging.exception(traceback.format_exc())

# broadcasts a news passed as a direct message in parameters
def spam_news_direct(context: CallbackContext, notice_message, channel):
    logging.exception("Call spam_news_direct({}, {}, {})".format(context, notice_p, channels))

    if notice_message != "":
        try:
            context.bot.sendMessage(chat_id=channel, text=notice_message, parse_mode='HTML')
        except Exception as e:
            logging.exception("Exception on call spam_news_direct({}, {}, {})".format(context, notice_p, channels))
            logging.exception(traceback.format_exc())

def send_news_approve_message(context: CallbackContext, notice_p, channel_folder, dep_name, page_name, group_chatid):
    logging.info("Call send_news_approve_message({}, {}, {}, {}, {}, {})".format(context, notice_p, channel_folder, dep_name, page_name, group_chatid))

    # maybe pending approval folder should be settable, to be reviewed
    pending_approval_folder = "in_approvazione"

    if os.path.isfile(notice_p):
        notice_message = open(notice_p).read()

        if notice_message != "":
            try:
                # notice disk id is used to identify an approval pending message. OS clock's used for this
                notice_disk_id = time.clock()
                approving_notice_filename = "{}/{}/{}_{}.dat".format(channel_folder, pending_approval_folder, page_name, notice_disk_id)

                if not os.path.exists(os.path.dirname(approving_notice_filename)):
                    try:
                        os.makedirs(os.path.dirname(approving_notice_filename))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise

                # write notice data into a file
                with open(approving_notice_filename, 'w') as fw:
                    fw.writelines(notice_message[0:])

                # reply buttons layout
                keyboard_markup = [
                    [InlineKeyboardButton("Accetta ✔", callback_data="news:approved:{}:{}:{}:{}".format(dep_name, page_name, channel_folder, notice_disk_id)),
                    InlineKeyboardButton("Rifiuta ❌", callback_data="news:rejected:{}:{}:{}:{}".format(dep_name, page_name, channel_folder, notice_disk_id))]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard_markup)

                # finally, send the message to the approval group
                context.bot.sendMessage(chat_id=group_chatid, text=notice_message, parse_mode='HTML', reply_markup=reply_markup)
            except Exception as e:
                logging.exception("Exception on call send_news_approve_message({}, {}, {}, {}, {}, {})".format(context, notice_p, channel_folder, dep_name, page_name, group_chatid))
                logging.exception(traceback.format_exc())

        os.remove(notice_p)

def scrape_notices(context):
    logging.info("Call scrape_notices({})".format(context))

    try:
        job = context.job
        notices_urls_cp = copy.deepcopy(notices_urls)

        for i in notices_urls_cp:
            if i.find("_") > -1:
                folder = i[0:i.find("_")]
            else:
                folder = i

            if "pages" in notices_urls_cp[i]:
                for page_name in notices_urls_cp[i]["pages"]:
                    page = notices_urls_cp[i]["pages"][page_name]

                    pending_path = "data/avvisi/"+str(folder)+"/"+page_name+"_avvisi_in_sospeso.dat"
                    archive_path = "data/avvisi/"+str(folder)+"/"+page_name+"_avvisi.dat"
                    notice_path = "data/avvisi/"+str(folder)+"/"+page_name+"_avviso.dat"

                    for url in page["urls"]:
                        base_url = url
                        base_url = base_url[:base_url.find(".unict.it")] + ".unict.it"

                        if not os.path.exists("data/avvisi/"+str(folder)+"/"):
                            os.makedirs("data/avvisi/"+str(folder)+"/")

                        pending_notice = pull_pending_notice(pending_path)

                        if pending_notice:
                            get_notice_content(pending_notice, base_url, archive_path, notice_path)
                        else:
                            notices = []
                            link = get_links(page_name, url)
                            if link:
                                notices.extend(link)

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

                        try:
                            approve_group_chatid = page["approve_group_chatid"]
                        except KeyError:
                            approve_group_chatid = None

                        if approve_group_chatid:
                            send_news_approve_message(context, notice_path, "data/avvisi/"+str(folder), folder, page_name, approve_group_chatid)
                        else:
                            spam_news(context, notice_path, page["channels"])
    except Exception as e:
        logging.exception("Exception on call scrape_notices({})".format(context))
        logging.exception(traceback.format_exc())



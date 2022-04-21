import ast
import logging
import os
import time
import traceback
import bs4
import requests

from module.config import load_configurations

config_map = load_configurations()


def get_links(label, url):
    logging.info("Call get_links(%s, %s)", label, url)

    try:
        response_received = False
        tries = 0
        max_tries = config_map["max_connection_tries"]

        while not response_received and tries < max_tries:
            try:
                req = requests.get(url)
                response_received = True
            except Exception as e:
                tries += 1
                logging.exception("Unhandled exception while connecting (%s), retrying in 5 seconds (%s/%s)", e, tries,
                                  max_tries)
                time.sleep(5)

        if not response_received:
            return None

        soup = bs4.BeautifulSoup(req.content, 'html.parser')

        result = soup.select("span.field-content a")

        if len(result) == 0:
            result = soup.select("strong.field-content a")

        return [link.get('href') for link in result if "/docenti/" not in link.get('href')]
    except Exception as e:
        # open("logs/errors.txt", "a+").write("{}\n".format(e))

        logging.exception("Exception on call get_links(%s, %s)", label, url)
        logging.exception(traceback.format_exc())

        return None


def get_content(url):
    logging.info("Call get_content(%s)", url)

    try:
        time.sleep(1)  # delay to avoid "Max retries exceeds" for too many requests

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
                table_content += "\n"

            table.decompose()  # remove table from content

        title = soup.find("h1", attrs={"class": "page-title"})
        content = soup.find("div", attrs={"class": "field-item even"})
        prof = soup.find("a", attrs={"class": "more-link"})

        if title is not None and content is not None:
            title = title.get_text()
            content = content.get_text()

            content.strip()  # trimming
            content += "\n"
            content += table_content

            if prof is not None:
                title = "[" + prof.get_text().replace("Vai alla scheda del prof. ", "") + "]\n" + title
        else:
            return None, None

        title = "\n" + title

        return title, content
    except Exception:
        logging.exception("Exception on call get_content(%s)", url)
        logging.exception(traceback.format_exc())

        return None, None


def pull_pending_notice(file_name):
    logging.info("Call pull_pending_notice(%s)", file_name)

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
    except Exception:
        logging.exception("Exception on call pull_pending_notice(%s)", file_name)
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
    except Exception:
        logging.exception("Exception on call format_content(%s)", content)
        logging.exception(traceback.format_exc())

        return None


def get_notice_content(notice_dict, base_url, archive_p, notice_p):
    # logging.info("Call get_notice_content({}, {}, {}, {})".format(notice_dict, base_url, archive_p, notice_p))

    try:
        label = list(notice_dict.keys())[0]

        post_url = notice_dict[label]
        if not post_url.startswith("/"):
            post_url = "/" + post_url

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
    except Exception:
        logging.exception("Exception on call get_notice_content(%s, %s, %s, %s)", notice_dict, base_url, archive_p,
                          notice_p)
        logging.exception(traceback.format_exc())

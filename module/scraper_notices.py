import logging
import time
import traceback
import bs4
import requests

from module.data import config_map

# TODO: add docstring and some type hints
def get_links(label, url: str) -> "list[str] | None":
    logging.info("Call get_links(%s, %s)", label, url)

    req = None
    tries = 0

    while req is None and tries < config_map["max_connection_tries"]:
        try:
            req = requests.get(url, timeout=10)
        except requests.Timeout as err:
            tries += 1
            logging.exception(
                "Unhandled exception while connecting (%s), retrying in 5 seconds (%s/%s)",
                err,
                tries,
                config_map["max_connection_tries"],
            )
            time.sleep(5)

    if req is None:
        return None

    try:
        soup = bs4.BeautifulSoup(req.content, "html.parser")

        result = soup.select("span.field-content a")

        if len(result) == 0:
            result = soup.select("strong.field-content a")

        links = []
        for link in result:
            if (new_link := link.get("href")) is not None:
                links.append(new_link)
        return links
    except bs4.FeatureNotFound:
        logging.exception("Exception on call get_links(%s, %s)", label, url)
        logging.exception(traceback.format_exc())
        return None


def get_content(url: str) -> "tuple[str, str] | tuple[None, None]":
    logging.info("Call get_content(%s)", url)

    try:
        time.sleep(1)  # delay to avoid "Max retries exceeds" for too many requests

        req = requests.get(url, timeout=10)
        soup = bs4.BeautifulSoup(req.content, "html.parser")

        table_content = ""
        table = soup.find("table")

        if table is not None:
            table_body = table.find("tbody")

            rows = table_body.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                table_content += "\t".join(cols) + "\n"

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
    except bs4.FeatureNotFound:
        logging.exception("Exception on call get_content(%s)", url)
        logging.exception(traceback.format_exc())

        return None, None


def format_content(content):
    max_len = config_map["max_messages_length"]

    if len(content) > max_len:
        split_index = max_len - 1

        while content[split_index] != " ":
            split_index = split_index - 1

        content = f"{content[:split_index]}{config_map['max_length_footer']}"

    return content

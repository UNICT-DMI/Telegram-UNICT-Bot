"""Notice class"""
import time
import logging
import traceback
import bs4
import requests
from telegram.ext import CallbackContext
from telegram.error import BadRequest, Unauthorized, TelegramError, RetryAfter
from module.data import config_map


class Notice:
    """Notice scraped from a page"""

    def __init__(self, label: str, title: str, content: str, url: str) -> None:
        self.label = label
        self.title = title
        self.content = content
        self.url = url

    def __repr__(self) -> str:
        return f"Notice({self.label}, {self.title}, {self.url})"

    @classmethod
    def from_url(cls, label: str, url: str) -> "Notice | None":
        """Generates a Notice object from the url of the notice.
        It uses the url to scrape the title and the content of the notice.

        Args:
            label: label used to identify the category of the notice
            url: url of the notice

        Returns:
            a new Notice object or None if the scraping fails
        """
        try:
            req = requests.get(url, timeout=10)
            soup = bs4.BeautifulSoup(req.content, "html.parser")

            table_content = ""
            table = soup.find("table")

            if isinstance(table, bs4.Tag):
                table_body = table.find("tbody")
                if isinstance(table_body, bs4.Tag):
                    rows: "list[bs4.Tag]" = table_body.find_all("tr")
                    for row in rows:
                        cols: "list[bs4.Tag]" = row.find_all("td")
                        cols_text = [ele.text.strip() for ele in cols]
                        table_content += "\t".join(cols_text) + "\n"
                    table.decompose()  # remove table from content

            title = soup.find("h1", attrs={"class": "page-title"})
            content = soup.find("div", attrs={"class": "field-item even"})
            prof = soup.find("a", attrs={"class": "more-link"})

            if title is not None and content is not None:
                title = title.get_text()
                content = content.get_text()

                content = f"{content.strip()}\n{table_content}"
                if prof is not None:
                    title = f"[{prof.get_text().replace('Vai alla scheda del prof. ', '')}]\n{title}"
            else:
                return None

            title = f"\n{title}"

            return cls(label, title, content, url)
        except (requests.Timeout, requests.ConnectionError, requests.ConnectTimeout, bs4.FeatureNotFound):
            logging.exception("Exception on call get_content(%s)", url)
            logging.exception(traceback.format_exc())

            return None

    @property
    def formatted_url(self) -> str:
        """Url formatted by removing the double slash"""
        return self.url.replace("it//", "it/")

    @property
    def formatted_message(self) -> str:
        """Properly formatted message to be sent to the user"""
        return f"<b>[{self.label}]</b>\n{self.url}\n<b>{self.title}</b>\n{self.formatted_content}"

    @property
    def formatted_content(self) -> str:
        """Formatted content with a set maximum length.
        If the content is longer than the maximum length, it is truncated
        and a footer is added to the end.
        """
        content = self.content
        max_len = config_map["max_messages_length"]

        # If message content is too long, cut it and add a footer
        if len(content) > max_len:
            split_index = max_len - 1

            while content[split_index] != " ":
                split_index = split_index - 1

            content = f"{content[:split_index]}{config_map['max_length_footer']}"

        return content

    def send(self, context: CallbackContext, chat_ids: "str | int | list[str | int]") -> None:
        """Try to send the notice to the given chat_id(s), retrying if necessary
        after a delay up to the maximum number of retries specified in the config.

        Args:
            context: context passed by the handler
            chat_ids: chat_id or list of chat_ids to send the message to
        """
        logging.info("Call send_notice(%s, %s, %s)", context, chat_ids, self)
        if not isinstance(chat_ids, list):
            chat_ids = [chat_ids]

        for chat_id in chat_ids:
            sent = False
            tries = 0

            while not sent and tries < config_map["max_connection_tries"]:
                try:
                    context.bot.sendMessage(
                        chat_id=chat_id, text=self.formatted_message, parse_mode="HTML"
                    )
                    sent = True
                    logging.info("Notice sent to %s", chat_id)
                except RetryAfter as err:
                    logging.warning("Retry after error encountered, retrying in 30 seconds")
                    time.sleep(err.retry_after)
                    tries += 1
                    continue
                except (BadRequest, Unauthorized, TelegramError):
                    sent = True  # avoid infinite loop
                    logging.exception("Exception on call enqueue_notice(%s)", context)
                    logging.exception(traceback.format_exc())

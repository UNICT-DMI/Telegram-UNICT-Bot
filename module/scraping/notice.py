"""Notice class"""
import logging
import traceback
import bs4
import requests
from module.data import config_map


class Notice:
    """Notice scraped from a page"""

    def __init__(self, label: str, title: str, content: str, url: str) -> None:
        self.label = label
        self.title = title
        self.content = content
        self.url = url

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

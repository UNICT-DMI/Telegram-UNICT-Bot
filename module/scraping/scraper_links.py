"""Notices scraper"""
import logging
import time
import traceback
import bs4
import requests
from module.data import config_map


def get_links(url: str) -> "list[str] | None":
    """Generates a list of links to the notices scraped from the page indicated by the url.

    Args:
        url: url from which to scrape the links

    Returns:
        list of links to the notices
    """
    logging.info("Call get_links(%s)", url)

    req = None
    tries = 0

    while req is None and tries < config_map["max_connection_tries"]:
        try:
            req = requests.get(url, timeout=10)
        except (requests.Timeout, requests.ConnectionError) as err:
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

        result = soup.select("span.field-content a") or \
            soup.select("strong.field-content a") or \
            soup.select("div.region.region-content div.view-content a:not(span a, p a)")

        links = [link.get("href") for link in result
                if link.get("href")
                and not link.get("href").endswith(".pdf")
                and not link.get("href").find("/docenti/")]

        return links
    except bs4.FeatureNotFound:
        logging.exception("Exception on call get_links(%s)", url)
        logging.exception(traceback.format_exc())
        return None

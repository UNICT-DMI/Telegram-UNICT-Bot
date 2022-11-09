"""Scrape groups"""
import logging
import os
import shutil
from typing import TypedDict
import yaml
from telegram.ext import CallbackContext
from module.data import GroupConfig
from .notice import Notice
from .scraper_links import get_links
from .send import send_notice


class NoticeData(TypedDict):
    """notice data type definition"""

    scraped_links: "list[str]"
    pending_notices: "list[str]"


def scrape_group(context: CallbackContext, group_key: str, group: GroupConfig) -> None:
    """Scrape notices for each group and page, and enqueue them for sending.

    Args:
        context: context passed by the job queue
        group_key: key identifier of the group
        group: configuration of the group
    """
    logging.info("- Group '%s'", group_key)

    # Loop over all the pages of the group
    for page_key, page in group["pages"].items():
        logging.info("-- Page '%s'", page_key)

        # Generate page folder's path and subpaths
        base_page_path = f"data/avvisi/{group_key.replace(' ', '_')}/{page_key.replace(' ', '_')}"
        data_file_path = f"{base_page_path}/notices_data.yaml"

        # Initialize folder and data file (if it doesn't exist)
        if not os.path.exists(data_file_path):
            os.makedirs(base_page_path, exist_ok=True)
            shutil.copyfile("dist/notices_data.yaml", data_file_path)

        # Read the data about past notices
        with open(data_file_path, "r", encoding="utf-8") as data_file:
            notices_data: NoticeData = yaml.safe_load(data_file)

        # Loop over all urls that need to be scraped
        for url in page["urls"]:
            logging.info("--- URL '%s'", url)

            links = get_links(group["base_url"] + url)

            if links is None:
                logging.warning("No links retrieved")
                continue

            for link in links:
                logging.info("---- Link '%s'", link)

                # If link has already been scraped
                # (implying that's invalid page or already posted notice), skip it
                if link in notices_data["scraped_links"]:
                    logging.info("Link is already present in the list")
                    continue

                notice = Notice.from_url(page["label"], group["base_url"] + link)

                # If the notice is valid,
                # enqueue it to be sent in the channel or in an approval group
                if notice is not None:
                    logging.info("Link is valid and seems to contain a notice, spamming")
                    for channel in page["channels"]:
                        send_notice(context, channel, notice)
                else:
                    logging.info("Link doesn't contain a valid notice")

                # Appends current link to scraped ones
                notices_data["scraped_links"].append(link)

        # Update notices data file
        with open(data_file_path, "w", encoding="utf-8") as data_file:
            yaml.safe_dump(notices_data, data_file)

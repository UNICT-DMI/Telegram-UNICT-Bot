"""Scraping job"""
import logging
from telegram.ext import CallbackContext
from module.data import config_map
from module.scraping import scrape_group


def update_notices_job(context: CallbackContext) -> None:
    """Called at a fixed interval to check for new notices.
    Loops over all the groups and pages, and checks for new notices
    by ensuring the links are not present in the `scraped links`.

    Args:
        context: context passed by the job queue
    """
    logging.info("Starting update tick (%s)", context)

    # Loop over all the notice groups
    for group_key, group in config_map["notices_groups"].items():
        scrape_group(context, group_key, group)
    logging.info("Update notices finished")

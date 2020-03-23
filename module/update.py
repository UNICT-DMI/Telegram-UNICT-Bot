import logging
import traceback
import yaml
import os

from module.post import enqueue_notice
from module.scraper_notices import *

def update_tick(context):
    logging.info ("Call update_tick ({})".format(context))

    logging.info("Starting update tick")

    try:
        # Load URLs from configuration
        config_map = yaml.safe_load(open("config/settings.yaml", "r"))
        groups = config_map["notices_groups"]

        for group_key in groups:
            logging.info("- Group '{}'".format(group_key))

            # Load group's data
            group = groups[group_key]

            approval_group_chatid = None
            if "approval_group_chatid" in group.keys():
                approval_group_chatid = group["approval_group_chatid"]

            group_folder = group_key.replace(" ", "_")

            for page_key in group["pages"]:
                logging.info("-- Page '{}'".format(page_key))

                # Load page's data
                page = group["pages"][page_key]

                # Generate page folder's path and subpaths
                page_folder = page_key.replace(" ", "_")

                base_page_path = "data/avvisi/{}/{}".format(group_folder, page_folder)
                data_file_path = base_page_path + "/notices_data.yaml"

                # Initialize folder and data file (if it doesn't exist)
                if not os.path.exists(data_file_path):
                    os.makedirs(base_page_path)
                    yaml.safe_dump(yaml.safe_load(open("dist/notices_data.yaml", "r")), open(data_file_path, "w"))

                notices_data = yaml.safe_load(open(data_file_path, "r"))

                for url in page["urls"]:
                    logging.info("--- URL '{}'".format(url))

                    page_url = group["base_url"] + url

                    links = get_links(page_key, page_url)

                    for link in links:
                        logging.info("--- Link '{}'".format(link))

                        # If link has already been scraped (implying that's invalid page or already posted notice), skip it
                        if link in notices_data["scraped_links"]:
                            continue

                        full_url = group["base_url"] + link 

                        link_content = get_content(full_url)

                        # Check if link's content is valid
                        if all(link_content):
                            logging.info("Link is valid and seems to contain a notice, spamming")

                            # Enqueue the notice to be sent in the channel or in an approval group
                            enqueue_notice(context, page, notices_data, full_url, link_content, approval_group_chatid)
                        else:
                            logging.info("Link doesn't contain a valid notice")

                        # Appends current link to scraped ones
                        notices_data["scraped_links"].append(link)

                # Update notices data file
                yaml.safe_dump(notices_data, open(data_file_path, "w"))

    except Exception as e:
        logging.exception("Exception on call update_tick({})".format(context))
        logging.exception(traceback.format_exc())

    logging.info("Update tick finished")


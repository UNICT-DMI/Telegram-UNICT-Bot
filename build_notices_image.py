import yaml, logging, traceback, bs4, os

from module.images_builder.department_scraper import DepartmentScraper
from module.images_builder.threading import DepartmentScraperThread

def load_notices_urls():
    config_map = yaml.safe_load(open('config/settings.yaml', 'r'))
    return config_map["notices_urls"]

def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename="logs.txt"
    )

    logger = logging.getLogger(__name__)

    notices_urls = load_notices_urls()

    scrapers = []

    for department_key in notices_urls:
        logger.info("Creating scraper for departiment '{}'".format(department_key))

        scraper = DepartmentScraper(department_key, notices_urls[department_key])
        scraper_thread = DepartmentScraperThread(scraper)

        scrapers.append(scraper_thread)

    for scraper in scrapers:
        scraper.start()

        # return # TODO: Remove to cycle all departments

    for scraper in scrapers:
        scraper.join()

if __name__ == "__main__":
    main()
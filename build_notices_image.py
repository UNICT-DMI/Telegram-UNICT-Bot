import yaml, logging, traceback, bs4, os, argparse

from concurrent.futures import ThreadPoolExecutor

from module.images_builder.department_scraper import DepartmentScraper
from module.images_builder.threading import DepartmentScraperThread

def load_notices_urls():
    config_map = yaml.safe_load(open('config/settings.yaml', 'r'))
    return config_map["notices_urls"]

def main():
    parser = argparse.ArgumentParser(description='UNICT-Bot notices images builder')
    parser.add_argument('workers', type=int)
    parser.add_argument('--logfile', nargs='+', help="Path to the file to print logs in")
    parser.add_argument('--scrape-only', nargs='+', help="Scrape only given departments")
    parser.add_argument('--exclude', nargs='+', help="Skip given departments while scraping")

    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        filename=args.logfile#"logs.txt"
    )

    logger = logging.getLogger(__name__)

    notices_urls = load_notices_urls()

    executor = ThreadPoolExecutor(max_workers = args.workers)

    scrapers = []
    futures = []

    for department_key in notices_urls:
        if args.scrape_only and department_key not in args.scrape_only:
            continue

        if args.exclude and department_key in args.exclude:
            continue

        logger.info("Creating scraper for departiment '{}'".format(department_key))

        scraper = DepartmentScraper(department_key, notices_urls[department_key])
        # scraper_thread = DepartmentScraperThread(scraper)

        # scrapers.append(scraper_thread)
        scrapers.append(scraper)

    for scraper in scrapers:
        future = executor.submit(scraper.run)

        futures.append(future)

    for future in futures:
        future.result()

        # No result is expected (right now)

if __name__ == "__main__":
    main()
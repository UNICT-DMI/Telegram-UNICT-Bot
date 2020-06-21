import logging, bs4, traceback, os

from module.scraper_notices import request_page_content, get_links

class DepartmentScraper():
    def __init__(self, department_key, department_data):
        self.department_key = department_key
        self.department_data = department_data

        self.logger = logging.getLogger("'{}' department scraper".format(department_key))

    def scrape_links_from_page(self, file_writer, page_id, page_url):
        page_content = request_page_content(page_url)
        links = get_links(page_id, page_content)

        # self.logger.info(links)

        for link in links:
            file_writer.write("{}\n".format(str(link)))

    def scrape_archive_pages(self, file_writer, page_id, page_url, max_archive_page_index):
        archive_page_index = 1

        while archive_page_index <= max_archive_page_index:
            archive_page_url = "{}/archivio?page={}".format(page_url, archive_page_index)

            self.logger.info("Scraping archive's page {}...".format(archive_page_url))

            self.scrape_links_from_page(file_writer, page_id, archive_page_url)

            archive_page_index += 1

    def scrape_single_page(self, file_writer, page_id, page_url):
        self.logger.info("Scraping single page {}...".format(page_url))

        self.scrape_links_from_page(file_writer, page_id, page_url)

    def get_last_page_in_archive(self, page_url):
        try:
            first_page_content = request_page_content("{}/archivio".format(page_url))
            soup = bs4.BeautifulSoup(first_page_content, 'html.parser')

            result = soup.find("a", {"title": "Vai all'ultima pagina"})

            return int(result['href'].split("=")[-1])
        except:
            self.logger.warning("Couldn't scrape last page, assuming there's no archive and only a single page is present")

            # traceback.print_exc()

            return 0

    def run(self):
        self.logger.info("Building a complete image for department '{}'...".format(self.department_key))

        department_root_folder = "images/{}".format(self.department_key)

        try:
            os.mkdir(department_root_folder)
        except FileExistsError:
            self.logger.warning("Department's folder exists, resulting images may be dirty and/or invalid.")

        for page_id, page_data in self.department_data["pages"].items():
            self.logger.info("Scraping page '{}'...".format(page_id))

            image_file_path = "{}/{}_avvisi.dat".format(department_root_folder, page_id)

            if os.path.exists(image_file_path):
                self.logger.info("Image file exists already, skipping")
                continue

            file_writer = open(image_file_path, 'w')

            for page_url in page_data["urls"]:
                max_archive_page_index = self.get_last_page_in_archive(page_url)

                self.logger.info("Last page: {}".format(max_archive_page_index))

                try:
                    if max_archive_page_index > 0:
                        self.scrape_archive_pages(file_writer, page_id, page_url, max_archive_page_index)
                    else:
                        self.scrape_single_page(file_writer, page_id, page_url)
                except:
                    self.logger.warning("Unhandled exception while scraping")
                    traceback.print_exc()

                    return

            file_writer.close()
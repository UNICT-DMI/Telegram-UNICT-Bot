import requests, logging, bs4, traceback, os, time

from module.scraper_notices import request_page_content, get_links

class DepartmentScraper():
    def __init__(self, department_key, department_data):
        self.__department_key = department_key
        self.__department_data = department_data

        self.__logger = logging.getLogger("'{}' department scraper".format(self.__department_key))

    def __str__(self):
        return "Department '{}' scraper".format(self.__department_key)

    def __repr__(self):
        return self.__str__()

    def __scrape_links_from_page(self, file_writer, page_id, page_url, exception_sleep=5):
        while True:
            try:
                page_content = request_page_content(page_url)
                break
            except requests.exceptions.ConnectionError:
                logging.warn("Connection error while requesting page content, sleeping and retrying...")

                traceback.print_exc()

                time.sleep(exception_sleep)

        links = get_links(page_id, page_content)

        # self.logger.info(links)

        for link in links:
            file_writer.write("{}\n".format(str(link)))

    def __scrape_archive_pages(self, file_writer, page_id, page_url, max_archive_page_index):
        archive_page_index = 1

        while archive_page_index <= max_archive_page_index:
            archive_page_url = "{}/archivio?page={}".format(page_url, archive_page_index)

            self.__logger.info("Scraping archive's page {}...".format(archive_page_url))

            self.__scrape_links_from_page(file_writer, page_id, archive_page_url)

            archive_page_index += 1

    def __scrape_single_page(self, file_writer, page_id, page_url):
        self.__logger.info("Scraping single page {}...".format(page_url))

        self.__scrape_links_from_page(file_writer, page_id, page_url)

    def __get_last_page_in_archive(self, page_url):
        try:
            first_page_content = request_page_content("{}/archivio".format(page_url))
            soup = bs4.BeautifulSoup(first_page_content, 'html.parser')

            result = soup.find("a", {"title": "Vai all'ultima pagina"})

            return int(result['href'].split("=")[-1])
        except:
            self.__logger.warning("Couldn't scrape last page, assuming there's no archive and only a single page is present")

            # traceback.print_exc()

            return 0

    def __escape_filename_chars(self, filename):
        filename = filename.replace("/", " ")

        return filename

    def run(self, destination_folder):
        self.__logger.info("Building a complete image for department '{}'...".format(self.__department_key))

        department_root_folder = "{}/{}".format(destination_folder, self.__escape_filename_chars(self.__department_key))

        try:
            os.mkdir(department_root_folder)
        except FileExistsError:
            self.__logger.warning("Department's folder exists, resulting images may be dirty and/or invalid.")

        for page_id, page_data in self.__department_data["pages"].items():
            self.__logger.info("Scraping page '{}'...".format(page_id))

            image_file_path = "{}/{}_avvisi.dat".format(
                department_root_folder,
                self.__escape_filename_chars(page_id)
            )

            if os.path.exists(image_file_path):
                self.__logger.info("Image file exists already, skipping")
                continue

            file_writer = open(image_file_path, 'w')

            for page_url in page_data["urls"]:
                max_archive_page_index = self.__get_last_page_in_archive(page_url)

                self.__logger.info("Last page: {}".format(max_archive_page_index))

                try:
                    if max_archive_page_index > 0:
                        self.__scrape_archive_pages(file_writer, page_id, page_url, max_archive_page_index)
                    else:
                        self.__scrape_single_page(file_writer, page_id, page_url)
                except:
                    self.__logger.warning("Unhandled exception while scraping")
                    traceback.print_exc()

                    return

            file_writer.close()
from threading import Thread

from .department_scraper import DepartmentScraper

class DepartmentScraperThread(Thread):
    def __init__(self, scraper):
        Thread.__init__(self)

        self.scraper = scraper

    def run(self):
        self.scraper.run()
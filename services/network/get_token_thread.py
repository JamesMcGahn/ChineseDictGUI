from PySide6.QtCore import QThread, Signal, Slot

from core.scrapers.cpod.lessons.web_scrape import WebScrape
from keys import keys
from services.network import SessionManager


class GetTokenThread(QThread):
    send_token = Signal(str, bool)

    def __init__(self):
        super().__init__()
        self.token = None

    @Slot()
    def run(self):
        print("Starting Lesson Scraper Thread")

        sess = SessionManager()
        print("set up session")

        try:
            self.wb = WebScrape(sess, keys["url"])
            print("finished setting up webscrape")
            self.wb.init_driver()
            print("initting driver")

            self.wb.find_bearer()
            token = self.wb.get_bearer()
            self.wb.close()

        except RuntimeError:
            self.token = None
        finally:
            self.send_token.emit(token, True if token else False)

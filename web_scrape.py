from time import sleep

from keys import keys
from logger import Logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class WebScrape:
    def __init__(self, session):
        self.session = session
        self.cookies = session.get_cookies()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.not_available = []
        self.source = None

    def get_source(self):
        return {"source": self.source, "not_available": self.not_available}

    def close(self):
        self.driver.close()

    def init_driver(self):
        cookies = self.cookies
        url = self.session.get_session_url()
        sleep(3)
        try:
            self.driver.get(url)
            for c in cookies:

                if c.domain not in keys["mdomain"]:
                    self.driver.add_cookie(
                        {
                            "name": c.name,
                            "value": c.value,
                            "domain": c.domain,
                            "path": c.path,
                        }
                    )

        except Exception as e:
            Logger().insert("Failed loading cookies", "ERROR")
            Logger().insert(e, "ERROR", False)

    def run_webdriver(self, url):
        try:
            Logger().insert(f"Starting Scrape......{url}", "INFO")
            self.not_available = []
            self.driver.get(url)
            sleep(3)
            for link in ("Dialogue", "Vocabulary", "Expansion", "Grammar"):
                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR, f"a[title='{link}']"
                    ).click()
                    sleep(3)
                except NoSuchElementException:
                    self.not_available.append(link)
                    Logger().insert(f"Lesson doesn't have a {link} section", "WARN")

            page_source = self.driver.page_source
            Logger().insert("Completed Scrape .....", "INFO")
            self.source = page_source
        except Exception as e:
            Logger().insert("Something Went Wrong...", "ERROR")
            Logger().insert(e, "ERROR", False)
            raise RuntimeError("An error has occurred")

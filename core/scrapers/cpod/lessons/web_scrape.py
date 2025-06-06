from time import sleep

from PySide6.QtCore import QMutexLocker, QObject, Signal
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from keys import keys
from services import Logger


class WebScrape:

    def __init__(self, session, url):
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")
        self.session = session
        self.cookies = session.get_cookies()
        self.driver = webdriver.Chrome(
            options=chrome_options, service=Service(ChromeDriverManager().install())
        )
        self.not_available = []
        self.source = None
        self.url = url

    def get_source(self):
        return {"source": self.source, "not_available": self.not_available}

    def close(self):
        self.driver.close()

    def init_driver(self):
        cookies = self.cookies

        sleep(3)
        try:
            self.driver.get(self.url)
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

            menu_list = self.driver.find_element(
                By.CSS_SELECTOR, "div.cpod-card-top ul.lesson-menu-tabs"
            )
            tabs = menu_list.find_elements(By.TAG_NAME, "a")
            tabs_titles = [tab.get_attribute("title") for tab in tabs]
            print(tabs_titles)
            tab_titles = [
                tab
                for tab in tabs_titles
                if tab in ("Dialogue", "Vocabulary", "Expansion", "Grammar")
            ]

            self.not_available = [
                na
                for na in ("Dialogue", "Vocabulary", "Expansion", "Grammar")
                if na not in tab_titles
            ]
            print("not available", self.not_available)

            def wait_for_content(content):
                ids = {
                    "Dialogue": "dialogue",
                    "Vocabulary": "lesson-vocabulary",
                    "Expansion": "expansion",
                    "Grammar": "lesson-grammar",
                }

                target_id = ids.get(content)
                if not target_id:
                    return
                WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located((By.ID, target_id))
                )

                WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"#{target_id} *"))
                )

                if target_id == "lesson-vocabulary":
                    WebDriverWait(self.driver, 40).until(
                        EC.presence_of_element_located((By.ID, "key_vocab"))
                    )

            for link in tab_titles:
                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR, f"a[title='{link}']"
                    ).click()
                    sleep(2)
                    wait_for_content(link)
                    sleep(5)
                except NoSuchElementException as e:
                    print(e)
                    self.not_available.append(link)
                    Logger().insert(f"Lesson doesn't have a {link} section", "WARN")

            page_source = self.driver.page_source
            Logger().insert("Completed Scrape .....", "INFO")
            self.source = page_source
        except Exception as e:
            Logger().insert("Something Went Wrong...", "ERROR")
            Logger().insert(e, "ERROR", False)
            print(e)

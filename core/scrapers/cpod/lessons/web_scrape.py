import json
import time
from time import sleep

from PySide6.QtCore import QMutexLocker, QObject, Signal
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from keys import keys
from services import Logger


class WebScrape:

    def __init__(self, session, url):

        caps = DesiredCapabilities.CHROME.copy()
        caps["goog:loggingPrefs"] = {"performance": "ALL"}

        self.chrome_options = Options()
        # chrome_options.add_argument("--headless=new")
        self.chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        self.session = session
        self.cookies = session.get_cookies()
        self.driver = webdriver.Chrome(
            options=self.chrome_options,
            service=Service(ChromeDriverManager().install()),
        )
        self.not_available = []
        self.source = None
        self.url = url
        self.bearer = None

    def get_source(self):
        return self.source

    def get_not_available(self):
        return self.not_available

    def get_bearer(self):
        return self.bearer

    def close(self):
        self.driver.close()

    def capture_page_source(self):
        self.source = self.driver.page_source

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

    def run_section(self, url, section):
        if section not in ("Dialogue", "Vocabulary", "Expansion", "Grammar"):
            return
        self.driver.get(url)
        sleep(3)
        self.get_section_content(section)
        self.page_source = self.driver.page_source

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

            for link in tab_titles:
                self.get_section_content(link)

            page_source = self.driver.page_source
            Logger().insert("Completed Scrape .....", "INFO")
            self.source = page_source
        except Exception as e:
            Logger().insert("Something Went Wrong...", "ERROR")
            Logger().insert(e, "ERROR", False)
            print(e)

    def get_section_content(self, link):
        try:
            self.driver.find_element(By.CSS_SELECTOR, f"a[title='{link}']").click()
            sleep(6)
            self.wait_for_content(link)
            sleep(5)
        except NoSuchElementException as e:
            print(e)
            self.not_available.append(link)
            Logger().insert(f"Lesson doesn't have a {link} section", "WARN")

    def wait_for_content(self, content):
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
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        sleep(5)

        self.driver.execute_script("window.scrollTo(0, 0);")

    def go_and_wait_for_id(self, url, id):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.ID, id))
            )
            return True
        except TimeoutException:
            Logger().insert(f"Cant find {id} on {url}", "ERROR")
            return False

    def find_bearer(self):
        try:
            url = keys["url"]
            self.driver.get(f"{url}home")
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'input[placeholder="Email"]')
                    )
                )

                login_name_field = self.driver.find_element(
                    By.CSS_SELECTOR, 'input[placeholder="Email"]'
                )
                login_name_field.send_keys(keys["email"])

                login_pw_field = self.driver.find_element(
                    By.CSS_SELECTOR, 'input[placeholder="Password"]'
                )
                login_pw_field.send_keys(keys["password"])

                login_btn = self.driver.find_element(By.CLASS_NAME, "btn-primary")
                # login_btn = self.driver.find_element(By.CLASS_NAME, "ajax-button")
                sleep(1)
                login_btn.click()
                time.sleep(5)
                cookies = self.driver.get_cookies()
                print(cookies)
                if cookies:
                    self.session.set_cookies(self.session.convert_cookies(cookies))
                    self.session.save_session()
            except TimeoutException:
                self.driver.get(f"{url}profile")
                time.sleep(5)
            finally:

                logs = self.driver.get_log("performance")

                for entry in logs:
                    message = json.loads(entry["message"])["message"]
                    if (
                        message["method"] == "Network.requestWillBeSent"
                        and "headers" in message["params"]["request"]
                    ):
                        headers = message["params"]["request"]["headers"]
                        auth = headers.get("Authorization")
                        if auth:
                            print("Bearer token:", auth)
                            self.bearer = auth

                if not self.bearer:
                    Logger().insert("Bearer token not found in browser logs.", "ERROR")
                    raise RuntimeError("Bearer token not found in browser logs.")

        except Exception as e:
            print("Unable to get Bearer Token", e)

    def find_lesson_id(self, url):
        try:
            self.driver.get(url)

            lesson_id = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//span[starts-with(text(), "ID:")]')
                )
            )
            lesson_id = lesson_id.text.replace("ID: ", "")
            lesson_id = lesson_id.strip()

            return lesson_id
        except Exception as e:
            Logger().insert(f"Error getting lesson id {e}", "ERROR")
            return None

    def check_complete_lesson(self):
        try:
            header = self.driver.find_element(By.CLASS_NAME, "header-body")
            buttons = header.find_elements(By.TAG_NAME, "button")
            if len(buttons) == 2:
                complete_button = buttons[1]
                complete_button.click()
            Logger().insert("Lesson Successfully Marked as Complete!", "INFO")
        except Exception as e:
            Logger().insert(f"Error Checking Lesson Complete {e}", "ERROR")

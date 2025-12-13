import json
import os
import shutil
import time
from time import sleep
from urllib.parse import urlparse

from PySide6.QtCore import QMutexLocker, QObject, Signal
from selenium import webdriver
from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from keys import keys
from services import Logger
from services.network import SessionManager
from utils.files import PathManager


class WebScrape:

    def __init__(self, url):

        caps = DesiredCapabilities.CHROME.copy()
        caps["goog:loggingPrefs"] = {"performance": "ALL"}

        self.chrome_options = Options()
        # chrome_options.add_argument("--headless=new")
        self.chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        self.session = SessionManager()

        self.driver = webdriver.Chrome(
            options=self.chrome_options,
            service=self.get_local_driver_service(),
        )
        self.not_available = []
        self.source = None
        self.url = url
        self.bearer = None
        self.cookies = self.filter_cookies_for_url(
            url, self.session.jar_to_selenium_list()
        )

    def get_local_driver_service(self):
        driver_path = ChromeDriverManager().install()
        driver_dir = PathManager.create_folder_in_app_data("driver_cache")
        local_driver_path = os.path.join(driver_dir, "chromedriver")
        shutil.copy(driver_path, local_driver_path)
        try:
            os.chmod(driver_path, 0o755)
        except Exception:
            pass

        return Service(local_driver_path)

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

    def filter_cookies_for_url(self, url: str, cookies: list) -> list:

        parsed = urlparse(url.strip())
        if not parsed.hostname:
            parsed = urlparse("https://" + url.strip())

        host = parsed.hostname or ""
        base_host = host.removeprefix("www.")
        valid_cookies = []
        for c in cookies:
            cookie_domain = c.get("domain") or ""
            cookie_domain = cookie_domain.removeprefix(".")
            cookie_domain = cookie_domain.removeprefix("www.")
            if cookie_domain == base_host or base_host.endswith(cookie_domain):
                valid_cookies.append(c)

        return valid_cookies

    def init_driver(self):
        cookies = self.cookies

        sleep(3)
        try:
            self.driver.get(self.url)
            print("cookies", cookies)

            for c in cookies:

                # skip HttpOnly cookies
                if c.get("httpOnly"):
                    continue

                try:
                    self.driver.add_cookie(
                        {
                            "name": c["name"],
                            "value": c["value"],
                            "domain": c.get("domain"),
                            "path": c.get("path", "/"),
                        }
                    )
                except Exception as ce:
                    print("Failed to add cookie:", c, ce)
                    continue
        except Exception as e:
            Logger().insert("Failed loading cookies", "ERROR")
            Logger().insert(e, "ERROR", False)

    def is_driver_alive(self) -> bool:
        try:
            if not getattr(self.driver, "session_id", None):
                return False
            self.driver.execute_script("return 1")
            _ = self.driver.title
            return True
        except (InvalidSessionIdException, WebDriverException):
            return False

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
                    self.session.update_cookie_jar(
                        self.session.convert_cookies(cookies)
                    )
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
            Logger().insert(f"Error getting lesson ID: {e}", "ERROR")
            return None

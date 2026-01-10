import os

from playwright.sync_api import sync_playwright
from PySide6.QtCore import Signal

from .qobject_base import QObjectBase


class PlaywrightBase(QObjectBase):
    finished = Signal()
    error = Signal(str)

    def __init__(self):
        super().__init__()
        from utils.files import PathManager

        app_data_playwright_path = PathManager.create_folder_in_app_data("playwright")
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = app_data_playwright_path
        self.browser = None
        self.context = None

    def run(self):

        try:

            with sync_playwright() as p:
                self.logging("PLAYWRIGHT: launching browser...")
                self.browser = p.chromium.launch(headless=False)
                self.logging("PLAYWRIGHT: browser launched")

                # context = browser.new_context(storage_state="auth.json")
                self.context = self.browser.new_context()
                page = self.context.new_page()
                self.do_work(page)
                self.close()

        except Exception as e:
            print(e)
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def do_work(self, page):
        raise NotImplementedError

    def close(self):
        self.logging("Playwright - Closing")
        self.context.close()
        self.browser.close()

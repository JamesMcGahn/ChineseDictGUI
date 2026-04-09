from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.network.session import BaseProviderSession


import os

from playwright.sync_api import sync_playwright
from PySide6.QtCore import Signal

from .qobject_base import QObjectBase


class PlaywrightBase(QObjectBase):
    done = Signal()
    error = Signal(str)

    def __init__(self, session: BaseProviderSession):
        super().__init__()
        self.provider_session = session
        from utils.files import PathManager

        app_data_playwright_path = PathManager.create_folder_in_app_data("playwright")
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = app_data_playwright_path
        self.browser = None

    def run(self):

        try:
            with sync_playwright() as p:
                self.logging("launching browser...")
                self.browser = p.chromium.launch(headless=False)
                self.logging("browser launched")

                self.context = self.browser.new_context()
                cookies = self.provider_session.convert_jar_to_cookie_list()
                self.context.add_cookies(cookies)
                page = self.context.new_page()
                self.do_work(page)
                cookies = self.context.cookies()
                self.provider_session.update_cookies_from_list(cookies)
                if self.should_auto_close():
                    self.close()

        except Exception as e:
            self.on_error(e)
        finally:
            self.done.emit()

    def do_work(self, page):
        raise NotImplementedError

    def should_auto_close(self):
        return True

    def on_error(self, e):
        self.logging(f"Playwright - {e}", "ERROR")
        self.error.emit(str(e))

    def close(self):
        self.logging("Playwright - Closing")
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()

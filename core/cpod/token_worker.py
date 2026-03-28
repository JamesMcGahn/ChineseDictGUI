from typing import override

from playwright.sync_api import TimeoutError as PWTimeoutError
from PySide6.QtCore import Signal

from base.play_wright import PlaywrightBase
from keys import keys


class TokenWorker(PlaywrightBase):
    send_cookies = Signal(list)
    send_token = Signal(str, bool)

    def __init__(self):
        super().__init__()
        self.bearer = None

    def do_work(self, page):
        self.logging("TokenWorker: Going to https://www.chinesepod.com/")
        page.goto("https://www.chinesepod.com/", wait_until="domcontentloaded")
        self.logging("TokenWorker: Going to https://www.chinesepod.com/home")
        page.goto("https://www.chinesepod.com/home", wait_until="domcontentloaded")

        self.logging("TokenWorker: Waiting for Login Form")
        page.wait_for_timeout(1_000)

        email = page.locator('input[placeholder="Email"]')
        password = page.locator('input[placeholder="Password"]')
        for locator, value in ((email, keys["email"]), (password, keys["password"])):
            filled = False
            for fill_attempt in range(3):
                try:
                    locator.wait_for(state="visible", timeout=10_000)
                    locator.click(timeout=5_000)
                    locator.fill(value, timeout=5_000)
                    filled = True
                    break
                except PWTimeoutError:
                    self.logging(
                        f"TokenWorker: Failed login form fill attempt {fill_attempt +1}"
                    )
                    page.wait_for_timeout(3_000)
            if not filled:
                self.logging("TokenWorker: Failed fill in login form", "ERROR")
                self.send_token.emit(self.bearer, False)
                return
        self.logging("TokenWorker: Login form visible and filled In.")
        try:
            self.logging("TokenWorker: Trying to Log In...")
            submit_btn = page.locator(".btn-primary")
            submit_btn.wait_for(state="visible", timeout=10_000)
            submit_btn.click(timeout=5_000)
        except PWTimeoutError:
            self.logging("TokenWorker: Failed to log in.", "ERROR")
            self.send_token.emit(self.bearer, False)
            return

        try:
            with page.expect_request(
                lambda r: "authorization" in r.headers, timeout=60_000
            ) as req_info:
                self.logging("TokenWorker: Going to Cpod profile page for token.")
                page.goto(
                    "https://www.chinesepod.com/profile", wait_until="domcontentloaded"
                )
                self.logging("TokenWorker: Profile page loaded.")
                self.logging("TokenWorker: Waiting for network calls to idle")
                page.wait_for_load_state("networkidle", timeout=60_000)
        except PWTimeoutError:
            self.logging("TokenWorker: Failed find Token.", "ERROR")
            self.send_token.emit(self.bearer, False)
            return

        if req_info is not None:
            req = req_info.value
            self.bearer = req.headers.get("authorization")

        if self.bearer is not None:
            self.logging("TokenWorker: Found token on profile page.")
            cookies = page.context.cookies()
            self.send_token.emit(self.bearer, True)
            self.send_cookies.emit(cookies)
        else:
            self.logging("TokenWorker: Failed find Token.", "ERROR")
            self.send_token.emit(self.bearer, False)

    @override
    def on_error(self, e):
        self.logging(f"TokenWorker: {e}", "ERROR")
        self.send_token.emit(self.bearer, False)
        self.error.emit(str(e))

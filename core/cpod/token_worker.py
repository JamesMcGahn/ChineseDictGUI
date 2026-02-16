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

        page.goto(keys["url"])
        page.wait_for_timeout(1_000)
        page.goto(f"{keys["url"]}home")
        page.wait_for_timeout(1_000)
        if page.locator('input[placeholder="Email"]').is_visible():
            page.fill('input[placeholder="Email"]', keys["email"])
            page.fill('input[placeholder="Password"]', keys["password"])
            page.click(".btn-primary")
            page.wait_for_timeout(3_000)

        with page.expect_request(
            lambda r: "authorization" in r.headers, timeout=30_000
        ) as req_info:
            page.goto(f"{keys["url"]}profile")

        if req_info is not None:
            req = req_info.value
            self.bearer = req.headers["authorization"]

        if self.bearer is not None:

            cookies = page.context.cookies()
            self.send_token.emit(self.bearer, True)
            self.send_cookies.emit(cookies)

            print(self.bearer)
        else:
            self.send_token.emit(self.bearer, False)

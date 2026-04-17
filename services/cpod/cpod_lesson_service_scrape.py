from typing import override

from PySide6.QtCore import Signal

from base.enums import JOBSTATUS, LESSONTASK
from base.play_wright import PlaywrightBase
from models.services import (
    CPodLessonPayload,
    JobRef,
    JobRequest,
    JobResponse,
)
from services.network.session import BaseProviderSession


class CpodLessonServiceScrape(PlaywrightBase):
    send_cookies = Signal(list)
    send_token = Signal(str, bool)
    task_complete = Signal(object)

    def __init__(
        self,
        job: JobRequest[CPodLessonPayload],
        session: BaseProviderSession,
    ):
        super().__init__(session=session)
        self.bearer = None
        self.job = job
        self.session = session
        self.handlers: dict[LESSONTASK, callable] = {
            LESSONTASK.INFO: self.get_info,
            LESSONTASK.EXPANSION: self.get_expansion,
            LESSONTASK.VOCAB: self.get_vocab,
            LESSONTASK.GRAMMAR: self.get_grammar,
            LESSONTASK.CHECK: self.get_check,
        }

    def do_work(self, page):
        if not self.job.payload.slug:
            self.on_error("Job does not have lesson slug.")
        self.logging(f"Going to https://www.chinesepod.com/{self.job.payload.slug}")
        self.get_handler(page, self.job.task)

    def get_handler(self, page, task: LESSONTASK):
        handler = self.handlers.get(task)
        if not handler:
            self.on_error()
        handler(page)

    def get_info(self, page):
        page.goto(
            f"https://chinesepod.com/lessons/{self.job.payload.slug}",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        info_card = page.locator("#panelLessonReviewDownloads")
        info_card.wait_for(state="attached", timeout=30_000)
        data = page.content()
        self.on_success(data)

    def get_dialogue(self, page):
        self.logging(f"Lesson - {self.job.payload.slug} - Getting Dialogue")
        page.goto(
            f"https://www.chinesepod.com/lessons/{self.job.payload.slug}#dialogue-tab",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        dialogue_tab = page.locator("#dialogue-tab")
        if self.page_has_tab(page, "#dialogue-tab"):
            dialogue_tab.click()
            data = page.content()
            self.on_success(data)
        else:
            self.on_error("Page does not have Dialogue")

    def get_expansion(self, page):
        self.logging(f"Lesson - {self.job.payload.slug} - Getting Expansion")
        page.goto(
            f"https://www.chinesepod.com/lessons/{self.job.payload.slug}#expansion-tab",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        expansion = page.locator("#expansion-tab")
        if self.page_has_tab(page, "#expansion-tab"):
            expansion.click()
            data = page.content()
            self.on_success(data)

    def get_vocab(self, page):
        self.logging(f"Lesson - {self.job.payload.slug} - Getting Vocab")
        page.goto(
            f"https://www.chinesepod.com/lessons/{self.job.payload.slug}#vocabulary-tab",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        vocab_card = page.locator("#vocabulary-tab")
        if self.page_has_tab(page, "#vocabulary-tab"):
            vocab_card.click()
            data = page.content()
            self.on_success(data)
        else:
            self.on_error("Page does not have Vocab")

    def get_grammar(self, page):
        self.logging(f"Lesson - {self.job.payload.slug} - Getting Grammar")
        page.goto(
            f"https://www.chinesepod.com/lessons/{self.job.payload.slug}",
            wait_until="domcontentloaded",
            timeout=60_000,
        )

        info_card = page.locator("#panelLessonReviewDownloads")
        info_card.wait_for(state="attached", timeout=30_000)

        grammar_link = page.locator("#panelLessonReviewDownloads a:has-text('Grammar')")

        if grammar_link.count() > 0:
            href = grammar_link.first.get_attribute("href")
            page.goto(href)
            data = page.content()
            self.on_success(data)
        else:
            self.on_error("Page does not have Grammar")

    def get_check(self, page):
        self.logging(f"Lesson - {self.job.payload.slug} - Checking Lesson")
        page.goto(
            f"https://www.chinesepod.com/lessons/{self.job.payload.slug}",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        studied_span = page.locator("#studiedBtn")
        studied_span.wait_for(state="attached", timeout=10_000)
        if not studied_span.is_visible():
            self.logging("Lesson already marked studied")
            self.on_success(None)
        else:
            button = studied_span.locator("button")
            button.wait_for(state="visible", timeout=10_000)
            self.on_success(None)

    def page_has_tab(self, page, tab_name: str) -> bool:
        tab = page.locator(
            f"div.cpod-card-top ul.lesson-menu-tabs a[href='{tab_name}']"
        )
        if tab:
            tab.click()
        return tab.count() > 0

    @override
    def on_error(self, e):
        msg = f" {e}"
        self.logging(msg, "ERROR")

        self.task_complete.emit(
            JobResponse(
                job_ref=JobRef(
                    id=self.job.id,
                    task=self.job.task,
                    status=(JOBSTATUS.ERROR),
                    error=msg,
                ),
                payload=None,
            )
        )

    def on_success(self, data):
        self.task_complete.emit(
            JobResponse(
                job_ref=JobRef(
                    id=self.job.id,
                    task=self.job.task,
                    status=(JOBSTATUS.COMPLETE),
                ),
                payload=data,
            )
        )

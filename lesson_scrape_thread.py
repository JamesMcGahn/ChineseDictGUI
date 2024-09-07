import os
import time
from random import randint

from bs4 import BeautifulSoup
from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot

from cpod_scrape import ScrapeCpod
from keys import keys
from session_manager import SessionManger
from web_scrape import WebScrape
from write_file import WriteFile


class LessonScraperThread(QThread):
    finished = Signal()
    data_scraped = Signal(str)
    md_thd_multi_words_sig = Signal(list)
    md_use_cpod_w_sig = Signal(object)
    send_words_sig = Signal(list)
    no_sents_inc_levels = Signal(list)
    send_sents_sig = Signal(object)

    def __init__(self, lesson_list):
        super().__init__()
        self.lesson_list = lesson_list

        self.user_use_cpod_sel = False

        self.cpod_word = None
        self.user_md_multi = None
        self.scraped_data = set()
        self._mutex = QMutex()

        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False
        self.user_update_levels = False
        self.new_level_selection = None

    def run(self):
        print("starting thread")
        print(self.lesson_list)
        sess = SessionManger()
        # TODO remove keys.py file
        wb = WebScrape(sess, keys["url"])
        wb.init_driver()

        for i, c_lesson in enumerate(self.lesson_list):
            print(i)
            with QMutexLocker(self._mutex):
                if self._stop:
                    break

                while self._paused:
                    self._wait_condition.wait(self._mutex)  # Wait until resumed

            wb.run_webdriver(c_lesson)
            lesson = wb.get_source()

            tempfile_path = WriteFile.write_file(
                "./data/temp/temp.html", lesson["source"]
            )

            data = open(tempfile_path, "r")
            soup = BeautifulSoup(data, "html.parser")
            wcpod = ScrapeCpod(soup)

            sentences = []

            if "Dialogue" not in lesson["not_available"]:
                wcpod.scrape_dialogues()
                dialogues = wcpod.get_dialogues()
                sentences.extend(dialogues)

            if "Expansion" not in lesson["not_available"]:
                wcpod.scrape_expansion()
                expand = wcpod.get_expansion()
                # TODO send sentences
                sentences.extend(expand)

            if "Grammar" not in lesson["not_available"]:
                wcpod.scrape_lesson_grammar()
                grammar = wcpod.get_grammar()
                sentences.extend(grammar)

            self.send_sents_sig.emit(sentences)

            if "Vocabulary" not in lesson["not_available"]:
                words = wcpod.scrape_lesson_vocab()

                # TODO check for duplicates here or somewhere else
                # TODO send back words to page ->new thread to better definitions/audio
                self.send_words_sig.emit(words)
            else:
                self.send_words_sig.emit([])

            try:
                os.remove(tempfile_path)
            except OSError as error:
                raise RuntimeError(error)
            time.sleep(randint(6, 15))
        wb.close()
        self.finished.emit()

    def scrape_word(self, word):
        return f"Scraped result for {word}"

    def resume(self):
        self.mutex.lock()
        self.paused = False
        self.wait_condition.wakeAll()
        self.mutex.unlock()

    @Slot(int)
    def get_md_user_select(self, int):
        self.user_md_multi = int
        self._wait_condition.wakeAll()

    @Slot(bool)
    def get_use_cpod_w(self, decision):
        self.user_use_cpod_sel = decision
        self._wait_condition.wakeAll()

    @Slot(bool, list)
    def get_updated_sents_levels(self, changed, levels):
        if changed:
            self.user_update_levels = True
            self.new_level_selection = levels

        self._wait_condition.wakeAll()

import os
import time
from random import randint

from bs4 import BeautifulSoup
from PySide6.QtCore import QMutexLocker, QObject, Signal

from utils.files import WriteFile

from ..cpod_scrape import ScrapeCpod


class LessonScraperWorker(QObject):
    finished = Signal()
    send_sents_sig = Signal(object)
    send_words_sig = Signal(list)

    def __init__(self, web_driver, lesson_list, mutex, wait_condition, parent_thread):
        super().__init__()
        self.web_driver = web_driver
        self.lesson_list = lesson_list
        self._mutex = mutex
        self._wait_condition = wait_condition
        self.parent_thread = parent_thread

    def do_work(self):
        for i, c_lesson in enumerate(self.lesson_list):
            print(i)
            with QMutexLocker(self._mutex):
                if self.parent_thread._stop:
                    break

                while self.parent_thread._paused:
                    self._wait_condition.wait(self._mutex)  # Wait until resumed

            self.web_driver.run_webdriver(c_lesson)
            lesson = self.web_driver.get_source()

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
                # TODO handle error
                print(error)
            time.sleep(randint(6, 15))
        self.finished.emit()

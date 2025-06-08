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
    send_dialogue = Signal(object, object)

    def __init__(self, web_driver, lesson_list, mutex, wait_condition, parent_thread):
        super().__init__()
        self.web_driver = web_driver
        self.lesson_list = lesson_list
        self._mutex = mutex
        self._wait_condition = wait_condition
        self.parent_thread = parent_thread
        self.temp_file_paths = []

    def do_work(self):
        for i, c_lesson in enumerate(self.lesson_list):
            print(i)
            with QMutexLocker(self._mutex):
                if self.parent_thread._stop:
                    break

                while self.parent_thread._paused:
                    self._wait_condition.wait(self._mutex)  # Wait until resumed

            self.web_driver.run_webdriver(c_lesson)

            source = self.web_driver.get_source()
            not_avail = self.web_driver.get_not_available()
            # TODO: add try here

            tempfile_path = WriteFile.write_file("./data/temp/temp.html", source)
            self.temp_file_paths.append(tempfile_path)
            data = open(tempfile_path, "r")
            soup = BeautifulSoup(data, "html.parser")
            wcpod = ScrapeCpod(soup)

            lesson_audio, dialogue_audio = wcpod.scrape_lesson_and_dialogue_audio()
            print("lesss", lesson_audio, dialogue_audio)
            self.send_dialogue.emit(lesson_audio, dialogue_audio)

            sentences = []

            if "Dialogue" not in not_avail:
                wcpod.scrape_dialogues()
                dialogues = wcpod.get_dialogues()
                sentences.extend(dialogues)

            if "Expansion" not in not_avail:
                wcpod.scrape_expansion()
                expand = wcpod.get_expansion()
                # TODO send sentences
                sentences.extend(expand)

            if "Grammar" not in not_avail:
                wcpod.scrape_lesson_grammar()
                grammar = wcpod.get_grammar()
                sentences.extend(grammar)

            self.send_sents_sig.emit(sentences)

            if "Vocabulary" not in not_avail:
                words = wcpod.scrape_lesson_vocab()

                if len(words) == 0:
                    print("scrape again")
                    self.web_driver.run_section(c_lesson, "Vocabulary")
                    source = self.web_driver.get_source()
                    tempfile_path = WriteFile.write_file(
                        "./data/temp/temp-v.html", source
                    )

                    data_v = open(tempfile_path, "r")
                    soup = BeautifulSoup(data_v, "html.parser")
                    wcpod = ScrapeCpod(soup)
                    words = wcpod.scrape_lesson_vocab()
                    print(len(words), words)
                    self.temp_file_paths.append(tempfile_path)
                # TODO check for duplicates here or somewhere else
                # TODO send back words to page ->new thread to better definitions/audio
                self.send_words_sig.emit(words)
            else:
                self.send_words_sig.emit([])

            for path in self.temp_file_paths:
                try:
                    os.remove(path)
                except OSError as error:
                    # TODO handle error
                    print(error)
            time.sleep(randint(6, 15))
        self.finished.emit()

import time
from random import randint

from bs4 import BeautifulSoup
from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot
from session_manager import SessionManger

from cpod_scrape import ScrapeCpod
from keys import keys
from md_scrape import ScrapeMd


class WordScraperThread(QThread):
    data_scraped = Signal(str)
    md_thd_multi_words_sig = Signal(list)
    md_use_cpod_w_sig = Signal(object)
    send_word_sig = Signal(object)

    def __init__(
        self, word_list, definition_source, save_sentences, level_selection=False
    ):
        super().__init__()
        self.word_list = word_list
        self.definition_source = definition_source
        self.save_sentences = save_sentences
        self.level_selection = level_selection

        self.user_use_cpod_sel = False

        self.cpod_word = None
        self.user_md_multi = None
        self.scraped_data = set()
        self._mutex = QMutex()

        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False

    def run(self):
        print("starting thread")
        for i, word in enumerate(self.word_list):
            with QMutexLocker(self._mutex):
                if self._stop:
                    break

                while self._paused:
                    self._wait_condition.wait(self._mutex)  # Wait until resumed
            # TODO remove keys.py file
            sess = SessionManger()

            cp_res = sess.get(f"{keys['url']}/dictionary/english-chinese/{word}")
            c_soup = BeautifulSoup(cp_res.text, "html.parser")

            cpod = ScrapeCpod(c_soup, word)
            cpod.scrape_defintion()

            if self.save_sentences:
                cpod.scrape_sentences(self.level_selection)
            self.cpod_word = cpod.get_defintion()
            print(self.cpod_word)
            if self.save_sentences == "Yes":
                example_sentences = cpod.get_sentences()
                # TODO do something with sentences

            if self.definition_source == "Cpod" and self.cpod_word is not None:
                self.send_word_sig.emit(self.cpod_word)
            else:
                md_res = sess.get(f"{keys['murl']}/dictionary/english-chinese/{word}")
                m_soup = BeautifulSoup(md_res.text, "html.parser")
                md = ScrapeMd(m_soup)
                md.scrape_definition()
                results = md.get_results_words()
                print(results)
                if len(results) > 1:
                    # signal with words for user to pick correct definition

                    self.md_thd_multi_words_sig.emit(results)
                    self._wait_condition.wait(self._mutex)

                self.m_defined_word = md.def_selection(self.user_md_multi)

                if self.cpod_word and self.m_defined_word is not None:
                    self.m_defined_word.audio = self.cpod_word.audio

                    self.send_word_sig.emit(self.m_defined_word)

                elif self.m_defined_word is not None:
                    self.send_word_sig.emit(self.m_defined_word)

                elif self.m_defined_word is None and self.cpod_word is not None:
                    print("emit -- gerer")
                    self.md_use_cpod_w_sig.emit(self.cpod_word)
                    self._wait_condition.wait(self._mutex)

                    if self.user_use_cpod_sel:
                        self.send_word_sig.emit(self.cpod_word)

            # Simulate scraping data
            # self.update_signal.emit(f"Scraping: {word}")
            # self.msleep(1000)  # Simulate a delay

            # if word in self.scraped_data:
            #     self.user_interaction_needed.emit(word)
            #     self.mutex.lock()
            #     self.paused = True
            #     self.mutex.unlock()
            # else:
            #     scraped_result = self.scrape_word(word)
            #     self.scraped_data.add(word)
            #     self.data_scraped.emit(scraped_result)
            time.sleep(randint(6, 15))  # Simulate time-consuming scraping

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

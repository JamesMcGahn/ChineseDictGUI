import time
from random import randint
from urllib.parse import quote, urlencode

from bs4 import BeautifulSoup
from PySide6.QtCore import QMutex, QMutexLocker, QThread, QWaitCondition, Signal, Slot

from keys import keys
from services.network import NetworkWorker, SessionManager

from ..cpod import ScrapeCpod
from ..mdgb.md_scrape import ScrapeMd


class WordScraperThread(QThread):
    finished = Signal()
    data_scraped = Signal(str)
    md_thd_multi_words_sig = Signal(list)
    md_use_cpod_w_sig = Signal(object)
    send_word_sig = Signal(object)
    no_sents_inc_levels = Signal(list)
    send_sents_sig = Signal(object)

    def __init__(
        self, word_list, definition_source, save_sentences, level_selection=False
    ):
        super().__init__()
        self.word_list = word_list
        self.definition_source = definition_source
        self.save_sentences = save_sentences
        self.level_selection = level_selection

        self.cpod_word = None
        self.m_defined_word = None
        self.c_soup = None
        self.m_soup = None

        # Thread Control
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._stop = False
        self._paused = False
        # GUI User response variables
        self.user_update_levels = False
        self.user_new_level_selection = None
        self.user_md_multi = None
        self.user_use_cpod_sel = False

    def run(self):
        self.session = SessionManager()
        print("starting thread")
        for i, word in enumerate(self.word_list):
            if word.strip() == "":
                continue
            print(i, len(self.word_list), word)

            self.pause_if_needed(self._stop)

            encoded_word = quote(word)
            # TODO remove keys.py file
            self.get_soup(
                f"{keys['old_url']}dictionary/english-chinese/{encoded_word}",
                self.received_csoup,
            )

            # TODO emit progess
            self.pause_if_needed(self.c_soup is None)
            self.scrape_cpod(word)
            self.scrape_sentences()

            if self.definition_source == "Cpod" and self.cpod_word is not None:
                self.send_word_sig.emit(self.cpod_word)
            else:
                params = {"page": "worddict", "wdrst": "0", "wdqb": word}
                encoded_params = urlencode(params)
                self.get_soup(
                    f"{keys['murl']}/dictionary/english-chinese?{encoded_params}",
                    self.received_msoup,
                )
                self.pause_if_needed(self.m_soup is None)
                self.scrape_mgdb(word)
                self.send_mgdb()

            # trunk-ignore(bandit/B311)
            time.sleep(randint(6, 15))

            self.cpod_word = None
            self.m_defined_word = None
            self.c_soup = None
            self.m_soup = None

        self.finished.emit()
        self.quit()

    def pause_if_needed(self, checkVar):
        with QMutexLocker(self._mutex):
            if checkVar:
                self._paused = True

            while self._paused:
                self._wait_condition.wait(self._mutex)  # Wait until resumed

    def resume(self):
        with QMutexLocker(self._mutex):  # Automatic lock and unlock
            self._paused = False
            self._wait_condition.wakeOne()

    def get_soup(self, url, receiver):
        self.net_worker = NetworkWorker(self.session, "GET", url, timeout=15, retry=2)
        self.net_worker.response_sig.connect(receiver)
        self.net_worker.error_sig.connect(receiver)
        self.net_worker.moveToThread(self)
        self.net_worker.do_work()

    def received_csoup(self, status, response, errorType=None):
        print("received soup")
        print(response)
        if status == "error":
            print("error")
            # TODO: do something
            self.c_soup = None
            self.cpod_word = None
        else:
            self.c_soup = BeautifulSoup(response.text, "html.parser")

            self.resume()
        self.net_worker.deleteLater()

    def received_msoup(self, status, response, errorType=None):
        print("here")
        if status == "error":
            print("error")
            self.m_defined_word = None
        else:
            self.m_soup = BeautifulSoup(response.text, "html.parser")

        self.resume()
        self.net_worker.deleteLater()

    def scrape_cpod(self, word):
        self.cpod = ScrapeCpod(self.c_soup, word)
        self.cpod.scrape_definition()
        self.cpod_word = self.cpod.get_definition()

    def scrape_mgdb(self, word):
        md = ScrapeMd(self.m_soup)
        md.scrape_definition()
        results = md.get_results_words()

        with QMutexLocker(self._mutex):
            if len(results) > 1:
                self.md_thd_multi_words_sig.emit(results)
                self._paused = True

            while self._paused:
                self._wait_condition.wait(self._mutex)

        if self.user_md_multi is not None:
            self.m_defined_word = md.def_selection(self.user_md_multi)
            self.user_md_multi = None
        elif len(results) == 1:
            self.m_defined_word = md.def_selection(0)
        else:
            self.m_defined_word = None

    def send_mgdb(self):
        print("sending mgdb")
        if self.cpod_word and self.m_defined_word is not None:
            if self.m_defined_word.pinyin == self.cpod_word.pinyin:
                self.m_defined_word.audio = self.cpod_word.audio

            self.send_word_sig.emit(self.m_defined_word)

        elif self.m_defined_word is not None:
            self.send_word_sig.emit(self.m_defined_word)

        with QMutexLocker(self._mutex):
            if self.m_defined_word is None and self.cpod_word is not None:
                self.md_use_cpod_w_sig.emit(self.cpod_word)
                self._paused = True
            while self._paused:
                self._wait_condition.wait(self._mutex)

        if self.user_use_cpod_sel:
            self.send_word_sig.emit(self.cpod_word)
            self.user_use_cpod_sel = False

    def scrape_sentences(self):
        if self.save_sentences and self.cpod_word is not None:
            self.cpod.scrape_sentences()
            example_sentences = self.cpod.get_sentences()

            if self.level_selection is not False:
                level_sentences = [
                    x for x in example_sentences if x.level in self.level_selection
                ]

                with QMutexLocker(self._mutex):
                    if len(level_sentences) == 0:
                        print("theres is 0 sentences")
                        self.no_sents_inc_levels.emit(self.level_selection)

                        self._paused = True

                    while self._paused:
                        self._wait_condition.wait(self._mutex)

                if self.user_update_levels:
                    if self.user_new_level_selection is not False:
                        level_sentences = [
                            x
                            for x in example_sentences
                            if x.level in self.user_new_level_selection
                        ]

                self.send_sents_sig.emit(level_sentences)
                self.user_update_levels = False
            else:
                self.send_sents_sig.emit(example_sentences)

    @Slot(int)
    def get_md_user_select(self, int):
        self.user_md_multi = int
        self.resume()

    @Slot(bool)
    def get_use_cpod_w(self, decision):
        self.user_use_cpod_sel = decision
        self.resume()

    @Slot(bool, list)
    def get_updated_sents_levels(self, changed, levels):
        if changed:
            self.user_update_levels = True
            self.user_new_level_selection = levels

        self.resume()

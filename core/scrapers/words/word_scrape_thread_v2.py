import os
import time
from collections import deque
from random import randint
from urllib.parse import quote, urlencode

from bs4 import BeautifulSoup
from PySide6.QtCore import QMutex, QThread, QWaitCondition, Signal, Slot

from keys import keys
from models.dictionary import Sentence, Word
from services.network import NetworkWorker
from utils.files import WriteFile

from ..cpod import ScrapeCpod
from ..cpod.lessons import WebScrape
from ..mdgb.md_scrape import ScrapeMd


class WordScraperThreadV2(QThread):
    finished = Signal()
    data_scraped = Signal(str)
    md_thd_multi_words_sig = Signal(list)
    md_use_cpod_w_sig = Signal(object)
    send_word_sig = Signal(object)
    no_sents_inc_levels = Signal(list)
    send_sents_sig = Signal(object)
    next_word_signal = Signal()

    def __init__(
        self, word_list, definition_source, save_sentences, level_selection=False
    ):
        super().__init__()
        self.word_list = deque(word_list)
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

        self.web_driver = WebScrape(keys["url"])
        self.host_url = keys["url"]
        self.audio_host_url = keys["audio_host"]
        self.token = None
        self.current_word = None
        self.next_word_signal.connect(self.get_next_word)

    @Slot()
    def do_work(self):
        print("starting worker")

        self.web_driver.init_driver()
        print("finished setting up webscrape")
        self.next_word_signal.emit()

    @Slot()
    def get_next_word(self):
        if self.word_list:
            self.current_word = self.word_list.popleft().strip()
            if self.current_word == "":
                pass
                # TODO

            if self.definition_source == "Cpod" or self.save_sentences:
                if not self.token:
                    try:

                        print("initting driver")
                        self.web_driver.find_bearer()
                        token = self.web_driver.get_bearer()
                        # TODO save token to settings?
                        if not token:
                            raise RuntimeError("Bearer token is None after login flow.")
                        self.token = token
                    except RuntimeError as e:
                        print(e)
                    except Exception as e:
                        print(e)

                encoded_word = quote(self.current_word)
                self.headers = {"Authorization": self.token}
                self.word_search_thread = QThread()
                self.word_search_worker = NetworkWorker(
                    "GET",
                    f"{self.host_url}api/v1/search/search-dictionary/{encoded_word}?skip=0",
                    headers=self.headers,
                )
                self.word_search_worker.moveToThread(self.word_search_thread)
                self.word_search_thread.start()
                self.word_search_worker.response_sig.connect(self.receive_word_results)
                self.word_search_worker.do_work()
                self.word_search_worker.finished.connect(
                    self.word_search_worker.deleteLater
                )
                self.word_search_worker.finished.connect(self.word_search_thread.quit)
                self.word_search_thread.finished.connect(
                    self.word_search_thread.deleteLater
                )
            else:
                self.get_mg_word()
        else:
            self.web_driver.close()
            print("Finished getting all words")
            self.finished.emit()

    def receive_word_results(self, status, payload):
        words_results = payload.json()
        print(words_results)
        word_matched = False
        if "results" in words_results and len(words_results["results"]) > 0:

            for word in words_results["results"]:
                if "simplified" in word and word["simplified"] == self.current_word:
                    word_matched = True

        if word_matched:
            print("word matched")
            encoded_word = quote(self.current_word)
            print(f"{self.host_url}api/v1/dictionary/get-details?word={encoded_word}")
            self.word_detail_search_thread = QThread()
            self.word_detail_search_worker = NetworkWorker(
                "GET",
                f"{self.host_url}api/v1/dictionary/get-details?word={encoded_word}",
                headers=self.headers,
            )
            self.word_detail_search_worker.moveToThread(self.word_detail_search_thread)
            self.word_detail_search_thread.start()
            self.word_detail_search_worker.response_sig.connect(
                self.receive_detail_word_result
            )
            self.word_detail_search_worker.do_work()
            self.word_detail_search_worker.finished.connect(
                self.word_detail_search_worker.deleteLater
            )
            self.word_detail_search_worker.finished.connect(
                self.word_detail_search_thread.quit
            )
            self.word_detail_search_thread.finished.connect(
                self.word_detail_search_thread.deleteLater
            )

        else:
            self.get_mg_word()

    def receive_detail_word_result(self, status, payload):
        self.word_payload = payload.json()
        print("******** \n")
        print(self.word_payload)
        # TODO fix this is an array
        if "definition" in self.word_payload and self.word_payload["definition"]:
            character = self.word_payload["definition"][0]["simplified"].strip()
            pinyin = (
                self.word_payload["definition"][0]["pinyin"].strip().replace(" ", "")
            )
            definition_string = ""
            audio = self.word_payload["audioUrl"]
            for index, definition in enumerate(self.word_payload["definition"]):
                def_split = definition["definition"].split("/")
                def_split = [
                    f"{i + 1}. {define} " for i, define in enumerate(def_split)
                ]
                pinyin_per_def = definition["pinyin"]
                definition_build = "".join(def_split).strip()

                if len(self.word_payload["definition"]) > 1 and index > 0:
                    definition_string += (
                        f"{index + 1}. - {pinyin_per_def} - {definition_build}"
                    )
                else:
                    definition_string += definition_build
                if index < len(self.word_payload["definition"]):
                    definition_string += "\n"

                if index < len(self.word_payload["definition"]) - 1:
                    definition_string += "\n"
        print("")
        print(character, self.current_word)
        if character == self.current_word:
            definition_string = definition_string.strip()
            self.cpod_word = Word(character, definition_string, pinyin, audio)
            print(self.definition_source, self.cpod_word)

            if self.definition_source == "Cpod" and self.cpod_word is not None:
                if self.cpod_word.audio == "":
                    self.get_old_dict_audio()
                else:
                    self.send_word_sig.emit(self.cpod_word)
                    self.completed_word()
            elif self.save_sentences and self.cpod_word is not None:
                if self.cpod_word.audio == "":
                    self.get_old_dict_audio()
                else:
                    self.get_sentences()
            else:
                self.get_mg_word()

        else:
            print("failed comparision")
            self.get_mg_word()

    def get_old_dict_audio(
        self,
    ):
        encoded_word = quote(self.current_word)
        old_url = keys["old_url"]
        found_audio_page = self.web_driver.go_and_wait_for_id(
            f"{old_url}dictionary/english-chinese/{encoded_word}",
            "myTable",
        )
        print(found_audio_page, "found id on page")
        self.web_driver.capture_page_source()
        source = self.web_driver.get_source()

        if source and found_audio_page:
            try:
                tempfile_path = WriteFile.write_file(
                    "./data/temp_files/temp.html", source, print_to_user=True
                )
                data = open(tempfile_path, "r")
                self.c_soup = BeautifulSoup(data, "html.parser")
                self.cpod = ScrapeCpod(self.c_soup, self.current_word)
                self.cpod.scrape_definition()
                word = self.cpod.get_definition()
                print(vars(word), "from the html")
                self.cpod_word.audio = word.audio
                print("got new audio")

                try:
                    os.remove(tempfile_path)
                except OSError as error:
                    # TODO handle error
                    print(error)
            except Exception as e:
                print(
                    f"Trouble getting audio {e}",
                )

        if self.definition_source == "Cpod" and self.cpod_word is not None:
            self.send_word_sig.emit(self.cpod_word)

        if self.save_sentences and self.cpod_word is not None:
            self.get_sentences()

        elif not self.definition_source == "Cpod":
            self.send_mgdb()
        else:
            self.completed_word()

    def get_sentences(self):

        self.example_sentences = []
        for sentence in self.word_payload["lessons"]:
            audio = sentence["audioUrl"]
            english = sentence["english"]
            pinyin = sentence["pinyin"]
            chinese = sentence["simplified"]
            level = sentence["lessonInfo"]["level"]
            sentence = Sentence(chinese, english, pinyin, audio, level)
            self.example_sentences.append(sentence)

        if self.level_selection:
            level_sentences = [
                x for x in self.example_sentences if x.level in self.level_selection
            ]

            if self.user_update_levels:
                if self.user_new_level_selection is not False:
                    level_sentences = [
                        x
                        for x in self.example_sentences
                        if x.level in self.user_new_level_selection
                    ]
                    if len(level_sentences) == 0 and len(self.example_sentences) > 0:
                        self.no_sents_inc_levels.emit(self.level_selection)
                        return
            elif len(level_sentences) == 0 and len(self.example_sentences) > 0:
                self.no_sents_inc_levels.emit(self.level_selection)
                return

            self.send_sents_sig.emit(level_sentences)
            self.user_update_levels = False
        else:
            self.send_sents_sig.emit(self.example_sentences)

        if not self.definition_source == "Cpod":
            self.get_mg_word()
        else:
            self.completed_word()

    def get_mg_word(self):
        params = {"page": "worddict", "wdrst": "0", "wdqb": self.current_word}
        encoded_params = urlencode(params)
        self.mg_word_thread = QThread()
        self.mg_word_worker = NetworkWorker(
            "GET",
            f"{keys['murl']}/dictionary/english-chinese?{encoded_params}",
            timeout=15,
            retry=2,
        )
        self.mg_word_worker.moveToThread(self.mg_word_thread)
        self.mg_word_thread.start()
        self.mg_word_worker.response_sig.connect(self.received_msoup)
        self.mg_word_worker.finished.connect(self.mg_word_worker.deleteLater)
        self.mg_word_worker.finished.connect(self.mg_word_thread.quit)
        self.mg_word_thread.finished.connect(self.mg_word_thread.deleteLater)

        # self.mg_word_worker.error_sig.connect(receiver)
        self.mg_word_worker.do_work()

    def received_msoup(self, status, response, errorType=None):
        print("here")
        if status == "error":
            print("error")
            self.m_defined_word = None
        else:
            self.m_soup = BeautifulSoup(response.text, "html.parser")
            self.scrape_mgdb()

    def scrape_mgdb(self):
        self.md = ScrapeMd(self.m_soup)
        self.md.scrape_definition()
        results = self.md.get_results_words()
        print("sending results")
        if len(results) > 1:
            self.md_thd_multi_words_sig.emit(results)
            return
        elif len(results) == 1:
            self.m_defined_word = self.md.def_selection(0)
        else:
            self.m_defined_word = None

        print("recieved results", self.user_md_multi)

        self.send_mgdb()

    def send_mgdb(self):
        print("sending mgdb")
        if self.cpod_word and self.m_defined_word is not None:
            if self.m_defined_word.pinyin == self.cpod_word.pinyin:
                self.m_defined_word.audio = self.cpod_word.audio

            self.send_word_sig.emit(self.m_defined_word)

        elif self.m_defined_word is not None:
            self.send_word_sig.emit(self.m_defined_word)

        elif self.m_defined_word is None and self.cpod_word is not None:
            self.md_use_cpod_w_sig.emit(self.cpod_word)
            return

        self.completed_word()

    def reset_state(self):
        self.current_word = None
        self.cpod_word = None
        self.m_defined_word = None
        self.c_soup = None
        self.m_soup = None

    def completed_word(self, skipped=False):
        if skipped:
            print(f"Skipping Getting Definition for {self.current_word} ")
        else:
            print(f"Completed Getting Definition for {self.current_word} ")

        self.reset_state()

        wait_time = randint(3, 13)
        print(f"Waiting for {wait_time} before searching for the next word")
        time.sleep(wait_time)
        self.next_word_signal.emit()

    @Slot(int)
    def get_md_user_select(self, val: int):
        print("received ", val)
        self.user_md_multi = val
        if self.user_md_multi is not None and not self.user_md_multi == 9999999:
            self.m_defined_word = self.md.def_selection(self.user_md_multi)
            self.user_md_multi = None
            self.send_mgdb()
        else:
            self.completed_word(True)

    @Slot(bool)
    def get_use_cpod_w(self, decision):
        self.user_use_cpod_sel = decision
        if self.user_use_cpod_sel:
            self.send_word_sig.emit(self.cpod_word)
            self.user_use_cpod_sel = False
            self.completed_word()
        else:
            self.completed_word(True)

    @Slot(bool, list)
    def get_updated_sents_levels(self, changed, levels):
        print(changed, levels)
        if changed:
            self.user_update_levels = True
            self.user_new_level_selection = levels

        elif not changed and not levels:
            self.get_mg_word()
            return

        self.get_sentences()

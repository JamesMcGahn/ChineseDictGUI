import concurrent.futures
import os
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from random import randint

import PySide6.QtConcurrent
from bs4 import BeautifulSoup
from db_manager import DatabaseManager
from network_thread import NetworkWorker
from PySide6.QtCore import (
    QMutex,
    QMutexLocker,
    QObject,
    QThread,
    QWaitCondition,
    Signal,
    Slot,
)
from sentsDAL import SentsDAL
from session_manager import SessionManger
from wordsDAL import WordsDAL

from cpod_scrape import ScrapeCpod
from dictionary import Word
from keys import keys
from web_scrape import WebScrape
from write_file import WriteFile


class FindAnkiInLocal(QObject):
    response_sig = Signal(str, object, str)

    def __init__(self, db_manager, ankiIds, dtype="words"):
        super().__init__()
        self.db_manager = db_manager
        self.ankiIds = ankiIds
        self.dtype = dtype

    @Slot()
    def do_work(self):
        print(f"Current thread ID -- find: {threading.get_ident()}")
        print(f"Anki running in thread: {QThread.currentThread()}")
        self.db_manager.connect()
        wd = WordsDAL(self.db_manager)
        sd = SentsDAL(self.db_manager)

        no_db_matches = []

        for id in self.ankiIds:
            if self.dtype == "words":
                result = wd.get_word_by_ankiid(id)
            else:
                result = sd.get_sent_by_ankiid(id)

            if result.fetchone() is None:
                no_db_matches.append(id)

        self.db_manager.disconnect()

        json = {
            "action": "notesInfo",
            "version": 6,
            "params": {"notes": no_db_matches},
        }

        if len(no_db_matches) == 0:
            print("no words found")
            return
        sess = SessionManger()
        self.net_worker = NetworkWorker(
            sess, "GET", "http://127.0.0.1:8765", json=json, timeout=60
        )
        self.net_worker.moveToThread(self.thread())
        print(self.thread())
        self.net_worker.response_sig.connect(self.notes_response)
        self.net_worker.error_sig.connect(self.notes_response)
        print("doo")
        self.net_worker.do_work()

    @Slot(str, object, str)
    def notes_response(self, status, response, errorType=None):
        print("dsssdsds")
        res = response
        if status == "error" or res.json()["error"] is not None:
            print(status, response, errorType)
            self.response_sig.emit(status, None, errorType)
        else:
            print("ererererere")
            print(res)
            self.response_sig.emit(status, res.json(), errorType)


class AnkiImportThread(QThread):
    data_scraped = Signal(str)
    md_thd_multi_words_sig = Signal(list)
    md_use_cpod_w_sig = Signal(object)
    send_words_sig = Signal(list)
    no_sents_inc_levels = Signal(list)
    send_sents_sig = Signal(object)

    def __init__(self):
        super().__init__()

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

        sess = SessionManger()
        json = {
            "action": "findNotes",
            "version": 6,
            "params": {"query": 'deck:"Mandarin Words"'},
        }
        # response = sess.get("http://127.0.0.1:8765", json=json)
        # response = response.json()

        net_worker = NetworkWorker(sess, "GET", "http://127.0.0.1:8765", json=json)

        # net_worker.finished.connect(net_worker.deleteLater)
        net_worker.response_sig.connect(self.received_response)
        net_worker.error_sig.connect(self.received_response)
        net_worker.moveToThread(self.thread())

        self.executor = ThreadPoolExecutor(max_workers=4)
        self.executor.submit(net_worker.do_work)

        # print(response)
        # if response["error"] is not None:
        #     # TODO: handle error properly
        #     print("error getting deck")

        # print(response["result"][0])

    def received_response(self, status, response, errorType=None):
        print("hi")
        if status == "error":
            print(status, response, errorType)
        else:
            ankiIds = response.json()["result"]
            db = DatabaseManager("chineseDict.db")
            self.worker = FindAnkiInLocal(db, ankiIds)
            self.worker.moveToThread(self.thread())
            self.worker.response_sig.connect(self.notes_response)

            # self.worker.do_work()

            self.executor.submit(self.worker.do_work)
            # anki worker here

    def notes_response(self, status, response, errorType=None):
        print("heehheheeh")

        words = response["result"]
        db = DatabaseManager("chineseDict.db")
        db.connect()
        wd = WordsDAL(db)
        db.begin_transaction()
        for word in words:
            wd.insert_word(
                Word(
                    chinese=word["fields"]["中文"]["value"],
                    pinyin=word["fields"]["Pinyin"]["value"],
                    definition=word["fields"]["English"]["value"],
                    audio=None,
                    level=word["fields"]["Notes"]["value"],
                    anki_audio=word["fields"]["audio"]["value"],
                    anki_id=word["noteId"],
                    anki_update=word["mod"],
                )
            )
        db.commit_transaction()

    def resume(self):
        self.mutex.lock()
        self.paused = False
        self.wait_condition.wakeAll()
        self.mutex.unlock()

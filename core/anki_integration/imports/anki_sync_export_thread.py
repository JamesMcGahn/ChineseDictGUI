import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QThread, Signal, Slot

from db import DatabaseManager
from db.dals import AnkiIntegrationDAL, SentsDAL, WordsDAL
from db.workers import AnkiIntQueryWorker, SentsQueryWorker, WordsQueryWorker
from services.network import NetworkWorker, SessionManager


class AnkiSyncExportThread(QThread):
    finished = Signal()
    update_add_sync_completed = Signal()

    def __init__(self, words_deckName, sents_deckName):
        super().__init__()
        self.words_deckName = words_deckName
        self.sents_deckName = sents_deckName
        self.deck_types_list = deque(["words", "sents"])
        self.deck_type = "sents"
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.cards_to_sync = []
        self.db = DatabaseManager("chineseDict.db")
        self.sentsDAL = SentsDAL(self.db)
        self.wordsDAL = WordsDAL(self.db)
        self.sync_in_progress = False
        self.sync_tasks_remaining = 0
        self.session = SessionManager()

        # self.update_add_sync_completed.connect(self.get_all_anki_deck_ids)

    def run(self):
        if self.sync_in_progress:
            return
        print(
            f"Starting Anki Import Sync in thread: {threading.get_ident()} - {QThread.currentThread()}  - {self.thread()}"
        )
        # step 1 connect to database
        print("# step 1 connect to database")
        self.db.connect()
        adb = AnkiIntegrationDAL(self.db)
        # step 2 query integration information -
        che = adb.get_anki_integration()
        (id, anki_import_time, local_import_time, initialSyncDone) = che.fetchone()
        # print(id, anki_import_time, local_import_time, initialSyncDone)
        self.local_import_time = local_import_time

        # step 3 check if initial baseline sync was completed
        print("# step 3 checking if initial baseline sync was completed")
        if initialSyncDone == 0:
            print("Initial baseline sync was not completed. Ending sync.")
            self.finished.emit()
            self.quit()
            return

        else:
            print("# intial sync was completed. Starting Sync.")
            self.sync_next_deck()

    def sync_next_deck(self):
        if self.sync_in_progress:
            return

        if self.deck_types_list:
            self.sync_in_progress = True
            self.cards_to_sync = []
            self.deck_type = self.deck_types_list.popleft()
            print(
                f"Starting Sync Process for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
            )
            self.get_edited_cards()

        else:
            print("**** Sync Complete - Card updates and adding complete")

    # step 5 query edited/new records from local db for this time interval
    def get_edited_cards(self):
        print(
            f"Getting Edited Cards for {'Sentences' if self.deck_type == 'sents' else 'Words' }"
        )
        if self.deck_type == "sents":
            self.dbworker = SentsQueryWorker("get_anki_export_sentences")
            self.dbworker.moveToThread(self)
            self.dbworker.error_occurred.emit(self.error_occured)
            self.dbworker.result.connect(self.receive_records_for_export)
            self.dbworker.finished.connect(self.dbworker.deleteLater)
            self.dbworker.do_work()
        else:
            self.dbworker = WordsQueryWorker("get_anki_export_words")
            self.dbworker.moveToThread(self)
            self.dbworker.result.connect(self.receive_records_for_export)
            self.dbworker.error_occurred.emit(self.error_occured)
            # self.dbworker.finished.connect(self.receive_records_for_export)
            self.dbworker.finished.connect(self.dbworker.deleteLater)
            self.dbworker.do_work()

    @Slot(list)
    def receive_records_for_export(self, records):
        print(records)
        # step 6 check if record local_update is > integration table local_update
        records = [
            record
            for record in records
            if record.local_update is None
            or record.local_update > self.local_import_time
        ]

        self.records_to_export = records

        self.build_export_payloads()

    def build_export_payloads(self):
        self.new_card_note_payload = []
        self.new_card_local_refs = []
        self.edited_card_note_payload = []
        self.edited_card_local_refs = []

        deck_name = (
            self.sents_deckName if self.deck_type == "sents" else self.words_deckName
        )

        # TODO: separate record - need id for update
        for rec in self.records_to_export:

            if rec.anki_id:
                note = {
                    "action": "updateNoteFields",
                    "params": {
                        "note": {
                            "id": rec.anki_id,
                            "fields": {
                                "Chinese": rec.chinese,
                                "English": (
                                    rec.english
                                    if self.deck_type == "sents"
                                    else rec.definition
                                ),
                                "Pinyin": rec.pinyin,
                                "Notes": rec.level,
                                "Audio": rec.anki_audio,
                                "LDBID": str(rec.id),
                            },
                        }
                    },
                }
                self.edited_card_note_payload.append(note)
                self.edited_card_local_refs.append(rec.id)
            else:
                note = {
                    "deckName": f"{deck_name}",
                    "modelName": f"Glossika ZS-{"S" if self.deck_type == "sents" else "W"}",
                    "fields": {
                        "Chinese": rec.chinese,
                        "English": (
                            rec.english if self.deck_type == "sents" else rec.definition
                        ),
                        "Pinyin": rec.pinyin,
                        "Notes": rec.level,
                        "Audio": rec.anki_audio,
                        "LDBID": str(rec.id),
                    },
                    "options": {
                        "allowDuplicate": False,
                        "duplicateScope": "deck",
                    },
                    "tags": [rec.level],
                }
                self.new_card_note_payload.append(note)
                self.new_card_local_refs.append(rec.id)

        self.verify_export_new_cards_to_anki()

    def verify_export_new_cards_to_anki(self):

        self.sync_tasks_remaining = 0
        if len(self.new_card_note_payload) > 0:
            print("Starting sync for new cards")
            self.sync_tasks_remaining += 1
            json = {
                "action": "canAddNotesWithErrorDetail",
                "version": 6,
                "params": {"notes": self.new_card_note_payload},
            }
            print(json)
            print("Start")

            self.new_record_verify_net_thread = QThread()
            self.networker_verify_add = NetworkWorker(
                self.session, "GET", "http://127.0.0.1:8765", json=json, timeout=20
            )
            self.new_record_verify_net_thread.start()
            self.networker_verify_add.moveToThread(self.new_record_verify_net_thread)
            self.networker_verify_add.finished.connect(
                self.networker_verify_add.deleteLater
            )
            self.networker_verify_add.response_sig.connect(
                lambda status, response: self.verify_export_new_cards_response(
                    status, response
                )
            )
            self.new_record_verify_net_thread.finished.connect(
                self.new_record_verify_net_thread.deleteLater
            )
            self.networker_verify_add.start_work.emit()
        else:
            print("No new cards to sync")
            self.export_updates_cards()

        # if len(edited_card_note_payload) > 0:
        #     self.sync_tasks_remaining += 1
        #     json = {
        #         "action": "addNotes",
        #         "version": 6,
        #         "params": {"notes": edited_card_note_payload},
        #     }
        #     print("Start")

        #     self.update_record_net_thread = QThread()
        #     self.networker_update = NetworkWorker(
        #         self.session, "GET", "http://127.0.0.1:8765", json=json, timeout=20
        #     )
        #     self.update_record_net_thread.start()
        #     self.networker_update.moveToThread(self.update_record_net_thread)
        #     self.networker_update.finished.connect(self.networker_update.deleteLater)
        #     self.networker_update.response_sig.connect(
        #         lambda status, response: self.notes_response(
        #             status,
        #             response,
        #             edited_card_local_refs,
        #             edited_card_note_payload,
        #         )
        #     )
        #     self.update_record_net_thread.finished.connect(
        #         self.update_record_net_thread.deleteLater
        #     )
        #     self.networker_update.start_work.emit()

    @Slot(str, object, str)
    def verify_export_new_cards_response(self, status, response):

        local_refs = self.new_card_local_refs
        note_payload = self.new_card_note_payload
        print("here - ttt")
        res = response.json()
        print(res)
        if status == "success":
            # print(res)
            # self.response_sig.emit(status, res.json(), errorType)
            result = res["result"]
            print(result)
            verified_cards_to_add = []
            failed_cards_to_add = []

            for i, status in enumerate(result):
                print(i, status)
                print(local_refs)
                local_id = local_refs[i]
                payload = note_payload[i]
                print(local_id, status["canAdd"])

                if status["canAdd"]:
                    verified_cards_to_add.append(payload)
                else:
                    # TODO handle error cards
                    failed_cards_to_add.append((local_id, payload, status["error"]))

            print(len(result), len(verified_cards_to_add), len(failed_cards_to_add))
            print(verified_cards_to_add, "\n\n\n", failed_cards_to_add)

            if len(verified_cards_to_add) > 0:
                self.export_new_cards(verified_cards_to_add)

            # for i, anki_id in enumerate(result):
            #     local_id = local_refs[i]
            #     if anki_id is not None:
            #         # update_local_db_with_anki_id(local_id, anki_id)
            #         print("success", local_id, anki_id)
            #     else:
            #         # log_failed_note_export(local_id, note_payload[i])
            #         print("fail", local_id, note_payload[i])
        else:
            print("There was an error", res["error"])

    def export_new_cards(self, verified_payload):
        self.sync_tasks_remaining += 1
        json = {
            "action": "addNotes",
            "version": 6,
            "params": {"notes": verified_payload},
        }
        print(json)
        print("Start")

        self.new_record_verify_net_thread = QThread()
        self.networker_verify_add = NetworkWorker(
            self.session, "GET", "http://127.0.0.1:8765", json=json, timeout=20
        )
        self.new_record_verify_net_thread.start()
        self.networker_verify_add.moveToThread(self.new_record_verify_net_thread)
        self.networker_verify_add.finished.connect(
            self.networker_verify_add.deleteLater
        )
        self.networker_verify_add.response_sig.connect(
            lambda status, response: self.export_add_new_notes_response(
                status, response, verified_payload
            )
        )
        self.new_record_verify_net_thread.finished.connect(
            self.new_record_verify_net_thread.deleteLater
        )
        self.networker_verify_add.start_work.emit()

    def export_add_new_notes_response(self, status, response, verified_payload):
        res = response.json()
        print(res)

        timestamp = int(time.time())

        cards_to_update_db = []
        if status == "success" and "result" in res:
            if res["result"] is None:
                self.error_occured("Error in checking if export cards.")

            if len(res["result"]) > 0:
                for i, card in enumerate(res["result"]):
                    print(verified_payload[i])
                    id = verified_payload[i]["fields"]["LDBID"]
                    print(card, id)

                    cards_to_update_db.append(
                        {
                            "id": id,
                            "updates": {"anki_id": card, "anki_update": timestamp},
                        }
                    )
                # TODO: Add Check to make sure there are cards to update
                if self.deck_type == "sents":
                    print(cards_to_update_db)
                    self.s_updatedbworker = SentsQueryWorker(
                        "update_sentences", sentences=cards_to_update_db
                    )
                    self.s_updatedbworker.moveToThread(self)
                    self.s_updatedbworker.error_occurred.emit(self.error_occured)
                    self.s_updatedbworker.finished.connect(self.export_updates_cards)
                    self.s_updatedbworker.finished.connect(
                        self.s_updatedbworker.deleteLater
                    )
                    self.s_updatedbworker.do_work()
                else:
                    print(cards_to_update_db)
                    self.w_updatedbworker = WordsQueryWorker(
                        "update_words", words=cards_to_update_db
                    )
                    self.w_updatedbworker.moveToThread(self)
                    self.w_updatedbworker.error_occurred.emit(self.error_occured)
                    self.w_updatedbworker.finished.connect(self.export_updates_cards)
                    self.w_updatedbworker.finished.connect(
                        self.w_updatedbworker.deleteLater
                    )
                    self.w_updatedbworker.do_work()

    def export_updates_cards(self):

        if len(self.edited_card_note_payload) > 0:
            print("Starting export of updated cards")
            self.sync_tasks_remaining += 1
            json = {
                "action": "multi",
                "version": 6,
                "params": {"actions": self.edited_card_note_payload},
            }
            print(json)
            print("Start")

            self.update_record_verify_net_thread = QThread()
            self.networker_verify_add = NetworkWorker(
                self.session, "GET", "http://127.0.0.1:8765", json=json, timeout=20
            )
            self.update_record_verify_net_thread.start()
            self.networker_verify_add.moveToThread(self.update_record_verify_net_thread)
            self.networker_verify_add.finished.connect(
                self.networker_verify_add.deleteLater
            )
            self.networker_verify_add.response_sig.connect(
                lambda status, response: self.export_update_notes_response(
                    status, response
                )
            )
            self.update_record_verify_net_thread.finished.connect(
                self.update_record_verify_net_thread.deleteLater
            )
            self.networker_verify_add.start_work.emit()
        else:
            print("No Updated cards to sync")
            self.update_db_integration_record()

    def export_update_notes_response(self, status, response):
        res = response.json()
        print(res)

        timestamp = int(time.time())

        cards_to_update_db = []
        failed_cards_to_add = []
        if status == "success" and "result" in res:
            if res["result"] is None:
                error_message = {res["error"]} if "error" in res else "error"
                self.error_occured(f"Error in exporting cards: {error_message}")
                return

            if len(res["result"]) > 0:
                for i, card in enumerate(res["result"]):

                    payload = self.edited_card_note_payload[i]
                    id = payload["params"]["note"]["fields"]["LDBID"]
                    print(card, id)

                    if isinstance(card, dict) and card.get("error"):
                        print((id, payload, card["error"]))
                        failed_cards_to_add.append((id, payload, card["error"]))
                    else:
                        cards_to_update_db.append(
                            {"id": id, "updates": {"anki_update": timestamp}}
                        )
                        print({"id": id, "updates": {"anki_update": timestamp}})

                # TODO: Add Check to make sure there are cards to update

                if self.deck_type == "sents":
                    print(cards_to_update_db)
                    self.s_updatedbworker = SentsQueryWorker(
                        "update_sentences", sentences=cards_to_update_db
                    )
                    self.s_updatedbworker.moveToThread(self)
                    self.s_updatedbworker.error_occurred.emit(self.error_occured)
                    # self.s_updatedbworker.finished.connect(self.wait_for_sync_complete)
                    self.s_updatedbworker.finished.connect(
                        self.s_updatedbworker.deleteLater
                    )
                    self.s_updatedbworker.do_work()
                else:
                    print(cards_to_update_db)
                    self.w_updatedbworker = WordsQueryWorker(
                        "update_words", words=cards_to_update_db
                    )
                    self.w_updatedbworker.moveToThread(self)
                    self.w_updatedbworker.error_occurred.emit(self.error_occured)
                    self.w_updatedbworker.finished.connect(
                        self.update_db_integration_record
                    )
                    self.w_updatedbworker.finished.connect(
                        self.w_updatedbworker.deleteLater
                    )
                    self.w_updatedbworker.do_work()

    def update_db_integration_record(self):
        timestamp = int(time.time())
        self.ankiDb = AnkiIntQueryWorker(
            "update_integration", updates={"local_update": timestamp}
        )

        def _continue_sync():
            if self.deck_type == "sents":
                print("** Completed syncing Sentences.")
            else:
                print("** Completed syncing Words.")
            self.sync_in_progress = False

            self.sync_next_deck()

        self.ankiDb.moveToThread(self)
        self.ankiDb.error_occurred.emit(self.error_occured)
        self.ankiDb.finished.connect(self.ankiDb.deleteLater)
        self.ankiDb.finished.connect(_continue_sync)

        self.ankiDb.do_work()

    def error_occured(self, message):
        print(message)
        # TODO: do something about error - Toast?


# step 1 connect to database
# step 2 query integration information -
# step 3 check if initial baseline sync was completed
# step 4 figure out the time difference between last sync
# step 5 query edited/new records from local db for this time interval
# - WHERE anki_id IS NULL OR local_update > anki_update
# step 6 check if record local_update is > integration table local_update
# step 7 export notes to anki
# - Use addNotes for new
# - Use updateNoteFields for updates
# step 8: Update local DB records
# - Set anki_id (if new)
# - Set anki_update = now()
# step 9: Update integration table with current timestamp
# step 10: Signal sync complete

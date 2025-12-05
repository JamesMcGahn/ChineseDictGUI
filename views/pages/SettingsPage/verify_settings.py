import os

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication

from base import QWidgetBase
from core.apple_note import AppleNoteImport
from models.dictionary import Word
from models.settings import AppSettingsModel, LogSettingsModel

# from services.audio import RemoveDuplicateAudioWorker, AudioThread
from services.audio import AudioThread
from services.network import NetworkWorker
from services.settings import AppSettings, SecureCredentials
from utils.files import RemoveFileWorker

from .page_settings_ui import PageSettingsUI


class VerifySettings(QWidgetBase):
    send_settings_verified = Signal(str)
    verify_response_update_ui = Signal(str, bool)
    send_settings_update = Signal(str)
    change_verify_btn_disable = Signal(str, bool)
    signal_request_line_value = Signal(str)  # key

    def __init__(self):
        super().__init__()

        self.running_tasks = {}
        self.settings = AppSettings()
        self.settings_model = AppSettingsModel()
        self.log_settings = LogSettingsModel()

        self.secure_creds = SecureCredentials()
        self.view = PageSettingsUI()
        self.home_directory = os.path.expanduser("~")
        print("home", self.home_directory)
        # self.get_settings("ALL", setText=True)

    def verify_settings(self, key, value=None):
        if key == "apple_note_name":
            self._verify_apple_note_name()
        elif key == "anki_words_deck_name" or key == "anki_sents_deck_name":
            self._verify_anki(key, {"action": "deckNames", "version": 6})
        elif key == "anki_sents_model_name" or key == "anki_words_model_name":
            self._verify_anki(key, {"action": "modelNames", "version": 6})
        elif key == "anki_user":
            self._verify_anki(key, {"action": "getProfiles", "version": 6})
        elif key == "google_api_key":
            self._verify_google_api_key()
        elif key == "anki_audio_path":
            self._verify_path_keys("anki_audio_path", value)
        elif key == "log_file_path":
            self._verify_path_keys("log_file_path", value)
        elif key == "log_backup_count":
            text = self.view.get_line_edit_text("log_backup_count")
            self.update_ui_verified("log_backup_count", text, "int")
        elif key == "log_file_name":
            text = self.view.get_line_edit_text("log_file_name")
            if not text.endswith(".log"):
                text = text + ".log"
            self.update_ui_verified("log_file_name", text)
        elif key == "log_file_max_mbs":
            text = self.view.get_line_edit_text("log_file_max_mbs")
            self.update_ui_verified("log_file_max_mbs", text, "int")
        elif key == "log_keep_files_days":
            text = self.view.get_line_edit_text("log_keep_files_days")
            self.update_ui_verified("log_keep_files_days", text, "int")
        elif key == "dictionary_source":
            text = self.view.get_combo_box_text("dictionary_source")
            self.update_ui_verified("dictionary_source", text)
        elif key == "merriam_webster_api_key":
            self._verify_merriam_webster_api_key()
        elif key == "auto_save_on_close":
            text = self.view.get_combo_box_text("auto_save_on_close")
            self.update_ui_verified("auto_save_on_close", text, "bool")

    def update_ui_verified(self, key, value, type="str"):
        self.settings_model.change_setting(key, value, True, type)
        self.verify_response_update_ui.emit(key, True)
        self.send_settings_update.emit(key)

    def run_network_check(self, key, url, json_data, success_cb=None, error_cb=None):
        network_thread = QThread()

        worker = NetworkWorker("GET", url, json=json_data, timeout=25)
        worker.moveToThread(network_thread)

        # Signal-Slot Connections
        worker.response_sig.connect(
            lambda: self.change_verify_btn_disable.emit(key, True)
        )
        if success_cb:
            worker.response_sig.connect(
                lambda success, response: success_cb(response, key)
            )
        if error_cb:
            worker.error_sig.connect(error_cb)
        network_thread.started.connect(worker.do_work)
        worker.finished.connect(lambda: self.cleanup_task(key))
        network_thread.finished.connect(lambda: self.cleanup_task(key, True))
        self.running_tasks[key] = (network_thread, worker)
        self.change_verify_btn_disable.emit(key, False)
        network_thread.start()

    def cleanup_task(self, task_id, thread_finished=False):
        if task_id in self.running_tasks:
            if thread_finished:
                w_thread, worker = self.running_tasks.pop(task_id)
                w_thread.deleteLater()
                print(f"Task {task_id} - Thread deleting.")
            else:
                w_thread, worker = self.running_tasks[task_id]
                worker.deleteLater()
                w_thread.quit()
                print(f"Task {task_id} - Worker cleaned up. Thread quitting.")

    def _verify_apple_note_name(self):
        self.change_verify_btn_disable.emit("apple_note_name", False)
        self.apple_note_thread = QThread(self)
        ui_note_name = self.view.get_line_edit_text("apple_note_name")
        self.apple_worker = AppleNoteImport(
            self.view.get_line_edit_text("apple_note_name")
        )
        self.running_tasks["apple_note_name"] = (
            self.apple_note_thread,
            self.apple_worker,
        )
        self.apple_worker.moveToThread(self.apple_note_thread)
        self.apple_worker.note_name_verified.connect(
            lambda response: self.response_update(
                ui_note_name if response else "", "apple_note_name", False
            )
        )
        self.apple_worker.finished.connect(lambda: self.cleanup_task("apple_note_name"))
        self.apple_note_thread.started.connect(self.apple_worker.verify_note_name)
        self.apple_note_thread.start()

    def _verify_anki(self, key, json_data):
        self.run_network_check(
            key,
            "http://127.0.0.1:8765/",
            json_data,
            self.response_update,
        )

    def _verify_google_api_key(self):

        self.audio_thread = AudioThread(
            [Word("test", "", "", "", "", 0)],
            folder_path="./",
            google_audio_credential=self.view.get_text_edit_text("google_api_key"),
        )

        self.audio_thread.updateAnkiAudio.connect(self.google_api_key_response)
        self.audio_thread.finished.connect(self.audio_thread.deleteLater)

        self.audio_thread.start()

    def _verify_path_keys(self, key, folder):

        isExist = os.path.exists(folder)
        if isExist:
            self.update_ui_verified(key, folder)

    def google_api_key_response(self, response):
        print()
        # success = response.status == Status.AUDIO
        if os.path.exists("./0.mp3"):

            self.response_update(
                "google_api_key",
                "google_api_key",
                False,
                "text_edit",
                override_check=True,
            )

            paths = ["./0.mp3"]
            self.removal_thread = QThread(self)
            self.removal_worker = RemoveFileWorker(paths)
            self.removal_worker.moveToThread(self.removal_thread)
            self.removal_thread.started.connect(self.removal_worker.do_work)
            self.removal_thread.finished.connect(self.removal_worker.deleteLater)
            self.removal_thread.finished.connect(self.removal_thread.deleteLater)
            self.removal_thread.start()

    def response_update(
        self, response, key, json_res=True, field_type="line_edit", override_check=False
    ):
        success = False
        value = ""

        if json_res:
            res = response.json()["result"]
        else:
            res = response
        print(res)
        if field_type == "line_edit":
            el = self.view.get_element("line_edit", key)
            value = el.text()
            if el and value in res:
                success = True
        elif field_type == "text_edit":
            el = self.view.get_element("text_edit", key)
            value = el.toPlainText()
            if el and el.toPlainText() in res:
                success = True

        if success or override_check:
            self.update_ui_verified(key, value)
        else:
            self.verify_response_update_ui.emit(key, False)

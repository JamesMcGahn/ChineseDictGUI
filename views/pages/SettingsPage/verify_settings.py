import os

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QApplication

from base import QSingleton, QWidgetBase
from core.apple_note import AppleNoteImport
from models.dictionary import Word
from models.settings import AppSettingsModel, LogSettingsModel

# from services.audio import RemoveDuplicateAudioWorker, AudioThread
from services.audio import AudioThread
from services.network import NetworkWorker
from services.settings import AppSettings, SecureCredentials
from utils.files import RemoveFileWorker

from .field_registry import FieldRegistry


class VerifySettings(QObject):
    verify_response_update_sui = Signal(str, str, bool)
    send_settings_update = Signal(str, str)
    change_verify_btn_disable = Signal(str, str, bool)

    def __init__(self):
        super().__init__()

        self.running_tasks = {}
        self.settings = AppSettings()
        self.settings_model = AppSettingsModel()
        self.log_settings = LogSettingsModel()
        self.field_registery = FieldRegistry()
        self.secure_creds = SecureCredentials()

        self.home_directory = os.path.expanduser("~")

    def verify_settings(self, tab, key, value=None):
        print("inn")

        if key == "apple_note_name":
            self._verify_apple_note_name(tab)
        elif key == "anki_words_deck_name" or key == "anki_sents_deck_name":
            self._verify_anki(tab, key, {"action": "deckNames", "version": 6})
        elif key == "anki_sents_model_name" or key == "anki_words_model_name":
            self._verify_anki(tab, key, {"action": "modelNames", "version": 6})
        elif key == "anki_user":
            self._verify_anki(tab, key, {"action": "getProfiles", "version": 6})
        elif key == "google_api_key":
            self._verify_google_api_key(tab)
        elif key == "anki_audio_path":
            self._verify_path_keys(tab, "anki_audio_path", value)
        elif key == "log_file_path":
            self._verify_path_keys(tab, "log_file_path", value)
        elif key == "log_backup_count":
            text = self.field_registery.get_line_edit_text("log_backup_count", tab)
            self.update_ui_verified(tab, "log_backup_count", text, "int")
        elif key == "log_file_name":
            text = self.field_registery.get_line_edit_text("log_file_name", tab)
            if not text.endswith(".log"):
                text = text + ".log"
            self.update_ui_verified(tab, "log_file_name", text)
        elif key == "log_file_max_mbs":
            text = self.field_registery.get_line_edit_text("log_file_max_mbs", tab)
            self.update_ui_verified(tab, "log_file_max_mbs", text, "int")
        elif key == "log_keep_files_days":
            text = self.field_registery.get_line_edit_text("log_keep_files_days", tab)
            self.update_ui_verified(tab, "log_keep_files_days", text, "int")
        elif key == "dictionary_source":
            text = self.field_registery.get_combo_box_text("dictionary_source", tab)
            self.update_ui_verified(tab, "dictionary_source", text)
        elif key == "merriam_webster_api_key":
            self._verify_merriam_webster_api_key()
        elif key == "auto_save_on_close":
            text = self.field_registery.get_combo_box_text("auto_save_on_close", tab)
            self.update_ui_verified(tab, "auto_save_on_close", text, "bool")

    def update_ui_verified(self, tab, key, value, type="str"):
        print("vverrr", tab, key, value)
        self.settings_model.change_setting(tab, key, value, True, type)
        self.verify_response_update_sui.emit(tab, key, True)
        self.send_settings_update.emit(tab, key)

    def run_network_check(
        self, tab, key, url, json_data, success_cb=None, error_cb=None
    ):
        network_thread = QThread()

        worker = NetworkWorker("GET", url, json=json_data, timeout=25)
        worker.moveToThread(network_thread)

        # Signal-Slot Connections
        worker.response_sig.connect(
            lambda: self.change_verify_btn_disable.emit(tab, key, True)
        )
        if success_cb:
            worker.response_sig.connect(
                lambda success, response: success_cb(response, tab, key)
            )
        if error_cb:
            worker.error_sig.connect(error_cb)
        network_thread.started.connect(worker.do_work)
        worker.finished.connect(lambda: self.cleanup_task(f"{tab}/{key}"))
        network_thread.finished.connect(lambda: self.cleanup_task(f"{tab}/{key}", True))
        self.running_tasks[f"{tab}/{key}"] = (network_thread, worker)
        self.change_verify_btn_disable.emit(tab, key, False)
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

    def _verify_apple_note_name(self, tab):
        self.change_verify_btn_disable.emit(tab, "apple_note_name", False)
        self.apple_note_thread = QThread(self)
        ui_note_name = self.field_registery.get_line_edit_text("apple_note_name", tab)
        self.apple_worker = AppleNoteImport(ui_note_name)
        self.running_tasks[f"{tab}/apple_note_name"] = (
            self.apple_note_thread,
            self.apple_worker,
        )
        self.apple_worker.moveToThread(self.apple_note_thread)
        self.apple_worker.note_name_verified.connect(
            lambda response: self.response_update(
                ui_note_name if response else "", tab, "apple_note_name", False
            )
        )
        self.apple_worker.finished.connect(
            lambda: self.cleanup_task(f"{tab}/apple_note_name")
        )
        self.apple_note_thread.started.connect(self.apple_worker.verify_note_name)
        self.apple_note_thread.start()

    def _verify_anki(self, tab, key, json_data):
        self.run_network_check(
            tab,
            key,
            "http://127.0.0.1:8765/",
            json_data,
            self.response_update,
        )

    def _verify_google_api_key(self, tab):

        self.audio_thread = AudioThread(
            [Word("test", "", "", "", "", 0)],
            folder_path="./",
            google_audio_credential=self.field_registery.get_text_edit_text(
                "google_api_key", tab
            ),
        )

        self.audio_thread.updateAnkiAudio.connect(
            lambda res: self.google_api_key_response(res, tab)
        )
        self.audio_thread.finished.connect(self.audio_thread.deleteLater)

        self.audio_thread.start()

    def _verify_path_keys(self, tab, key, folder):

        isExist = os.path.exists(folder)
        if isExist:
            self.update_ui_verified(tab, key, folder)

    def google_api_key_response(self, response, tab):
        print()
        # success = response.status == Status.AUDIO
        if os.path.exists("./0.mp3"):

            self.response_update(
                "google_api_key",
                tab,
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
        self,
        response,
        tab,
        key,
        json_res=True,
        field_type="line_edit",
        override_check=False,
    ):
        success = False
        value = ""

        if json_res:
            res = response.json()["result"]
        else:
            res = response
        print(res)
        if field_type == "line_edit":
            value = self.field_registery.get_line_edit_text(key, tab)

            if value in res:
                success = True
        elif field_type == "text_edit":
            value = self.field_registery.get_text_edit_text(key, tab)

            if value in res:
                success = True

        if success or override_check:
            self.update_ui_verified(tab, key, value)
        else:
            self.verify_response_update_sui.emit(tab, key, False)

import os

from PySide6.QtCore import QTimer, Signal, Slot

from base import QWidgetBase
from models.settings import AppSettingsModel, LogSettingsModel
from services.settings import AppSettings, SecureCredentials

from .page_settings_ui import PageSettingsUI
from .verify_settings import VerifySettings


class PageSettings(QWidgetBase):
    main_app_settings = Signal(bool, bool)
    import_page_settings = Signal(str, bool)
    audio_page_settings = Signal(str, bool, str, bool)
    sync_page_settings = Signal(str, bool, str, bool)
    log_page_settings = Signal(str, bool, str, bool)
    define_page_settings = Signal(str, bool, str, bool)
    save_log_settings_model = Signal(str, str, int, int, int, bool)
    verify_response_update_ui = Signal(str, bool)
    handle_change_update_ui = Signal(str)
    change_verify_btn_disable = Signal(str, bool)

    def __init__(self):
        super().__init__()

        self.view = PageSettingsUI()
        self.setLayout(self.view.layout())
        self.verify_settings = VerifySettings()
        self.running_tasks = {}
        self.settings = AppSettings()
        self.settings_model = AppSettingsModel()
        self.log_settings = LogSettingsModel()

        self.secure_creds = SecureCredentials()
        self.timers = {}
        self.home_directory = os.path.expanduser("~")
        print("home", self.home_directory)
        # self.get_settings("ALL", setText=True)

        self.save_log_settings_model.connect(self.log_settings.save_log_settings)

        self.view.btn_apple_note_name_verify.clicked.connect(
            lambda: self.handle_verify("apple_note_name")
        )
        self.view.btn_anki_words_deck_name_verify.clicked.connect(
            lambda: self.handle_verify("anki_words_deck_name")
        )
        self.view.btn_anki_sents_deck_name_verify.clicked.connect(
            lambda: self.handle_verify("anki_sents_deck_name")
        )
        self.view.btn_anki_words_model_name_verify.clicked.connect(
            lambda: self.handle_verify("anki_words_model_name")
        )
        self.view.btn_anki_sents_model_name_verify.clicked.connect(
            lambda: self.handle_verify("anki_sents_model_name")
        )
        self.view.btn_anki_user_verify.clicked.connect(
            lambda: self.handle_verify("anki_user")
        )
        self.view.btn_google_api_key_verify.clicked.connect(
            lambda: self.handle_verify("google_api_key")
        )
        self.view.btn_log_file_name_verify.clicked.connect(
            lambda: self.handle_verify("log_file_name")
        )
        self.view.btn_log_backup_count_verify.clicked.connect(
            lambda: self.handle_verify("log_backup_count")
        )
        self.view.btn_log_file_max_mbs_verify.clicked.connect(
            lambda: self.handle_verify("log_file_max_mbs")
        )
        self.view.btn_log_keep_files_days_verify.clicked.connect(
            lambda: self.handle_verify("log_keep_files_days")
        )
        self.view.btn_dictionary_source_verify.clicked.connect(
            lambda: self.handle_verify("dictionary_source")
        )
        self.view.btn_auto_save_on_close_verify.clicked.connect(
            lambda: self.handle_verify("auto_save_on_close")
        )

        self.view.comboBox_dictionary_source.currentIndexChanged.connect(
            lambda index, sender=self.view.comboBox_dictionary_source, key="dictionary_source": self.onComboBox_changed(
                index, sender, key
            )
        )
        self.view.comboBox_auto_save_on_close.currentIndexChanged.connect(
            lambda index, sender=self.view.comboBox_auto_save_on_close, key="auto_save_on_close", type="bool": self.onComboBox_changed(
                index, sender, key, type
            )
        )

        self.line_edit_connections = [
            (self.view.lineEdit_apple_note_name, "apple_note_name", "str"),
            (self.view.lineEdit_anki_sents_deck_name, "anki_sents_deck_name", "str"),
            (self.view.lineEdit_anki_sents_model_name, "anki_sents_model_name", "str"),
            (self.view.lineEdit_anki_words_deck_name, "anki_words_deck_name", "str"),
            (self.view.lineEdit_anki_words_model_name, "anki_words_model_name", "str"),
            (self.view.lineEdit_anki_user, "anki_user", "str"),
            (self.view.lineEdit_anki_audio_path, "anki_audio_path", "str"),
            (self.view.lineEdit_log_file_path, "log_file_path", "str"),
            (self.view.lineEdit_log_file_name, "log_file_name", "str"),
            (self.view.lineEdit_log_backup_count, "log_backup_count", "int"),
            (self.view.lineEdit_log_file_max_mbs, "log_file_max_mbs", "int"),
            (self.view.lineEdit_log_keep_files_days, "log_keep_files_days", "int"),
        ]
        # self.view.lineEdit_merriam_webster_api_key.textChanged.connect(
        #     lambda text, key="merriam_webster_api_key", field=self.view.lineEdit_merriam_webster_api_key: self.handle_secure_text_change_timer(
        #         text, key, field
        #     )
        # )
        self.setup_text_changed_connections()
        self.verify_settings.verify_response_update_ui.connect(
            self.view.verify_response_update
        )
        self.verify_settings.send_settings_update.connect(self.send_settings_update)
        self.handle_change_update_ui.connect(self.view.handle_setting_change_update)
        self.verify_settings.change_verify_btn_disable.connect(
            self.view.set_verify_btn_disable
        )
        self.view.folder_submit.connect(self.folder_change)
        self.view.secure_setting_change.connect(self.handle_secure_setting_change)

    def setup_text_changed_connections(self):
        for item in self.line_edit_connections:
            line_edit, key, field_type = item
            print(line_edit, key, field_type)

            el = self.view.get_element("line_edit", key)
            el.textChanged.connect(
                lambda word, key=key, field_type=field_type: self.handle_text_change_timer(
                    key=key, text=word, field_type=field_type
                )
            )

    def handle_text_change_timer(self, key, text, field_type):
        if key in self.timers:
            self.timers[key].stop()

        self.timers[key] = QTimer(self)
        self.timers[key].setSingleShot(True)
        self.timers[key].timeout.connect(
            lambda: self.handle_setting_change(key, text, field_type)
        )

        self.timers[key].start(500)

    def handle_user_done_typing(self, key, field):
        text = field.text()
        self.handle_secure_setting_change(key, text)

    def handle_secure_text_change_timer(self, text, key, field):
        if key not in self.timers:
            self.timers[key] = QTimer()
            self.timers[key].setSingleShot(True)
            self.timers[key].timeout.connect(
                lambda: self.handle_secure_user_done_typing(key, field)
            )

        self.timers[key].start(1000)

    def handle_secure_user_done_typing(self, key, field):
        text = field.text()
        self.handle_secure_setting_change(key, text)

    def onComboBox_changed(self, index, sender, key, field_type="str"):
        selected_text = sender.currentText()
        print("currentText", selected_text)
        self.handle_setting_change(key, selected_text, field_type)

    def handle_setting_change(self, field, word, field_type="str"):
        """
        Handles the setting change: saves the new value and updates the icon.

        Args:
            field (str): The field name for the setting.
            word (str): The new value of the setting.
            icon_label (QLabel): The icon label to update.
        """

        self.settings_model.change_setting(field, word, type=field_type)
        self.handle_change_update_ui.emit(field)

    @Slot(str, str)
    def handle_secure_setting_change(self, field, word):
        self.settings_model.change_secure_setting(
            field,
            word,
        )
        self.handle_change_update_ui.emit(field)

    def handle_verify(self, key):
        self.verify_settings.verify_settings(key)

    @Slot(str, str)
    def folder_change(self, key, folder):
        self.verify_settings.verify_settings(key, folder)

    def send_settings_update(self, key):

        # Import Page settings
        if key in ["apple_note_name"]:
            self.send_import_page_settings()
        elif key in ["audio_path", "google_api_key"]:
            self.send_audio_page_settings()
        elif key in ["anki_deck_name", "anki_model_name"]:
            self.send_sync_page_settings()
        elif key in [
            "log_file_path",
            "log_file_name",
            "log_backup_count",
            "log_file_max_mbs",
            "log_keep_files_days",
        ]:
            self.send_logs_page_setting()
        elif key in ["dictionary_source", "merriam_webster_api_key"]:
            self.send_define_page_settings()
        elif key in ["auto_save_on_close"]:
            self.main_app_settings()

    def send_main_app_settings(self):
        auto_save_on_close, auto_save_on_close_verifed = (
            self.settings_model.get_setting("auto_save_on_close")
        )
        self.main_app_settings.emit(auto_save_on_close, auto_save_on_close_verifed)

    def send_define_page_settings(self):
        dictionary_source, dict_source_verifed = self.settings_model.get_setting(
            "dictionary_source"
        )
        merriam_webster_api_key, merriam_webster_verifed = (
            self.settings_model.get_setting("merriam_webster_api_key")
        )

        self.define_page_settings.emit(
            dictionary_source,
            dict_source_verifed,
            merriam_webster_api_key,
            merriam_webster_verifed,
        )

    def send_import_page_settings(self):
        apple_note_name, ann_verifed = self.settings_model.get_setting(
            "apple_note_name"
        )
        self.import_page_settings.emit(apple_note_name, ann_verifed)

    def send_audio_page_settings(self):
        google_api_key, gak_verifed = self.settings_model.get_setting("google_api_key")
        anki_audio_path, aap_verifed = self.settings_model.get_setting(
            "anki_audio_path"
        )

        self.audio_page_settings.emit(
            google_api_key,
            gak_verifed,
            anki_audio_path,
            aap_verifed,
        )

    def send_sync_page_settings(self):
        anki_deck_name, adn_verifed = self.settings_model.get_setting("anki_deck_name")
        anki_model_name, amn_verifed = self.settings_model.get_setting(
            "anki_model_name"
        )

        self.sync_page_settings.emit(
            anki_deck_name, adn_verifed, anki_model_name, amn_verifed
        )

    def send_logs_page_setting(self):
        log_file_path, lfp_verifed = self.settings_model.get_setting("log_file_path")
        log_file_name, lfn_verifed = self.settings_model.get_setting("log_file_name")
        log_file_max_mbs, _ = self.settings_model.get_setting("log_file_max_mbs")
        log_backup_count, _ = self.settings_model.get_setting("log_backup_count")
        log_keep_files_days, _ = self.settings_model.get_setting("log_keep_files_days")

        self.log_page_settings.emit(
            log_file_path,
            lfp_verifed,
            log_file_name,
            lfn_verifed,
        )
        self.save_log_settings_model.emit(
            log_file_path,
            log_file_name,
            log_file_max_mbs,
            log_backup_count,
            log_keep_files_days,
            False,
        )

    @Slot()
    def send_all_settings(self):
        print("send all settings")
        self.send_import_page_settings()
        self.send_audio_page_settings()
        self.send_sync_page_settings()
        self.send_logs_page_setting()
        self.send_define_page_settings()
        self.send_main_app_settings()


# import os

# from PySide6.QtCore import Signal
# from PySide6.QtWidgets import QVBoxLayout

# from base import QWidgetBase
# from components.toasts import QToast
# from core.anki_integration.imports import (
#     AnkiInitialImportThread,
#     AnkiSyncExportThread,
#     AnkiSyncImportThread,
# )
# from services.network import NetworkThread
# from services.settings import AppSettings

# from .page_settings_ui import PageSettingsUI


# class PageSettings(QWidgetBase):
#     md_multi_selection_sig = Signal(int)
#     use_cpod_def_sig = Signal(bool)
#     updated_sents_levels_sig = Signal(bool, list)

#     def __init__(self):

#         super().__init__()
#         self.setObjectName("settings_page")
#         module_dir = os.path.dirname(os.path.realpath(__file__))
#         file_path = os.path.join(module_dir, "settings.css")
#         with open(file_path, "r") as ss:
#             self.setStyleSheet(ss.read())
#         self.ui = PageSettingsUI()
#         wrap = QVBoxLayout(self)
#         wrap.setContentsMargins(0, 0, 0, 0)
#         wrap.addWidget(self.ui)

#         self.settings = AppSettings()
#         # self.ui.import_deck_btn.clicked.connect(self.import_anki_deck)

#         # self.get_deck_names()

#         # self.ui.lineEdit_anki_sents_deck.textChanged.connect(
#         #     lambda word, caller="sents": self.change_deck_names(word, caller)
#         # )
#         # self.ui.lineEdit_anki_words_deck.textChanged.connect(
#         #     lambda word, caller="words": self.change_deck_names(word, caller)
#         # )

#         # self.ui.label_anki_sents_verify_btn.clicked.connect(
#         #     lambda checked, caller="sents": self.clicked_verify_deck_names(
#         #         checked, caller
#         #     )
#         # )
#         # self.ui.label_anki_words_verify_btn.clicked.connect(
#         #     lambda checked, caller="words": self.clicked_verify_deck_names(
#         #         checked, caller
#         #     )
#         # )

#         # self.ui.sync_import_btn.clicked.connect(self.anki_sync_import)
#         # self.ui.sync_export_btn.clicked.connect(self.anki_sync_export)

#     def get_deck_names(self):
#         self.settings.begin_group("deckNames")
#         self.sents_deck = self.settings.get_value("sents", "")
#         self.words_deck = self.settings.get_value("words", "")
#         self.ui.lineEdit_anki_sents_deck.setText(self.sents_deck)
#         self.ui.lineEdit_anki_words_deck.setText(self.words_deck)
#         self.words_verified = self.settings.get_value("words-verified", False)
#         self.sents_verified = self.settings.get_value("sents-verified", False)

#         self.ui.label_anki_words_deck_verfied.setIcon(
#             self.ui.check_icon if self.words_verified else self.ui.x_icon
#         )
#         self.ui.label_anki_sents_deck_verfied.setIcon(
#             self.ui.check_icon if self.sents_verified else self.ui.x_icon
#         )

#         self.ui.label_anki_sents_verify_btn.setDisabled(self.sents_verified)
#         self.ui.label_anki_words_verify_btn.setDisabled(self.words_verified)

#         self.settings.end_group()

#     def change_deck_names(self, deckName, caller, verified=False):
#         self.settings.begin_group("deckNames")
#         self.settings.set_value(caller, deckName)
#         self.settings.set_value(f"{caller}-verified", verified)
#         self.settings.end_group()
#         self.get_deck_names()

#     def import_anki_deck(self):
#         self.import_anki_w = AnkiInitialImportThread("Mandarin Words", "words")
#         self.import_anki_w.start()
#         self.import_anki_w.finished.connect(self.import_anki_sents)

#     # # TODO: Refesh dictionary view when loaded
#     # # TODO: Remove threads
#     def import_anki_sents(self):
#         self.import_anki_s = AnkiInitialImportThread("Mandarin 10k Sentences", "sents")
#         self.import_anki_s.start()

#     def clicked_verify_deck_names(self, _, caller):
#         print("sss", caller)
#         json = {"action": "deckNames", "version": 6}
#         self.net_thread = NetworkThread("GET", "http://127.0.0.1:8765/", json=json)
#         self.net_thread.response_sig.connect(
#             lambda status, response, errorType=None, caller=caller: self.verify_decks_response(
#                 status, response, errorType, caller
#             )
#         )
#         self.net_thread.error_sig.connect(
#             lambda status, err, errorType, caller=caller: self.verify_decks_response(
#                 status, err, errorType, caller
#             )
#         )
#         self.net_thread.finished.connect(self.net_thread.deleteLater)
#         self.net_thread.start()

#     def verify_decks_response(self, status, response, errorType, caller):
#         if status == "success":
#             response = response.json()
#             deckName = self.settings.get_value(f"deckNames/{caller}", None)
#             if deckName in response["result"]:
#                 self.change_deck_names(deckName, caller, True)
#                 QToast(
#                     self,
#                     "success",
#                     "Deck Name Verified",
#                     "Deck Name found in Anki, verify all decks and then start the integration!",
#                 ).show()
#             else:
#                 QToast(
#                     self,
#                     "error",
#                     "Deck Name Not Found",
#                     "Deck Name not found in Anki, please make sure you have it typed correctly.",
#                 ).show()
#         else:
#             QToast(
#                 self,
#                 "error",
#                 "Anki API Error",
#                 "Make sure that you have Anki Opened",
#             ).show()

#     def anki_sync_import(self):
#         if (
#             self.sents_deck
#             and self.words_deck
#             and self.words_verified
#             and self.sents_verified
#         ):
#             self.sync_thread = AnkiSyncImportThread(self.words_deck, self.sents_deck)
#             self.sync_thread.start()
#             print("Sync Import")

#     def anki_sync_export(self):
#         if (
#             self.sents_deck
#             and self.words_deck
#             and self.words_verified
#             and self.sents_verified
#         ):
#             self.sync_thread = AnkiSyncExportThread(self.words_deck, self.sents_deck)
#             self.sync_thread.start()
#             print("Sync Import")

import time

from PySide6.QtCore import Signal, Slot

from base import QWidgetBase
from base.enums import UIEVENTTYPE
from base.events import SentencesEvent, ToastEvent, UIEvent, WordsEvent
from components.dialogs import (
    AddLessonsDialog,
)
from context import AppContext
from controllers.models import ImportPageControllers
from db import DatabaseManager, DatabaseQueryThread
from models.table import SentenceTableModel, WordTableModel

from .page_lessons_ui import PageLessonsView

# TODO: CLEAN UP : Remove OLD DB ACCESS
# TODO: Remove AppContext
# TODO Remove Logic -> Implement Controller


class PageLessons(QWidgetBase):
    md_multi_selection_sig = Signal(int)
    use_cpod_def_sig = Signal(bool)
    updated_sents_levels_sig = Signal(bool, list)
    set_button_disabled = Signal(bool)

    def __init__(self, controllers: ImportPageControllers):
        super().__init__()
        self.controllers = controllers
        self.ui = PageLessonsView()
        self.ctx = AppContext()

        # self.ctx.lesson_pipeline_manager.scraping_active.connect(
        #     self.set_button_disabled
        # )
        self.controllers.lessons.ui_event.connect(self.handle_ui_event)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.ui)

        self.setObjectName("lessons_page")
        self.check_for_dups = False

        self.table_wordmodel = WordTableModel()
        self.table_sentmodel = SentenceTableModel()
        self.ui.table_view_s.setModel(self.table_sentmodel)
        self.ui.table_view_w.setModel(self.table_wordmodel)
        self.dialog = AddLessonsDialog()
        self.dialog.add_lesson_submited_signal.connect(self.get_dialog_submitted)

        self.ui.stacked_widget.setCurrentIndex(1)
        self.ui.import_button.clicked.connect(self.handle_import_button_clicked)

        self.ui.words_table_btn.clicked.connect(self.change_table)
        self.ui.sents_table_btn.clicked.connect(self.change_table)
        self.ui.save_btn_words.clicked.connect(self.save_selected_words)
        self.ui.save_btn_sents.clicked.connect(self.save_selected_sents)
        self.ui.select_all_w.clicked.connect(self.select_all_words)
        self.ui.select_all_s.clicked.connect(self.select_all_sents)
        self.ui.clear_w.clicked.connect(self.clear_table_words)
        self.ui.clear_s.clicked.connect(self.clear_table_sents)
        self.set_button_disabled.connect(self.ui.set_import_btn)

        self.appshutdown.connect(lambda: print("app shutdown lesson"))
        self.dbw = DatabaseManager("chineseDict.db")
        self.dbs = DatabaseManager("chineseDict.db")

    def select_all_words(self):
        self.ui.table_view_w.selectAll()

    def select_all_sents(self):
        self.ui.table_view_s.selectAll()

    def clear_table_words(self):
        self.select_all_words()
        selection_model = self.ui.table_view_w.selectionModel()
        selected_rows = selection_model.selectedRows()
        self.table_wordmodel.remove_selected(selected_rows)

    def clear_table_sents(self):
        self.select_all_sents()
        selection_model = self.ui.table_view_s.selectionModel()
        selected_rows = selection_model.selectedRows()
        self.table_sentmodel.remove_selected(selected_rows)

    def save_selected_words(self):
        selection_model = self.ui.table_view_w.selectionModel()
        selected_rows = selection_model.selectedRows()
        words = [
            self.table_wordmodel.get_row_data(index.row()) for index in selected_rows
        ]
        for word in words:
            word.local_update = int(time.time())

        self.save_selwords = DatabaseQueryThread("words", "insert_words", words=words)
        self.save_selwords.start()
        self.table_wordmodel.remove_selected(selected_rows)
        self.save_selwords.result.connect(
            self.ctx.audio_n_whisper_manager.download_audio
        )

    def save_selected_sents(self):
        selection_model = self.ui.table_view_s.selectionModel()
        selected_rows = selection_model.selectedRows()

        sents = []
        for index in selected_rows:
            save_sent = self.table_sentmodel.get_row_data(index.row())
            save_sent.local_update = int(time.time())
            sents.append(save_sent)

        print("aaaaa", sents)

        self.save_selsents = DatabaseQueryThread(
            "sents", "insert_sentences", sentences=sents
        )
        self.save_selsents.start()
        self.table_sentmodel.remove_selected(selected_rows)
        self.save_selsents.result.connect(
            self.ctx.audio_n_whisper_manager.download_audio
        )
        self.save_selsents.finished.connect(self.save_selsents.deleteLater)

    def change_table(self):
        btn_name = self.sender().objectName()

        if btn_name == "words_table_btn":
            self.ui.stacked_widget.setCurrentIndex(0)
        else:
            self.ui.stacked_widget.setCurrentIndex(1)

    @Slot(object)
    def handle_ui_event(self, event: UIEvent):
        if event.event_type == UIEVENTTYPE.DISPLAY:
            if isinstance(event.payload, WordsEvent):
                [self.table_wordmodel.add_word(x) for x in event.payload.words]
                return
            if isinstance(event.payload, SentencesEvent):
                [self.table_sentmodel.add_sentence(x) for x in event.payload.sentences]
                return
            if isinstance(event.payload, ToastEvent):
                e = event.payload
                self.log_with_toast(
                    parent=self,
                    toast_title=e.title,
                    msg=e.message,
                    log_level=e.log_level,
                    toast_level=e.toast_level,
                )

    @Slot(list)
    def get_dialog_submitted(self, form_data):
        self.logging(f"Received {len(form_data)} Lessons", "INFO")
        self.controllers.lessons.add_to_lesson_queue(form_data)

    def handle_import_button_clicked(self):
        self.dialog.exec()

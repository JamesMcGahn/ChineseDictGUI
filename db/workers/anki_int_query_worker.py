import sqlite3

from PySide6.QtCore import QObject, Signal, Slot

from ..dals import AnkiIntegrationDAL


class AnkiIntQueryWorker(QObject):
    finished = Signal()
    error_occurred = Signal(str)
    message = Signal(str)
    result = Signal(object)

    def __init__(self, db_manager, operation, **kwargs):
        super().__init__()
        self.db_manager = db_manager
        self.operation = operation
        self.kwargs = kwargs

    @Slot()
    def do_work(self):
        self.db_manager.connect()
        self.dala = AnkiIntegrationDAL(self.db_manager)
        try:
            match (self.operation):
                case "update_integration":
                    self.handle_update_integration()

        except sqlite3.Error as e:
            self.db_manager.rollback_transaction()
            print(e)
            self.error_occurred.emit(f"An error occurred: {e}")

        except Exception as e:
            print(e)
            self.error_occurred.emit(f"An error occurred: {e}")
        finally:
            self.db_manager.disconnect()
            self.finished.emit()

    def handle_update_integration(self):
        updates = self.kwargs.get("updates", None)
        if updates is None:
            raise ValueError("updates must be specified as kwarg")
        self.db_manager.begin_transaction()
        self.dala.update_anki_integration(updates)
        self.db_manager.commit_transaction()

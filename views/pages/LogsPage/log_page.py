from PySide6.QtCore import Slot
from PySide6.QtWidgets import QScrollArea, QTextEdit, QVBoxLayout

from base import QWidgetBase


class PageLogs(QWidgetBase):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the UI components of the log page, including the layout and
        the text display for logs.

        Returns:
            None: This function does not return a value.
        """
        self.log_file_path = None
        self.log_file_path_verified = False
        self.log_file_name = None
        self.log_file_name_verified = False

        self.settings_layout = QVBoxLayout(self)

        # Text edit widget for displaying logs
        self.log_display = QTextEdit()
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self.logger.send_log.connect(self.update_log_display)
        # Scroll area for the log display
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.log_display)
        scroll_area.setMinimumWidth(500)
        # scroll_area.setStyleSheet(SCROLL_AREA_STYLES)
        self.settings_layout.addWidget(scroll_area)

    def load_all_logs(self):
        self.log_display.setText("")
        try:
            print("here")
            with open(self.log_file_path + self.log_file_name, "r") as file:
                for line in file:
                    self.log_display.append(line.strip())
        except FileNotFoundError:
            print(
                f"Error: The file '{self.log_file_path + self.log_file_name}' was not found."
            )
        except IOError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def update_log_display(self, log: str) -> None:
        """
        Appends a new log entry to the log display.

        Args:
            log (str): The log entry to be appended.

        Returns:
            None: This function does not return a value.
        """
        self.log_display.append(log)

    @Slot(str, bool, str, bool)
    def receive_settings_update(
        self,
        log_file_path,
        log_file_path_verified,
        log_file_name,
        log_file_name_verified,
    ):

        self.log_file_path = log_file_path
        self.log_file_path_verified = log_file_path_verified
        self.log_file_name = log_file_name
        self.log_file_name_verified = log_file_name_verified
        if (
            log_file_path
            and log_file_path_verified
            and log_file_name
            and log_file_name_verified
        ):
            self.load_all_logs()

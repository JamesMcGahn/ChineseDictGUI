from dataclasses import dataclass

from .settings_helper import setting


@dataclass
class LogSettings:
    log_file_path: str = setting(
        key="log_file_path",
        default="./logs/",
        category="log_settings",
        widget_type="line_edit",
        label_text="Log File path:",
        verify_btn_text="Verify Log Path",
        secure=False,
        folder_icon=True,
        verify=None,
    )
    log_file_name: str = setting(
        key="log_file_name",
        default="application.log",
        category="log_settings",
        widget_type="line_edit",
        label_text="Log File Name:",
        verify_btn_text="Save Log File Name",
        secure=False,
        folder_icon=True,
        verify=None,
    )
    log_file_max_mbs: int = setting(
        key="log_file_max_mbs",
        default=5,
        category="log_settings",
        widget_type="line_edit",
        label_text="Log File Max Mbs:",
        verify_btn_text="Save Log File Max Mbs",
        secure=False,
        folder_icon=False,
        verify=None,
    )
    log_keep_files_days: int = setting(
        key="log_keep_files_days",
        default=5,
        category="log_settings",
        widget_type="line_edit",
        label_text="Keep Log File Days:",
        verify_btn_text="Save Log File Days",
        secure=False,
        folder_icon=False,
        verify=None,
    )
    log_backup_count: int = setting(
        key="log_backup_count",
        default=5,
        category="log_settings",
        widget_type="line_edit",
        label_text="Log Backup Count:",
        verify_btn_text="Save Log Backup Count",
        secure=False,
        folder_icon=False,
        verify=None,
    )
    log_level: str = setting(
        key="log_level",
        default="INFO",
        category="log_settings",
        widget_type="combo_box",
        label_text="Log Level:",
        verify_btn_text="Save Log Level",
        secure=False,
        combo_box=["INFO", "WARN", "DEBUG", "ERROR"],
        verify=None,
    )

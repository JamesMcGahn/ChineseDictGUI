from dataclasses import dataclass
from typing import ClassVar

from ..enums import SETTINGSCATEGORIES, SETTINGSWIDGETTYPE
from ..validators.log_validators import (
    validate_log_backup_count,
    validate_log_file_max_mbs,
    validate_log_file_name,
    validate_log_file_path,
    validate_log_keep_files_days,
    validate_log_level,
    validate_log_print_logs,
)
from .base_category_map import SettingsCategoryBase
from .settings_field_helper import setting


@dataclass
class LogSettings(SettingsCategoryBase):
    schema_name: ClassVar[str] = SETTINGSCATEGORIES.LOG
    display_name: ClassVar[str] = "Log Settings"
    log_file_path: str = setting(
        key="log_file_path",
        default="./logs/",
        category=SETTINGSCATEGORIES.LOG,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Log File path:",
        verify_btn_text="Verify Log Path",
        secure=False,
        folder_icon=True,
        verify=validate_log_file_path,
    )
    log_file_name: str = setting(
        key="log_file_name",
        default="application.log",
        category=SETTINGSCATEGORIES.LOG,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Log File Name:",
        verify_btn_text="Save Log File Name",
        secure=False,
        folder_icon=False,
        verify=validate_log_file_name,
    )
    log_file_max_mbs: int = setting(
        key="log_file_max_mbs",
        default=5,
        category=SETTINGSCATEGORIES.LOG,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Log File Max Mbs:",
        verify_btn_text="Save Log File Max Mbs",
        secure=False,
        folder_icon=False,
        verify=validate_log_file_max_mbs,
    )
    log_keep_files_days: int = setting(
        key="log_keep_files_days",
        default=5,
        category=SETTINGSCATEGORIES.LOG,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Keep Log File Days:",
        verify_btn_text="Save Log File Days",
        secure=False,
        folder_icon=False,
        verify=validate_log_keep_files_days,
    )
    log_backup_count: int = setting(
        key="log_backup_count",
        default=5,
        category=SETTINGSCATEGORIES.LOG,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Log Backup Count:",
        verify_btn_text="Save Log Backup Count",
        secure=False,
        folder_icon=False,
        verify=validate_log_backup_count,
    )
    log_level: str = setting(
        key="log_level",
        default="INFO",
        category=SETTINGSCATEGORIES.LOG,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Log Level:",
        verify_btn_text="Save Log Level",
        secure=False,
        combo_box=["INFO", "WARN", "DEBUG", "ERROR"],
        verify=validate_log_level,
    )
    log_print_logs: str = setting(
        key="log_print_logs",
        default="True",
        category=SETTINGSCATEGORIES.LOG,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Print Logs:",
        verify_btn_text="Save Print Logs",
        secure=False,
        combo_box=["True", "False"],
        verify=validate_log_print_logs,
    )

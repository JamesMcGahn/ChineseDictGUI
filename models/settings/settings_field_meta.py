from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class SettingsFieldMeta:
    key: str
    label_text: str
    category: str
    widget_type: str
    verify_btn_text: str
    secure: bool = False
    folder_icon: bool = False
    combo_box: list[str] | None = None
    verify: Optional[Callable] = None

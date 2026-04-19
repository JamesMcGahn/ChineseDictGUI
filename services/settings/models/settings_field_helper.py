from dataclasses import field
from typing import Callable, Optional

from ..enums import SETTINGSWIDGETTYPE
from .settings_field_meta import SettingsFieldMeta


def setting(
    *,
    key: str,
    default: int | bool | str | float,
    category: str,
    widget_type: SETTINGSWIDGETTYPE,
    label_text: str,
    verify_btn_text: str,
    secure: bool = False,
    folder_icon: bool = False,
    combo_box: list[str] | None = None,
    verify: Optional[Callable] = None
):
    return field(
        default=default,
        metadata={
            "meta": SettingsFieldMeta(
                key=key,
                label_text=label_text,
                category=category,
                widget_type=widget_type,
                verify_btn_text=verify_btn_text,
                secure=secure,
                folder_icon=folder_icon,
                combo_box=combo_box,
                verify=verify,
            )
        },
    )

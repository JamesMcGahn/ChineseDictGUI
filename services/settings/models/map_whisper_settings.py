from dataclasses import dataclass
from typing import ClassVar

from services.audio.enums import WHISPERPROVIDER

from ..enums import SETTINGSCATEGORIES, SETTINGSWIDGETTYPE
from ..validators.whisper_validators import (
    validate_beam_size,
    validate_chunk_length,
    validate_compute_type,
    validate_initial_prompt,
    validate_min_silence_ms,
    validate_model,
    validate_on_multilingual,
    validate_on_previous_text,
    validate_vad_filter,
    validate_whisper_choice,
)
from .base_category_map import SettingsCategoryBase
from .settings_field_helper import setting


@dataclass
class WhisperSettings(SettingsCategoryBase):
    schema_name: ClassVar[str] = SETTINGSCATEGORIES.WHISPER
    display_name: ClassVar[str] = "Whisper Settings"
    whisper_choice: str = setting(
        key="whisper_choice",
        default=WHISPERPROVIDER.FASTER_WHISPER,
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Whisper Choice:",
        verify_btn_text="Save Whisper Choice",
        secure=False,
        combo_box=[WHISPERPROVIDER.FASTER_WHISPER, WHISPERPROVIDER.WHISPER],
        verify=validate_whisper_choice,
    )
    model: str = setting(
        key="model",
        default="large",
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Model Choice:",
        verify_btn_text="Save Model Choice",
        secure=False,
        combo_box=["medium", "large", "large-v2", "large-v3"],
        verify=validate_model,
    )
    beam_size: int = setting(
        key="beam_size",
        default=8,
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Model Choice:",
        verify_btn_text="Save Model Choice",
        secure=False,
        combo_box=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15],
        verify=validate_beam_size,
    )
    compute_type: str = setting(
        key="compute_type",
        default="auto",
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Compute Type:",
        verify_btn_text="Save Compute Type",
        secure=False,
        combo_box=[
            "auto",
            "int8",
            "int8_float32",
            "int8_float16",
            "int8_bfloat16",
            "int16",
            "float16",
            "float32",
            "bfloat16",
        ],
        verify=validate_compute_type,
    )
    vad_filter: bool = setting(
        key="vad_filter",
        default="False",
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Vad Filter:",
        verify_btn_text="Save Vad Filter",
        secure=False,
        combo_box=["True", "False"],
        verify=validate_vad_filter,
    )
    min_silence_ms: int = setting(
        key="min_silence_ms",
        default=2500,
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Minimum Silence:",
        verify_btn_text="Save Minimum Silence",
        secure=False,
        verify=validate_min_silence_ms,
    )
    chunk_length: int = setting(
        key="chunk_length",
        default=120,
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.LINE_EDIT,
        label_text="Chunk Length:",
        verify_btn_text="Save Chunk Length",
        secure=False,
        verify=validate_chunk_length,
    )
    on_previous_text: bool = setting(
        key="on_previous_text",
        default="True",
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="On Previous Text:",
        verify_btn_text="Save On Previous Text",
        secure=False,
        combo_box=["True", "False"],
        verify=validate_on_previous_text,
    )
    multilingual: bool = setting(
        key="multilingual",
        default="False",
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.COMBO_BOX,
        label_text="Multilingual:",
        verify_btn_text="Save Multilingual",
        secure=False,
        combo_box=["True", "False"],
        verify=validate_on_multilingual,
    )
    initial_prompt: str = setting(
        key="initial_prompt",
        default="Transcribe Mandarin in Simplified Chinese. Transcribe English in Standard English",
        category=SETTINGSCATEGORIES.WHISPER,
        widget_type=SETTINGSWIDGETTYPE.TEXT_EDIT,
        label_text="Save Initial Prompt:",
        verify_btn_text="Save Initial Prompt",
        secure=False,
        verify=validate_initial_prompt,
    )

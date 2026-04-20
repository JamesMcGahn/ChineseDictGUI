from ..enums import SETTINGSCATEGORIES
from .validator_helper import ValidatorHelper

helper = ValidatorHelper(SETTINGSCATEGORIES.WHISPER)


def validate_whisper_choice(field, value):
    return helper.settings_response(field, value, bool(value))


def validate_model(field, value):
    return helper.settings_response(field, value, bool(value))


def validate_beam_size(field, value):
    return helper.settings_response(
        field, value, helper.is_int(value) and int(value) > 0
    )


def validate_compute_type(field, value):
    return helper.settings_response(field, value, bool(value))


def validate_vad_filter(field, value):
    return helper.settings_response(field, value, True)


def validate_min_silence_ms(field, value):
    return helper.settings_response(
        field, value, helper.is_int(value) and int(value) > 0
    )


def validate_chunk_length(field, value):
    return helper.settings_response(
        field, value, helper.is_int(value) and int(value) > 0
    )


def validate_on_previous_text(field, value):
    return helper.settings_response(field, value, True)


def validate_on_multilingual(field, value):
    return helper.settings_response(field, value, True)


def validate_initial_prompt(field, value):
    return helper.settings_response(field, value, bool(value))

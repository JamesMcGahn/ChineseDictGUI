# patern validate_{field_name}
import os

from base.enums import LOGLEVEL
from services.validation.models import SettingsValidateResponse

from ..enums import SETTINGSCATEGORIES


def _response(field, is_valid):
    return SettingsValidateResponse(
        category=SETTINGSCATEGORIES.LOG, field=field, is_valid=is_valid
    )


def _is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def validate_log_file_path(field, value):
    _response(field, os.path.isdir(value))


def validate_log_file_name(field, value):
    _response(field, value.endswith(".log"))


def validate_log_file_max_mbs(field, value):
    _response(field, _is_int(value))


def validate_log_keep_files_days(field, value):
    _response(field, _is_int(value))


def validate_log_backup_count(field, value):
    _response(field, _is_int(value))


def validate_log_level(field, value):
    try:
        LOGLEVEL(value)
        return _response(field, True)
    except ValueError:
        return _response(field, False)

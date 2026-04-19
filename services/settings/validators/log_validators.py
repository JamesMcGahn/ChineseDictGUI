# patern validate_{field_name}
import os

from base.enums import LOGLEVEL

from ..enums import SETTINGSCATEGORIES
from .validator_helper import ValidatorHelper

helper = ValidatorHelper(SETTINGSCATEGORIES.LOG)


def validate_log_file_path(field, value):
    return helper.settings_response(field, os.path.isdir(value))


def validate_log_file_name(field, value):
    return helper.settings_response(field, value.endswith(".log"))


def validate_log_file_max_mbs(field, value):
    return helper.settings_response(field, helper.is_int(value) and value > 0)


def validate_log_keep_files_days(field, value):
    return helper.settings_response(field, helper.is_int(value))


def validate_log_backup_count(field, value):
    return helper.settings_response(field, helper.is_int(value))


def validate_log_level(field, value):
    try:
        LOGLEVEL(value)
        return helper.settings_response(field, True)
    except ValueError:
        return helper.settings_response(field, False)

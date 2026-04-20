# patern validate_{field_name}
import os

from base.enums import LOGLEVEL

from ..enums import SETTINGSCATEGORIES
from .validator_helper import ValidatorHelper

helper = ValidatorHelper(SETTINGSCATEGORIES.LOG)


def validate_log_file_path(field, value):
    return helper.settings_response(field, value, os.path.isdir(value))


def validate_log_file_name(field, value):
    return helper.settings_response(field, value, value.endswith(".log"))


def validate_log_file_max_mbs(field, value):
    return helper.settings_response(
        field, value, helper.is_int(value) and int(value) > 0
    )


def validate_log_keep_files_days(field, value):
    return helper.settings_response(field, value, helper.is_int(value))


def validate_log_backup_count(field, value):
    return helper.settings_response(field, value, helper.is_int(value))


def validate_log_level(field, value):
    try:
        LOGLEVEL(value)
        return helper.settings_response(field, value, True)
    except ValueError:
        return helper.settings_response(field, value, False)


def validate_log_print_logs(field, value):
    return helper.settings_response(field, value, True)

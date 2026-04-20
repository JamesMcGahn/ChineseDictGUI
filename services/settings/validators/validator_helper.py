from services.validation.models import SettingsValidateResponse

from ..enums import FIELDSTATESTATUS, SETTINGSCATEGORIES


class ValidatorHelper:

    def __init__(self, category: SETTINGSCATEGORIES):
        self.category = category

    def settings_response(self, field, value, is_valid, error_msg=None):
        if is_valid:
            display_field = field.replace("_", " ").title()
            msg = f"{display_field} is valid."
            status = FIELDSTATESTATUS.VALID
        else:
            status = FIELDSTATESTATUS.INVALID
            msg = error_msg
        return SettingsValidateResponse(
            category=self.category, field=field, value=value, status=status, message=msg
        )

    def is_int(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

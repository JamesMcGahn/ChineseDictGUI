from services.validation.models import SettingsValidateResponse

from ..enums import SETTINGSCATEGORIES


class ValidatorHelper:

    def __init__(self, category: SETTINGSCATEGORIES):
        self.category = category

    def settings_response(self, field, is_valid):
        return SettingsValidateResponse(
            category=self.category, field=field, is_valid=is_valid
        )

    def is_int(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

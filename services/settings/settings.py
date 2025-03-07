from typing import Any, Optional

from PySide6.QtCore import QSettings

from base import Singleton


class AppSettings(Singleton):
    """
    A singleton class for managing application settings using QSettings. It provides methods for storing,
    retrieving, and managing settings values across different groups.

    Attributes:
        _settings (QSettings): The QSettings instance that manages the key-value pairs for the application.

    Args:
        None
    """

    def __init__(self):
        """
        Initializes the AppSettings singleton with the QSettings instance for the application.
        """
        super().__init__()
        self._settings = QSettings("ChineseDict", "ChineseDictApp")

    def set_value(self, key: str, value: Optional[Any]) -> None:
        """
        Sets a key-value pair in the application settings.

        Args:
            key (str): The key to set the value for.
            value (any): The value to associate with the key.

        Returns:
            None: This function does not return a value.
        """
        self._settings.setValue(key, value)

    def get_value(
        self, key: str, default: Optional[Any] = None, type: Optional[Any] = None
    ):
        """
        Retrieves a value from the application settings.

        Args:
            key (str): The key to retrieve the value for.
            default (Optional[Any], optional): The default value if the key is not found. Defaults to None.
            type (Optional[Any], optional): The expected type for the value. Defaults to None.

        Returns:
            Any: The value associated with the key or the default value if the key is not found.
        """
        if type is not None:
            return self._settings.value(key, default, type=type)
        else:
            return self._settings.value(key, default)

    def begin_group(self, group: str) -> None:
        """
        Begins a new group in the settings, allowing related key-value pairs to be grouped together.

        Args:
            group (str): The group name.

        Returns:
            None: This function does not return a value.
        """
        self._settings.beginGroup(group)

    def end_group(self) -> None:
        """
        Ends the current group in the settings.

        Returns:
            None: This function does not return a value.
        """
        self._settings.endGroup()

    def remove(self, key: str) -> None:
        """
        Removes a key-value pair from the application settings.

        Args:
            key (str): The key to be removed.

        Returns:
            None: This function does not return a value.
        """
        self._settings.remove(key)

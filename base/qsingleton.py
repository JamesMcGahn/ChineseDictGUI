from typing import Any, Dict, Optional, Type

from PySide6.QtCore import QObject


class QSingleton(type(QObject), type):
    """
    A thread-safe singleton metaclass for QObject-based classes.

    This metaclass ensures that only one instance of a QObject-based class
    is created throughout the application's lifecycle.

    Attributes:
        _instance (Optional[QObject]): Stores the single instance of the class.
    """

    _instance: Optional[QObject] = None

    def __init__(
        cls: Type[QObject], name: str, bases: tuple, dict: Dict[str, Any]
    ) -> None:
        """
        Initialize the singleton class.

        Args:
            name (str): The name of the class being initialized.
            bases (tuple): The base classes of the class.
            dict (Dict[str, Any]): The class attributes dictionary.
        """
        super().__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls: Type[QObject], *args: Any, **kwargs: Any) -> QObject:
        """
        Return the single instance of the class.

        If the instance doesn't exist, create it and return the instance. Otherwise, return the existing instance.

        Args:
            *args: Positional arguments for the class instantiation.
            **kwargs: Keyword arguments for the class instantiation.

        Returns:
            QObject: The single instance of the class.
        """
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

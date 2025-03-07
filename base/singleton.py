from typing import Any, Dict


class Singleton(object):
    """
    A generic singleton class to ensure only one instance of a class is created.

    This class maintains a registry of class instances and ensures that only one instance
    of any class inheriting from Singleton is created.

    Attributes:
        _instances (Dict[type, object]): A dictionary to store the single instances of classes.
    """

    _instances: Dict[type, object] = {}

    def __new__(cls: type, *args: Any, **kwargs: Any) -> object:
        """
        Create or return the single instance of the class.

        If the class instance doesn't exist, create it and store it. Otherwise, return the existing instance.

        Args:
            *args: Positional arguments for the class instantiation.
            **kwargs: Keyword arguments for the class instantiation.

        Returns:
            object: The single instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]

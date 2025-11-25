import platform
from typing import Optional

import keyring
from keyring import get_keyring
from PySide6.QtCore import Signal, Slot

from base import QObjectBase, QSingleton


class SecureCredentials(QObjectBase, metaclass=QSingleton):
    """
    Manages the credentials for the application, handling saving, retrieval,
    and secure storage using keyring.


    Signals:
        success (Signal): Emitted after credentials are saved successfully.
    """

    success = Signal()
    error = Signal(str)

    def __init__(self):
        """
        Sets up the keyring backend based on the operating system and retrieves
        stored credentials from the application settings and keyring if available.
        """
        super().__init__()

        self.set_keyring_backend()

    def set_keyring_backend(self) -> None:
        """
        Configures the keyring backend based on the operating system. Windows and macOS
        have specific keyring backends set. Logs the current keyring backend or errors
        during setup.
        """
        try:
            get_keyring()
            self.logging("Current Keyring method: " + str(get_keyring()), "INFO")
            current_os = platform.system()

            if current_os == "Windows":
                keyring.core.set_keyring(
                    keyring.core.load_keyring(
                        "keyring.backends.Windows.WinVaultKeyring"
                    )
                )
                self.logging("Windows keyring backend set successfully.", "INFO")

            elif current_os == "Darwin":
                # Set the macOS Keychain as the backend
                keyring.core.set_keyring(
                    keyring.core.load_keyring("keyring.backends.macOS.Keyring")
                )
                self.logging("macOS keyring backend set successfully.", "INFO")

            else:
                self.logging(
                    "Unsupported operating system or no suitable backend found.",
                    "ERROR",
                )

        except Exception as e:
            self.logging(f"Error setting keyring backend: {e}", "ERROR")

    def get_creds(self, service_name: str, name_field: str) -> Optional[str]:
        """
        Retrieves the stored credential.
        Args:
            service_name (str): name of the service.
            name_field (str): name field.

        Returns:
            str: secure credential.
        """
        return keyring.get_password(service_name, name_field)

    @Slot(str, str, str)
    def save_creds(self, service_name: str, name_field: str, secure: str) -> None:
        """
        Saves the provided credentials to keyring .
        Emits success signal once the save operation is complete.

        Args:
            service_name (str): name of the service.
            name_field (str): name field.
            secure (str): secure field.

        Returns:
            None: This function does not return a value.
        """
        try:
            if service_name and name_field and secure:
                keyring.set_password(service_name, name_field, secure)
                self.logging("Saved Credentials to Keyring", "INFO")
                self.success.emit()
        except Exception as e:
            self.error.emit(f"Error occured saving secured credentials: {e}")
            self.logging(f"Error saving secure credentials: {e}")

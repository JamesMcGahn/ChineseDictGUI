import requests
from PySide6.QtCore import QThread, Signal


class NetworkThread(QThread):
    response_sig = Signal(str, object)
    error_sig = Signal(str, str)

    def __init__(self, session_mangager, operation, url, data=None):
        super().__init__()
        self.session_mangager = session_mangager
        self.url = url
        self.data = data
        self.operation = operation

    def run(self):
        try:
            if self.operation == "POST":
                response = self.session_mangager.post(self.url, data=self.data)

            elif self.operation == "SESSION":
                response = self.session_mangager.post(self.url, data=self.data)
                if not any(c.name == "lang" for c in response.cookies):
                    raise requests.exceptions.RequestException
                print("here1", response)
                print("here", response.text)

            if response.status_code in (200, 201):
                print("suc", response)
                self.response_sig.emit("success", response)
            else:
                self.error_sig.emit("success", response)
                print("suc2", response)

        except requests.exceptions.RequestException as e:
            print("eerr")
            print(e)
            self.error_sig.emit("error", str(e))

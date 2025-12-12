import threading

import requests
from PySide6.QtCore import QObject, QThread, Signal, Slot

from .session_manager import SessionManager


class NetworkWorker(QObject):
    finished = Signal()
    response_sig = Signal(str, object)
    error_sig = Signal(str, object, int)
    start_work = Signal()

    def __init__(
        self,
        operation,
        url,
        data=None,
        json=None,
        timeout=10,
        retry=0,
        headers=None,
    ):
        super().__init__()
        self.session_manager = SessionManager()
        self.url = url
        self.data = data
        self.operation = operation
        self.json = json
        self.timeout = timeout
        self.start_work.connect(self.do_work)
        self.retry = retry
        self.headers = headers

    @Slot()
    def do_work(self):
        print(
            f"Starting NetworkWorker in thread: {threading.get_ident()} - {self.thread()}"
        )

        try:
            if self.operation == "POST":
                response = self.session_manager.post(
                    self.url,
                    data=self.data,
                    json=self.json,
                    timeout=self.timeout,
                    headers=self.headers,
                )

                if response.status_code in (200, 201, 202, 203):
                    self.response_sig.emit("success", response)
                else:
                    self.error_sig.emit("error", response, response.status_code)

            elif self.operation == "SESSION":
                response = self.session_manager.post(
                    self.url, data=self.data, json=self.json, timeout=self.timeout
                )
                if not any(c.name == "lang" for c in response.cookies):
                    raise requests.exceptions.RequestException

            elif self.operation == "GET":
                print(f"getting {self.url}")

                for attempt in range(self.retry + 1):
                    response = self.operation_get()
                    if response.status_code in (200, 201):
                        self.response_sig.emit("success", response)
                        break
                    else:
                        if attempt < self.retry:
                            print(f"Retrying... ({attempt + 1}/{self.retry})")
                            continue
                        else:
                            print("status check - error", response)
                            self.error_sig.emit("error", response, response.status_code)

        except requests.exceptions.ConnectionError as e:
            # TODO - handle error
            print(e)
            self.error_sig.emit(
                "error", {"message": str(e)}, getattr(e.response, "status_code", 0)
            )

        except requests.exceptions.RequestException as e:
            print(e)
            # TODO - handle error

            self.error_sig.emit(
                "error", {"message": str(e)}, getattr(e.response, "status_code", 0)
            )

        finally:
            self.finished.emit()

    def operation_get(self):
        return self.session_manager.get(
            self.url,
            data=self.data,
            json=self.json,
            timeout=self.timeout,
            headers=self.headers,
        )

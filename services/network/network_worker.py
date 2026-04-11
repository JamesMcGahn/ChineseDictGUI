from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.network.session import BaseProviderSession

import requests
from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from models.services import NetworkResponse

from .session_manager import SessionManager


# TODO change finished signal to done
class NetworkWorker(QObjectBase):
    finished = Signal()
    response = Signal(object)
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
        files=None,
        session_provider: BaseProviderSession = None,
    ):
        super().__init__()
        # TODO remove session manager when fully moved over to session providerser
        self.session_provider = session_provider
        self.session_manager = SessionManager()
        self.url = url
        self.data = data
        self.operation = operation
        self.json = json
        self.timeout = timeout
        self.start_work.connect(self.do_work)
        self.retry = retry
        self.headers = headers
        self.files = files

    @Slot()
    def do_work(self):
        self.log_thread()

        try:
            if self.operation == "POST":
                for attempt in range(self.retry + 1):
                    res = self.operation_post()

                    if res.status_code in (200, 201, 202, 203):
                        if self.session_provider:
                            self.session_provider.update_cookies_from_res(res)
                        self.logging(
                            f"Received {res.status_code} response for POST to {self.url}",
                            "INFO",
                        )
                        self.response_sig.emit("success", res)
                        self.response.emit(
                            NetworkResponse(
                                ok=True,
                                status=res.status_code,
                                data=self.extract_payload(res),
                                message="success",
                                raw=res,
                            )
                        )
                        break
                    else:
                        self.logging(
                            f"Received {res.status_code} response for POST to {self.url}",
                            "WARN",
                        )
                        if attempt < self.retry:
                            print(f"Retrying... ({attempt + 1}/{self.retry})")
                            continue

                        self.error_sig.emit("error", res, res.status_code)
                        self.response.emit(
                            NetworkResponse(
                                ok=False,
                                status=res.status_code,
                                data=self.extract_payload(res),
                                message="error",
                                raw=res,
                            )
                        )

            elif self.operation == "GET":
                print(f"getting {self.url}")

                for attempt in range(self.retry + 1):
                    res = self.operation_get()
                    if res.status_code in (200, 201):
                        if self.session_provider:
                            self.session_provider.update_cookies_from_res(res)
                        self.logging(
                            f"Received {res.status_code} response for GET to {self.url}",
                            "INFO",
                        )
                        self.response_sig.emit("success", res)
                        self.response.emit(
                            NetworkResponse(
                                ok=True,
                                status=res.status_code,
                                data=self.extract_payload(res),
                                message="success",
                                raw=res,
                            )
                        )
                        break
                    else:
                        if attempt < self.retry:
                            print(f"Retrying... ({attempt + 1}/{self.retry})")
                            continue
                        else:
                            self.logging(
                                f"Received {res.status_code} response for POST to {self.url}",
                                "WARN",
                            )
                            self.error_sig.emit("error", res, res.status_code)
                            self.response.emit(
                                NetworkResponse(
                                    ok=False,
                                    status=res.status_code,
                                    data=self.extract_payload(res),
                                    message="error",
                                    raw=res,
                                )
                            )
        except requests.exceptions.ConnectionError as e:
            self.logging(
                f"Received Connection Error for POST to {self.url}",
                "ERROR",
            )
            self.error_sig.emit(
                "error", {"message": str(e)}, getattr(e.response, "status_code", 0)
            )
            self.response.emit(
                NetworkResponse(
                    ok=False,
                    status=0,
                    data=None,
                    message=f"error: {str(e)}",
                    raw=None,
                )
            )

        except requests.exceptions.RequestException as e:
            self.logging(
                f"Received Request Exception Error for POST to {self.url}: {e}",
                "ERROR",
            )

            self.error_sig.emit(
                "error", {"message": str(e)}, getattr(e.response, "status_code", 0)
            )
            self.response.emit(
                NetworkResponse(
                    ok=False,
                    status=0,
                    data=None,
                    message=f"error: {str(e)}",
                    raw=None,
                )
            )

        finally:
            self.finished.emit()

    # TODO remove session manager when fully moved over to session provider
    def operation_post(self):
        if self.session_provider:
            session = self.session_provider.build_session()
            return session.post(
                self.url,
                data=self.data,
                json=self.json,
                timeout=self.timeout,
                headers=self.headers,
                files=self.files,
            )
        else:
            return self.session_manager.post(
                self.url,
                data=self.data,
                json=self.json,
                timeout=self.timeout,
                headers=self.headers,
                files=self.files,
            )

    # TODO remove session manager when fully moved over to session provider
    def operation_get(self):
        if self.session_provider:
            session = self.session_provider.build_session()
            return session.get(
                self.url,
                timeout=self.timeout,
                headers=self.headers,
            )
        else:
            return self.session_manager.get(
                self.url,
                timeout=self.timeout,
                headers=self.headers,
            )

    def extract_payload(self, response):
        if not response:
            return None

        content_type = response.headers.get("Content-Type", "").lower()

        if "json" in content_type:
            try:
                return response.json()
            except ValueError:
                pass

        return response.text

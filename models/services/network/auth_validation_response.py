from dataclasses import dataclass


@dataclass
class AuthValidationResponse:
    cookies_valid: bool = False
    token_valid: bool = False

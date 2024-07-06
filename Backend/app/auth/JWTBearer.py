"""JWT Token validation and injection for endpoints"""

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import app.auth.security_service as security_service
from app.auth.security_schema import (
    BadJWTTokenProvidedException,
    JWTValidationException,
    TokenData,
)
from app.auth.security_service import get_jwt_token_data
from app.logging.logging_constants import LOGGING_JWT_BEARER
from app.logging.logging_schema import SpotifyElectronLogger

jwt_bearer_logger = SpotifyElectronLogger(LOGGING_JWT_BEARER).getLogger()

TOKEN_HEADER_FIELD_NAME = "Authorization"
BEARER_SCHEME_NAME = "Bearer"
JWT_COOKIE_HEADER_FIELD_NAME = "jwt"


class FakeRequest:
    headers: dict = {}

    def __init__(self, auth_value: str) -> None:
        self.headers[TOKEN_HEADER_FIELD_NAME] = auth_value


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> TokenData:
        """Returns Token data or 403 Code if credentials are invalid

        Args:
            request (Request): the incoming request

        Raises:
            BadJWTTokenProvidedException: invalid credentials

        Returns:
            TokenData: the token data
        """
        # TODO Recieving b'"bearer eyJhbGciOiJIUzI"' from frontend
        # instead of b'bearer eyJhbGciOiJIUzI'
        # replacing " with white space for all headers can be deleted if its solved
        if len(request.cookies) == 0 or not request.cookies.get(JWT_COOKIE_HEADER_FIELD_NAME):
            jwt_bearer_logger.warning(
                f"Request with no cookies {request}, getting JWT from Authentication Header"
            )
            jwt_raw = get_authorization_bearer(request.headers.raw)
        else:
            jwt_raw = request.cookies.get(JWT_COOKIE_HEADER_FIELD_NAME)

        fake_request = FakeRequest(jwt_raw)  # type: ignore
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(  # noqa: UP008
            fake_request  # type: ignore
        )
        if not credentials or credentials.scheme != BEARER_SCHEME_NAME:
            raise BadJWTTokenProvidedException
        try:
            jwt_raw = credentials.credentials
            security_service.validate_jwt(jwt_raw)
            jwt_token_data = get_jwt_token_data(credentials.credentials)
        except (JWTValidationException, Exception):
            jwt_bearer_logger.exception(f"Request with invalid JWT {jwt_raw} {request}")
            raise BadJWTTokenProvidedException
        else:
            return jwt_token_data


def get_authorization_bearer(headers: list[tuple]) -> str | None:
    """Get authorization bearer value from HTTP header 'authorization'

    Args:
        headers (list[tuple]): headers

    Returns:
        str | None: the authorization value
    """
    for key, value in headers:
        if key == b"authorization":
            return value.decode("utf-8")
    return None

from datetime import datetime
from datetime import timedelta

import jwt
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.utils.timezone import now
from pytz import utc

from core.errors import ErrorMessages
from core.exceptions import DecodeException
from core.exceptions import IATException
from core.exceptions import InvalidTokenName
from core.exceptions import SecretNotFoundException


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        if token := self.get_token_from_scope(scope):
            try:
                scope["user"] = self.authenticate_with_token(token)
                return await super().__call__(scope, receive, send)
            except (IATException, DecodeException, SecretNotFoundException, InvalidTokenName) as exc:
                await self.send_error_response(send, str(exc))
                return
        else:
            await self.send_error_response(send, ErrorMessages.TOKEN_NOT_PROVIDED)
            return

    @staticmethod
    async def send_error_response(send, error_message):
        await send({"type": "websocket.close", "code": 1002, "reason": error_message})

    @staticmethod
    def get_token_from_scope(scope) -> bytes | None:
        headers = dict(scope.get("headers", {}))
        return headers.get(b"authorization")

    @staticmethod
    def _get_token_name_and_key(token: bytes) -> str:
        try:
            token_name, token_key = token.decode().split()
        except ValueError:
            raise InvalidTokenName(ErrorMessages.INVALID_TOKEN_NAME, "UNPARSED")
        else:
            if token_name == "Bearer":
                return token_key
            raise InvalidTokenName(ErrorMessages.INVALID_TOKEN_NAME, token_name)

    @staticmethod
    def _get_secret(token_key) -> str:
        try:
            unverified_payload = jwt.decode(token_key, algorithms=["HS256"], options={"verify_signature": False})
        except jwt.DecodeError as exc:
            raise DecodeException(str(exc))
        else:
            if secret := settings.WS_CLIENTS.get(unverified_payload.get("iss")):
                return secret
            raise SecretNotFoundException(ErrorMessages.SECRET_NOT_FOUND)

    def authenticate_with_token(self, token) -> str:
        token_key = self._get_token_name_and_key(token)
        secret = self._get_secret(token_key)
        try:
            payload = jwt.decode(token_key, secret, algorithms=["HS256"], options={"require_iat": True})
            iat = datetime.fromtimestamp(payload.get("iat"), tz=utc)
            if now() - iat > settings.JWT_TOKEN_LIFETIME:
                raise IATException(ErrorMessages.TOKEN_EXPIRED)
            return payload["iss"]
        except jwt.DecodeError:
            raise DecodeException(ErrorMessages.ERROR_DECODING)
        except jwt.ImmatureSignatureError as exc:
            raise IATException(str(exc))

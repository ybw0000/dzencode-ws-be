from datetime import timedelta
from unittest import IsolatedAsyncioTestCase
from unittest import mock
from unittest.mock import MagicMock

import jwt
from django.utils.timezone import now

from core.middlewares import JWTAuthMiddleware


class MockInnerApp:
    async def __call__(self, scope, receive, send):
        pass


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class JWTAuthMiddlewareTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.inner = MockInnerApp()
        self.middleware = JWTAuthMiddleware(self.inner)
        token = jwt.encode(payload={"iat": now().timestamp(), "iss": "test"}, key="test", algorithm="HS256").encode()
        self.scope = {
            "type": "websocket",
            "headers": {b"authorization": b"Bearer %s" % token},
        }
        self.receive = AsyncMock()
        self.send = AsyncMock()

    @mock.patch("core.middlewares.settings.WS_CLIENTS", {"test": "test"})
    async def test__middleware__success__valid_token(self):
        await self.middleware(self.scope, self.receive, self.send)
        self.assertEqual(self.scope["user"], "test")
        self.send.assert_not_called()

    @mock.patch("core.middlewares.settings.WS_CLIENTS", {"test": "test"})
    async def test__middleware__fail__iat_invalid(self):
        token_in_future = jwt.encode(
            payload={"iat": (now() + timedelta(minutes=2)).timestamp(), "iss": "test"}, key="test", algorithm="HS256"
        ).encode()
        self.scope["headers"][b"authorization"] = b"Bearer %s" % token_in_future
        await self.middleware(self.scope, self.receive, self.send)
        self.send.assert_called_once()

    @mock.patch("core.middlewares.settings.WS_CLIENTS", {"test": "test"})
    @mock.patch("core.middlewares.settings.JWT_TOKEN_LIFETIME", timedelta(minutes=5))
    async def test__middleware__fail__token_expire(self):
        token_in_future = jwt.encode(
            payload={"iat": (now() - timedelta(minutes=6)).timestamp(), "iss": "test"}, key="test", algorithm="HS256"
        ).encode()
        self.scope["headers"][b"authorization"] = b"Bearer %s" % token_in_future
        await self.middleware(self.scope, self.receive, self.send)
        self.send.assert_called_once()

    @mock.patch("core.middlewares.settings.WS_CLIENTS", {"test": "test"})
    async def test__middleware__fail__invalid_token(self):
        self.scope["headers"][b"authorization"] = b"Bearer %s" % b"asd.123.asd"
        await self.middleware(self.scope, self.receive, self.send)
        self.send.assert_called_once()

    @mock.patch("core.middlewares.settings.WS_CLIENTS", {"INVALID_CLIENT": "test"})
    async def test__middleware__fail__no_secret(self):
        await self.middleware(self.scope, self.receive, self.send)
        self.send.assert_called_once()

    @mock.patch("core.middlewares.settings.WS_CLIENTS", {"test": "test"})
    async def test__middleware__fail__no_token_name(self):
        self.scope["headers"][b"authorization"] = self.scope["headers"][b"authorization"].decode().split()[1].encode()
        await self.middleware(self.scope, self.receive, self.send)
        self.send.assert_called_once()

    @mock.patch("core.middlewares.settings.WS_CLIENTS", {"test": "test"})
    async def test__middleware__fail__invalid_token_name(self):
        _, token_key = self.scope["headers"][b"authorization"].decode().split()
        self.scope["headers"][b"authorization"] = b"NOT_BEARER %s" % token_key.encode()
        await self.middleware(self.scope, self.receive, self.send)
        self.send.assert_called_once()

    async def test__middleware__fail__token_not_provided(self):
        del self.scope["headers"][b"authorization"]
        await self.middleware(self.scope, self.receive, self.send)
        self.send.assert_called_once()

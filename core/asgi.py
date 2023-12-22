import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.core.asgi import get_asgi_application
from strawberry.channels.handlers.http_handler import GraphQLHTTPConsumer
from strawberry.channels.handlers.ws_handler import GraphQLWSConsumer

from comments.routing import websocket_urlpatterns
from core.graphql import schema
from core.middlewares import JWTAuthMiddleware

django_asgi_application = get_asgi_application()

gql_http_consumer = AuthMiddlewareStack(GraphQLHTTPConsumer.as_asgi(schema=schema))
gql_ws_consumer = GraphQLWSConsumer.as_asgi(schema=schema)

application = ProtocolTypeRouter(
    {
        "http": URLRouter(
            [
                path("graphql/", gql_http_consumer),
            ]
        ),
        "websocket": AllowedHostsOriginValidator(JWTAuthMiddleware(URLRouter(websocket_urlpatterns))),
    }
)

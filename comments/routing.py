from django.urls import path
from strawberry.channels.handlers.ws_handler import GraphQLWSConsumer

from comments.consumers import CommentsConsumer
from core.graphql import schema

websocket_urlpatterns = [
    path("ws/comments/", CommentsConsumer.as_asgi(), name="ws_comments"),
    path("graphql/", GraphQLWSConsumer.as_asgi(schema=schema), name="ws_graphql"),
]

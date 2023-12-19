import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from comments.models import Comment
from comments.serializers import CommentSerializer


class CommentsConsumer(AsyncWebsocketConsumer):
    group_name = 'comments'

    async def connect(self):
        await self.channel_layer.group_add(group=self.group_name, channel=self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({'type': 'parent.comments', 'data': await self.get_all_parent_comments()}))

    async def disconnect(self, close_code):
        await self.close(close_code)

    async def receive(self, text_data=None, bytes_data=None):
        pass

    @database_sync_to_async
    def get_all_parent_comments(self) -> dict:
        qs = Comment.parent_objects.all()
        serializer = CommentSerializer(qs, many=True)
        return serializer.data

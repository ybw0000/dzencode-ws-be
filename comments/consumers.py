import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from comments.enums import EventTypes
from comments.errors import ErrorMessages
from comments.models import Comment
from comments.serializers import ChildCommentRequestSerializer
from comments.serializers import CommentSerializer

logger = logging.getLogger(__name__)


class CommentsConsumer(AsyncJsonWebsocketConsumer):
    group_name = "comments"

    async def send_json(self, content, close=False):
        logger.info(msg={"message": "Sending event", "content": content})
        await super().send_json(content, close)

    async def connect(self):
        await self.channel_layer.group_add(group=self.group_name, channel=self.channel_name)
        await self.accept()
        logger.info(msg={"message": f"WebSocket connected: {self.channel_name}"})
        await self.send_json({"type": EventTypes.COMMENT_PARENT_LIST, "data": await self.__get_all_parent_comments()})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(msg={"message": f"WebSocket disconnected: {self.channel_name}"})

    async def receive_json(self, content, **kwargs):
        logger.info(msg={"message": f"Received event {content.get('type')}", "content": content})
        message_type = content.get("type")
        if message_type == EventTypes.COMMENT_CREATE:
            await self.__handle_create_comment(content.get("data"), **kwargs)
        elif message_type == EventTypes.COMMENT_CHILD_LIST:
            await self.__handle_get_child_list(content.get("data"), **kwargs)
        else:
            await self.send_json({"type": EventTypes.ERROR, "data": ErrorMessages.INVALID_MESSAGE_TYPE})

    async def comment_create(self, content):
        await self.send_json(content)

    async def __handle_create_comment(self, data=None, **kwargs):
        serializer = CommentSerializer(data=data)
        if await database_sync_to_async(serializer.is_valid)(raise_exception=False):
            await self.__create_comment(serializer)
            if not serializer.data["parent"]:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": EventTypes.COMMENT_CREATE,
                        "data": serializer.data,
                    },
                )
            else:
                await self.send_json(
                    {
                        "type": EventTypes.COMMENT_CREATE,
                        "data": serializer.data,
                    },
                )
        else:
            await self.send_json({"type": EventTypes.COMMENT_ERROR, "data": serializer.errors})

    async def __handle_get_child_list(self, data=None, **kwargs):
        serializer = ChildCommentRequestSerializer(data=data)
        if await database_sync_to_async(serializer.is_valid)(raise_exception=False):
            await self.send_json(
                {
                    "type": EventTypes.COMMENT_CHILD_LIST,
                    "data": await self.__get_child_comments(serializer.validated_data),
                }
            )
        else:
            await self.send_json({"type": EventTypes.COMMENT_CHILD_LIST_ERROR, "data": serializer.errors})

    @staticmethod
    @database_sync_to_async
    def __create_comment(serializer: CommentSerializer) -> None:
        serializer.save()

    @staticmethod
    @database_sync_to_async
    def __get_all_parent_comments() -> dict:
        qs = Comment.parent_objects.all()
        serializer = CommentSerializer(qs, many=True)
        return serializer.data

    @staticmethod
    @database_sync_to_async
    def __get_child_comments(filters: dict) -> dict:
        offset = 25
        if filters["page"] == 1:
            range_from = 0
            range_to = offset
        else:
            range_to = filters["page"] * offset
            range_from = range_to - offset
        qs = Comment.children_objects.filter(parent=filters["parent"])[range_from:range_to]
        serializer = CommentSerializer(qs, many=True)
        return serializer.data

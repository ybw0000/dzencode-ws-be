import strawberry
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels_redis.core import RedisChannelLayer
from strawberry.types import Info

from comments.enums import EventTypes
from comments.serializers import CommentSerializer
from comments.types import CreateChildCommentInput
from comments.types import CreateCommentInput
from comments.types import CreateCommentType


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_parent_comment(self, info: Info, data: CreateCommentInput) -> CreateCommentType:
        serializer = CommentSerializer(data=data.__dict__)
        if serializer.is_valid(raise_exception=False):
            await database_sync_to_async(serializer.save)()
            channel_layer: RedisChannelLayer = get_channel_layer()

            await channel_layer.group_send(
                "comments",
                {
                    "type": EventTypes.COMMENT_CREATE,
                    "data": serializer.data,
                },
            )
            return CreateCommentType(**serializer.data)
        return serializer.errors

    @strawberry.mutation
    async def create_child_comment(self, info: Info, data: CreateChildCommentInput) -> CreateCommentType:
        serializer = CommentSerializer(data=data.__dict__)
        if await database_sync_to_async(serializer.is_valid)(raise_exception=False):
            await database_sync_to_async(serializer.save)()
            return CreateCommentType(**serializer.data)
        return serializer.errors

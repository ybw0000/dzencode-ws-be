from typing import AsyncGenerator
from typing import List

import strawberry
from channels.db import database_sync_to_async
from strawberry.types import Info

from comments.enums import EventTypes
from comments.models import Comment
from comments.serializers import CommentSerializer
from comments.types import CreateCommentType


@database_sync_to_async
def get_parents_data() -> List[CreateCommentType]:
    qs = Comment.parent_objects.all()
    serializer = CommentSerializer(qs, many=True)
    return [CreateCommentType(**data) for data in serializer.data]


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def listen_parent_comments(
        self,
        info: Info,
    ) -> AsyncGenerator[list[CreateCommentType] | None, None]:
        ws = info.context["ws"]
        channel_layer = ws.channel_layer

        await channel_layer.group_add("comments", ws.channel_name)

        async with ws.listen_to_channel(EventTypes.COMMENT_CREATE, groups=["comments"]) as cc:
            yield await get_parents_data()
            async for message in cc:
                yield [CreateCommentType(**message["data"])]

from typing import List

import strawberry
from channels.db import database_sync_to_async

from comments.models import Comment
from comments.serializers import CommentSerializer
from comments.types import CreateCommentType


@database_sync_to_async
def resolver_parents() -> List[CreateCommentType]:
    qs = Comment.parent_objects.all()
    serializer = CommentSerializer(qs, many=True)
    return [CreateCommentType(**data) for data in serializer.data]


@database_sync_to_async
def resolver_children(parent: int) -> List[CreateCommentType]:
    qs = Comment.children_objects.filter(parent_id=parent)
    serializer = CommentSerializer(qs, many=True)
    return [CreateCommentType(**data) for data in serializer.data]


@strawberry.type
class Query:
    parents = strawberry.field(resolver=resolver_parents)
    children = strawberry.field(resolver=resolver_children)

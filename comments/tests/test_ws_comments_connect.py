from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TestCase

from comments.consumers import CommentsConsumer
from comments.enums import EventTypes
from comments.serializers import CommentSerializer
from comments.tests.factories import ChildCommentFactory
from comments.tests.factories import CommentFactory


class CommentWsTestCase(TestCase):
    maxDiff = None

    async def test__ws_connect__success__without_comments(self):
        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()

        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {"type": EventTypes.COMMENT_PARENT_LIST, "data": []}  # Adjust with your expected data
        self.assertEqual(response, expected_data)

        await communicator.disconnect()

    async def test__ws_connect__success__with_parent_comment(self):
        comment = await database_sync_to_async(CommentFactory)()

        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()

        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            "type": EventTypes.COMMENT_PARENT_LIST,
            "data": [CommentSerializer(instance=comment).data],
        }
        self.assertEqual(response, expected_data)

        await communicator.disconnect()

    async def test__ws_connect__success__with_child_comment(self):
        child_comment = await database_sync_to_async(ChildCommentFactory)()

        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()

        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            "type": EventTypes.COMMENT_PARENT_LIST,
            "data": [CommentSerializer(instance=child_comment.parent).data],
        }
        self.assertEqual(response, expected_data)

        await communicator.disconnect()

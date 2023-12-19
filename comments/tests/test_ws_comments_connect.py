from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TestCase

from comments.consumers import CommentsConsumer
from comments.serializers import CommentSerializer
from comments.tests.factories import ChildCommentFactory
from comments.tests.factories import CommentFactory


class CommentWsTestCase(TestCase):
    maxDiff = None

    async def test__ws_connect__success__without_comments(self):
        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), 'websocket.connect')
        connected = await communicator.connect()

        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {'type': 'parent.comments', 'data': []}  # Adjust with your expected data
        self.assertEqual(response, expected_data)

        await communicator.disconnect()

    async def test__ws_connect__success__with_parent_comment(self):
        comment = await sync_to_async(CommentFactory)()

        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), 'websocket.connect')
        connected = await communicator.connect()

        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            'type': 'parent.comments',
            'data': [CommentSerializer(instance=comment).data],
        }
        self.assertEqual(response, expected_data)

        await communicator.disconnect()

    async def test__ws_connect__success__with_child_comment(self):
        child_comment = await sync_to_async(ChildCommentFactory)()

        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), 'websocket.connect')
        connected = await communicator.connect()

        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            'type': 'parent.comments',
            'data': [CommentSerializer(instance=child_comment.parent).data],
        }
        self.assertEqual(response, expected_data)

        await communicator.disconnect()

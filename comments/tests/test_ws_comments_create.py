from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TestCase

from comments.consumers import CommentsConsumer
from comments.enums import EventTypes
from comments.errors import ErrorMessages
from comments.models import Comment
from comments.tests.factories import CommentFactory


class WsCommentsCreateTestCase(TestCase):
    maxDiff = None

    async def test__parent_comment_create__success(self):
        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            "type": EventTypes.COMMENT_PARENT_LIST,
            "data": [],
        }
        self.assertEqual(response, expected_data)

        await communicator.send_json_to(
            {
                "type": EventTypes.COMMENT_CREATE,
                "data": {
                    "user_name": "test",
                    "text": "test comment",
                },
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": {
                    "email": None,
                    "home_page": None,
                    "id": 1,
                    "parent": None,
                    "text": "test comment",
                    "user_name": "test",
                },
                "type": EventTypes.COMMENT_CREATE,
            },
            response,
        )
        self.assertEqual(await database_sync_to_async(Comment.objects.count)(), 1)

    async def test__child_comment_create__success(self):
        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            "type": EventTypes.COMMENT_PARENT_LIST,
            "data": [],
        }
        self.assertEqual(response, expected_data)

        parent = await database_sync_to_async(CommentFactory)()
        await communicator.send_json_to(
            {
                "type": EventTypes.COMMENT_CREATE,
                "data": {
                    "user_name": "test",
                    "text": "test comment",
                    "parent": parent.id,
                },
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": {
                    "email": None,
                    "home_page": None,
                    "id": 2,
                    "parent": parent.id,
                    "text": "test comment",
                    "user_name": "test",
                },
                "type": EventTypes.COMMENT_CREATE,
            },
            response,
        )
        self.assertEqual(await database_sync_to_async(Comment.objects.count)(), 2)
        self.assertEqual(await database_sync_to_async(Comment.parent_objects.count)(), 1)
        self.assertEqual(await database_sync_to_async(Comment.children_objects.count)(), 1)

    async def test__parent_comment_create__fail__invalid_data(self):
        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            "type": EventTypes.COMMENT_PARENT_LIST,
            "data": [],
        }
        self.assertEqual(response, expected_data)

        await communicator.send_json_to(
            {
                "type": EventTypes.COMMENT_CREATE,
                "data": {},
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": {
                    "text": ["This field is required."],
                    "user_name": ["This field is required."],
                },
                "type": EventTypes.COMMENT_ERROR,
            },
            response,
        )
        self.assertEqual(await database_sync_to_async(Comment.objects.count)(), 0)

    async def test__child_comment_create__fail__invalid_parent_id(self):
        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            "type": EventTypes.COMMENT_PARENT_LIST,
            "data": [],
        }
        self.assertEqual(response, expected_data)

        parent = await database_sync_to_async(CommentFactory)()
        await communicator.send_json_to(
            {
                "type": EventTypes.COMMENT_CREATE,
                "data": {
                    "user_name": "test",
                    "text": "test comment",
                    "parent": parent.id + 100,
                },
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": {
                    "parent": [f'Invalid pk "{parent.id + 100}" - object does not exist.'],
                },
                "type": EventTypes.COMMENT_ERROR,
            },
            response,
        )
        self.assertEqual(await database_sync_to_async(Comment.objects.count)(), 1)
        self.assertEqual(await database_sync_to_async(Comment.parent_objects.count)(), 1)
        self.assertEqual(await database_sync_to_async(Comment.children_objects.count)(), 0)

    async def test__parent_comment_create__fail__invalid_message_type(self):
        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            "type": EventTypes.COMMENT_PARENT_LIST,
            "data": [],
        }
        self.assertEqual(response, expected_data)

        await communicator.send_json_to(
            {
                "type": "INVALID_MESSAGE_TYPE",
                "data": {
                    "user_name": "test",
                    "text": "test comment",
                },
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": ErrorMessages.INVALID_MESSAGE_TYPE,
                "type": EventTypes.ERROR,
            },
            response,
        )
        self.assertEqual(await database_sync_to_async(Comment.objects.count)(), 0)

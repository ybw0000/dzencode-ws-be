from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import TestCase

from comments.consumers import CommentsConsumer
from comments.enums import EventTypes
from comments.serializers import CommentSerializer
from comments.tests.factories import ChildCommentFactory
from comments.tests.factories import CommentFactory


class WsCommentsRetrieveTestCase(TestCase):
    maxDiff = None

    async def test__ws_comments_retrieve__fails__invalid_data(self):
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
                "type": EventTypes.COMMENT_CHILD_LIST,
                "data": {},
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": {"parent": ["This field is required."]},
                "type": "comment.child.list.error",
            },
            response,
        )

    async def test__ws_comments_retrieve__fails__parent_not_found(self):
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
                "type": EventTypes.COMMENT_CHILD_LIST,
                "data": {"parent": 1},
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": {"parent": ['Invalid pk "1" - object does not exist.']},
                "type": "comment.child.list.error",
            },
            response,
        )

    async def test__ws_comments_retrieve__success__no_children(self):
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
                "type": EventTypes.COMMENT_CHILD_LIST,
                "data": {"parent": parent.id},
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": [],
                "type": "comment.child.list",
            },
            response,
        )

    async def test__ws_comments_retrieve__success__one_child(self):
        communicator = WebsocketCommunicator(CommentsConsumer.as_asgi(), "websocket.connect")
        connected = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        expected_data = {
            "type": EventTypes.COMMENT_PARENT_LIST,
            "data": [],
        }
        self.assertEqual(response, expected_data)

        child = await database_sync_to_async(ChildCommentFactory)()
        await communicator.send_json_to(
            {
                "type": EventTypes.COMMENT_CHILD_LIST,
                "data": {"parent": child.parent_id},
            }
        )
        response = await communicator.receive_json_from()
        self.assertEqual(
            {
                "data": [
                    {
                        "email": None,
                        "home_page": None,
                        "parent": child.parent_id,
                        "id": child.id,
                        "user_name": child.user_name,
                        "text": child.text,
                    }
                ],
                "type": "comment.child.list",
            },
            response,
        )

    async def test__ws_comments_retrieve__success__test_pages(self):
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
        children = await database_sync_to_async(ChildCommentFactory.create_batch)(size=30, parent=parent)

        # get first page
        await communicator.send_json_to(
            {
                "type": EventTypes.COMMENT_CHILD_LIST,
                "data": {"parent": parent.id},
            }
        )
        response = await communicator.receive_json_from()
        self.assertIn("data", response)
        self.assertListEqual(CommentSerializer(list(reversed(children))[:25], many=True).data, response["data"])
        self.assertEqual(EventTypes.COMMENT_CHILD_LIST, response["type"])

        # get second page
        await communicator.send_json_to(
            {
                "type": EventTypes.COMMENT_CHILD_LIST,
                "data": {
                    "parent": parent.id,
                    "page": 2,
                },
            }
        )
        response = await communicator.receive_json_from()
        self.assertIn("data", response)
        self.assertListEqual(CommentSerializer(list(reversed(children))[25:30], many=True).data, response["data"])
        self.assertEqual(EventTypes.COMMENT_CHILD_LIST, response["type"])

from django.test import TestCase

from comments.models import Comment
from comments.tests.factories import ChildCommentFactory
from comments.tests.factories import CommentFactory


class CommentModelTest(TestCase):
    maxDiff = None

    def test__create_parent_comment__success(self):
        CommentFactory()

        self.assertNotEqual(Comment.objects.first(), None)
        self.assertEqual(len(Comment.objects.all()), 1)
        self.assertEqual(len(Comment.children_objects.all()), 0)

    def test__create_child_comment__success(self):
        ChildCommentFactory()

        self.assertNotEqual(Comment.objects.first(), None)
        self.assertEqual(len(Comment.objects.all()), 2)
        self.assertEqual(len(Comment.children_objects.all()), 1)

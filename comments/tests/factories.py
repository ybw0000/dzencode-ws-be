import factory

from comments.models import Comment


class CommentFactory(factory.django.DjangoModelFactory):
    """Factory for creating a comment object"""

    parent = None

    class Meta:
        model = Comment


class ChildCommentFactory(factory.django.DjangoModelFactory):
    """Factory for creating a child comment object"""

    parent = factory.SubFactory(CommentFactory)

    class Meta:
        model = Comment

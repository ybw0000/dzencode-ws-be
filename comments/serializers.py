from django.core.validators import MinValueValidator
from rest_framework import serializers

from comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class ChildCommentRequestSerializer(serializers.Serializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.parent_objects.all())
    page = serializers.IntegerField(default=1, required=False, validators=[MinValueValidator(1)])

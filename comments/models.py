from django.db import models


class ChildrenManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent__isnull=False).order_by("-id")


class ParentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(parent__isnull=True).order_by("-id")


class Comment(models.Model):
    user_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    home_page = models.URLField(blank=True, null=True)
    text = models.TextField()
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, blank=True, null=True)

    objects = models.Manager()
    children_objects = ChildrenManager()
    parent_objects = ParentManager()

from django.db import models


class Image(models.Model):
    src = models.CharField(max_length=255, null=True)
    width = models.SmallIntegerField(null=True)
    height = models.SmallIntegerField(null=True)
    portrait = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

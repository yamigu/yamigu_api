from django.db import models
from authorization.models import User
from file_management.models import Image


class FriendRequest(models.Model):
    requestee = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_request')
    requestor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_request')
    requested_on = models.DateTimeField()
    approved_on = models.DateTimeField()
    declined_on = models.DateTimeField()


class Shield(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shield')
    phoneno = models.CharField(max_length=255)
    belong = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class MatchRequest(models.Model):
    STATUS_CODE_MATCHING = 1
    STATUS_CODE_MATCHED = 2
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='match_request')
    requested_on = models.DateTimeField(auto_now_add=True, blank=True)
    matched_on = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(default=0)


class Feed(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feed')
    before = models.ForeignKey(
        "self", on_delete=models.SET_NULL, related_name='next', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='like')
    feed = models.ForeignKey(
        Feed, on_delete=models.CASCADE, related_name='like')
    is_unread = models.BooleanField(default=True)


class FeedImage(models.Model):
    feed = models.OneToOneField(
        Feed, on_delete=models.CASCADE, related_name='image')
    data = models.OneToOneField(
        Image, on_delete=models.CASCADE, null=True)


class FeedText(models.Model):
    feed = models.OneToOneField(
        Feed, on_delete=models.CASCADE, related_name='text')
    value = models.CharField(max_length=255)


class FeedRead(models.Model):
    feed = models.ForeignKey(
        Feed, on_delete=models.CASCADE, related_name='read')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='read')
    read_on = models.DateTimeField(auto_now_add=True)


class Chat(models.Model):
    roomno = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notification')
    like = models.BooleanField(default=True)
    like_match = models.BooleanField(default=True)
    request = models.BooleanField(default=True)
    match = models.BooleanField(default=True)
    chat = models.BooleanField(default=True)

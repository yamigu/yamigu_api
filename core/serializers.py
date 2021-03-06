from rest_framework.serializers import ModelSerializer, SerializerMethodField, Serializer
from django.db import models
from .models import *
from authorization.serializers import ProfileSerializer
from drf_yasg.utils import swagger_serializer_method


class MatchRequestSerializer(ModelSerializer):
    class Meta:
        model = MatchRequest
        fields = "__all__"
        read_only_fields = ('status', 'matched_on')


class FeedSerializer(ModelSerializer):
    img_src = SerializerMethodField('get_img_src')

    def get_img_src(self, feed):
        if(hasattr(feed, 'image')):
            return feed.image.data.src
        return None

    class Meta:
        model = Feed
        fields = ('img_src', 'created_at')


class FeedListSerializer(ModelSerializer):
    profile = SerializerMethodField('get_profile')
    feed_list = SerializerMethodField('get_feed_list')
    @swagger_serializer_method(serializer_or_field=ProfileSerializer)
    def get_profile(self, user):
        return ProfileSerializer(user).data

    @swagger_serializer_method(serializer_or_field=FeedSerializer)
    def get_feed_list(self, user):
        feed_for_user = user.feed.all()
        return FeedSerializer(feed_for_user, many=True).data

    class Meta:
        model = User
        fields = ('profile', 'feed_list')


class FeedCreateSerializer(ModelSerializer):
    image = models.ImageField()

    class Meta:
        model = Feed
        fields = ('image',)


class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ('user', 'is_unread', 'created_at')


class SendFriendRequestSerialzier(ModelSerializer):
    class Meta:
        model = IdentityVerification
        fields = ('phoneno',)


class FriendRequestSerializer(ModelSerializer):
    approved = SerializerMethodField('check_if_approved')
    you_sent = SerializerMethodField('check_if_you_sent')
    phoneno = SerializerMethodField('get_phoneno')
    user_info = SerializerMethodField('get_user_info')

    def check_if_approved(self, friendRequest):
        if friendRequest.approved_on is not None:
            return True
        return False

    def check_if_you_sent(self, friendRequest):
        user = self.context.get("user")
        if friendRequest.requestor == user.iv:
            return True
        return False

    def get_phoneno(self, friendRequest):
        user = self.context.get("user")
        if friendRequest.requestor == user.iv:
            return friendRequest.requestee.phoneno
        return friendRequest.requestor.phoneno

    @swagger_serializer_method(serializer_or_field=ProfileSerializer)
    def get_user_info(self, friendRequest):
        user = self.context.get("user")
        if friendRequest.approved_on is not None:
            if(friendRequest.requestee == user.iv):
                return ProfileSerializer(friendRequest.requestor.user).data
            else:
                return ProfileSerializer(friendRequest.requestee.user).data
        return None

    class Meta:
        model = FriendRequest
        fields = ('approved', 'you_sent', 'phoneno', 'user_info')

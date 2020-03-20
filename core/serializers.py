from rest_framework.serializers import ModelSerializer, SerializerMethodField, Serializer, IntegerField, CharField
from django.db import models
from django.db.models import Q
from .models import *
from authorization.serializers import ProfileSerializer
from drf_yasg.utils import swagger_serializer_method
from file_management.serializers import ImageSerializer


class MatchRequestSerializer(ModelSerializer):
    class Meta:
        model = MatchRequest
        fields = "__all__"
        read_only_fields = ('matched_on',)
        extra_kwargs = {'status': {'required': False}}


class FeedSerializer(ModelSerializer):
    img_src = SerializerMethodField('get_img_src')

    def get_img_src(self, feed):
        if(hasattr(feed, 'image')):
            return ImageSerializer(feed.image.data).data['src']
        return None

    class Meta:
        model = Feed
        fields = ('id', 'img_src', 'created_at')


class FeedListSerializer(ModelSerializer):
    profile = SerializerMethodField('get_profile')
    feed_list = SerializerMethodField('get_feed_list')
    liked = SerializerMethodField('check_if_liked')

    @swagger_serializer_method(serializer_or_field=ProfileSerializer)
    def get_profile(self, user):
        return ProfileSerializer(user).data

    @swagger_serializer_method(serializer_or_field=FeedSerializer)
    def get_feed_list(self, user):
        feed_for_user = user.feed.filter(deleted_at__isnull=True)
        return FeedSerializer(feed_for_user, many=True).data

    def check_if_liked(self, user):
        me = self.context.get("user")
        if hasattr(user, 'feed'):
            if user.feed.count() > 0:
                likes = user.feed.last().like.all()
                for like in likes:
                    if like.user.id == me.id and like.value:
                        return True
        return False

    class Meta:
        model = User
        fields = ('profile', 'liked', 'feed_list')


class FeedCreateSerializer(ModelSerializer):
    image = models.ImageField()

    class Meta:
        model = Feed
        fields = ('image',)


class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = ('user', 'value', 'is_unread', 'created_at')
        read_only_fields = ('user', 'value', 'is_unread', 'created_at')


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
        fields = ('id', 'approved', 'you_sent', 'phoneno', 'user_info')
        read_only_fields = ('id', 'approved', 'you_sent', 'user_info')


class FriendRequestPatchSerializer(Serializer):
    id = IntegerField(help_text='FriendRequest\'s ID')
    action = CharField(help_text='APPROVE or DECLINE or DELETE or CANCEL')


class FriendRequestNotAprListSerializer(Serializer):
    count = SerializerMethodField('get_requests')

    def get_requests(self, user):
        received_request = []
        sent_request = []
        return user.iv.received_request.filter(approved_on__isnull=True).count()

    class Meta:
        model = User
        fields = ('count', )


class FriendListSerializer(ModelSerializer):
    friends = SerializerMethodField('get_friends')

    def get_friends(self, user):
        received_request = []
        sent_request = []
        received_request = user.iv.received_request.filter(
            approved_on__isnull=False)
        sent_request = user.iv.sent_request.filter(
            approved_on__isnull=False)
        friends_list = []
        for request in received_request:
            friends_list.append(request.requestor.user)
        for request in sent_request:
            friends_list.append(request.requestee.user)
        return ProfileSerializer(friends_list, many=True).data

    class Meta:
        model = User
        fields = ('friends', )


class ChatCreateAPISerializer(Serializer):
    target_uid = CharField(help_text='Partner\'s UID')


class ChatCreateSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'declined_on',
                            'canceled_on', 'approved_on')
        optional_fields = ('chat_type', )


class ChatSerializer(ModelSerializer):
    sender = SerializerMethodField('get_sender')
    receiver = SerializerMethodField('get_receiver')

    @swagger_serializer_method(serializer_or_field=ProfileSerializer)
    def get_sender(self, chat):
        serializer = ProfileSerializer(chat.sender)
        return serializer.data

    @swagger_serializer_method(serializer_or_field=ProfileSerializer)
    def get_receiver(self, chat):
        serializer = ProfileSerializer(chat.receiver)
        return serializer.data

    class Meta:
        model = Chat
        fields = ('id', 'sender', 'receiver', 'created_at', 'chat_type',
                  'declined_on', 'canceled_on', 'approved_on')
        read_only_fields = ('id', 'sender', 'receiver', 'chat_type', 'created_at', 'declined_on',
                            'canceled_on', 'approved_on')


class ChatDetailSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'


class ChatListSerializer(ModelSerializer):
    chat_list = SerializerMethodField('get_chat_list')

    @swagger_serializer_method(serializer_or_field=ChatSerializer)
    def get_chat_list(self, user):
        chat_sent = user.chat_sent.filter(
            declined_on__isnull=True).exclude(Q(canceled_on__isnull=False) & Q(canceled_by=user)).exclude(cancel_check=True)
        chat_recv = user.chat_recv.filter(
            declined_on__isnull=True).exclude(Q(canceled_on__isnull=False) & Q(canceled_by=user)).exclude(cancel_check=True)
        data = chat_sent | chat_recv
        serializer = ChatSerializer(data, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = ('chat_list', )


class ShieldCreateSerializer(Serializer):
    phoneno = CharField(help_text="phoneno", required=False)
    belong = CharField(help_text="belong", required=False)


class ShieldSerializer(ModelSerializer):
    class Meta:
        model = Shield
        fields = '__all__'


class ReportSerializer(ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


class ReportCreateSerializer(Serializer):
    who = CharField(help_text="신고할 대상 유저의 uid", required=True)
    why = CharField(help_text="신고 이유", required=True)


class BlockCreateSerializer(Serializer):
    who = CharField(help_text="차단할 대상 유저의 uid", required=True)


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *
from file_management.utils.file_helper import save_uploaded_file, rotate_image, get_file_path
from authorization.models import *
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from django.db import IntegrityError
import datetime


class MatchRequestView(APIView):
    """
        미팅 주선 신청

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: MatchRequestSerializer(), 204: "No Match Request"})
    def get(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, 'match_request') and user.match_request.last() is not None:
            mr = user.match_request.last()
            if mr.status == MatchRequest.STATUS_CODE_MATCHING:
                serializer = MatchRequestSerializer(mr)
                return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT, data="no match request")

    @swagger_auto_schema(request_body=MatchRequestSerializer, responses={201: "successfully requested", 400: "Bad Request"})
    def post(self, request, *args, **kwargs):
        user = request.user
        personnel = request.data['personnel_selected']
        date = request.data['date_selected']
        min_age = request.data['min_age']
        max_age = request.data['max_age']
        data = {
            'user': user.id,
            'status': MatchRequest.STATUS_CODE_MATCHING,
            'personnel_selected': personnel,
            'date_selected': date,
            'min_age': min_age,
            'max_age': max_age,
        }
        serializer = MatchRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data="successfully requested")
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @swagger_auto_schema(responses={202: "successfully canceled", 400: "Bad Request"})
    def patch(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, 'match_request'):
            mr = user.match_request.last()
            if mr.status == MatchRequest.STATUS_CODE_MATCHING:
                mr.status = MatchRequest.STATUS_CODE_CANCELED
                mr.save()
                return Response(status=status.HTTP_202_ACCEPTED, data="successfully canceled")
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")


class FeedListView(APIView):
    """
        피드 List

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: FeedListSerializer()})
    def get(self, request, *args, **kwargs):
        user = request.user
        users = User.objects.all()
        serializer = FeedListSerializer(
            users, many=True, context={'user': user})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FeedView(APIView):
    """
        피드 자세히 보기

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: FeedSerializer()})
    def get(self, request, *args, **kwargs):
        user = User.objects.get(uid=kwargs.get('uid'))
        serializer = FeedSerializer(user.feed.filter(
            deleted_at__isnull=True), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FeedDeleteView(APIView):
    """
        피드 삭제

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: 'successfully deleted'})
    def patch(self, request, *args, **kwargs):
        feed = Feed.objects.get(id=kwargs.get('fid'))
        feed.deleted_at = datetime.datetime.now()
        feed.save()
        return Response(status=status.HTTP_200_OK, data="successfully deleted")


class FeedCreateView(APIView):
    """
        피드 생성

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=FeedCreateSerializer(), responses={201: "successfully created"})
    def post(self, request, *args, **kwargs):
        user = request.user
        before = None
        if(hasattr(user, 'feed')):
            before = user.feed.last()
        feed = Feed(
            user=user,
            before=before
        )
        feed.save()
        TAG = "Feed"
        file_name = save_uploaded_file(request.data['image'], TAG)
        image = Image(
            src=TAG + "/" + file_name
        )
        image.save()
        feed_image = FeedImage(
            feed=feed,
            data=image
        )
        feed_image.save()
        rotate_image(get_file_path(file_name, TAG))
        serializer = FeedSerializer(feed)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ShieldView(APIView):
    """
        아는 사람 피하기

        ---
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = []
        if(hasattr(user.shield)):
            shields = user.shield.all()
            for shield in shields:
                if not shield.phoneno.empty():
                    data.append({'phoneno': shield.phoneno})
                else:
                    data.append({'belong': shield.belong})
            return Response(status=status.HTTP_200_OK, data=data)
        return Response(status=status.HTTP_200_OK, data="No shield")

    def post(self, request, *args, **kwargs):
        user = request.user
        phoneno_list = request.POST.getlist('phoneno')
        belong = request.POST.get('belong')
        if len(phoneno_list) > 0:
            for phoneno in phoneno_list:
                shield = Shield(user=user, phoneno=phoneno)
                shield.save()
            return Response(status=status.HTTP_200_OK, data="successfully created")
        elif belong is not None:
            shield = Shield(user=user, belong=belong)
            shield.save()
            return Response(status=status.HTTP_200_OK, data="successfully created")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LikeView(APIView):
    """
        좋아요

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: LikeSerializer()})
    def get(self, request, *args, **kwargs):
        feed = Feed.objects.get(id=kwargs.get('fid'))
        likes = feed.like.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @swagger_auto_schema(responses={201: 'successfully created', 208: ProfileSerializer})
    def post(self, request, *args, **kwargs):
        feed = Feed.objects.get(id=kwargs.get('fid'))
        user = request.user
        try:
            like = feed.like.get(user=user.id)
            like.value = True
            like.created_at = datetime.datetime.now()
            like.save()
        except ObjectDoesNotExist:
            like = Like(user=user, feed=feed)
            like.save()
        target_like_users = []
        for target_like in feed.user.like.all():
            if (target_like.value):
                target_like_users.append(target_like.feed.user)

        if user in target_like_users:
            user.something_with.add(feed.user)
            user.save()
            serializer = ProfileSerializer(feed.user)
            return Response(status=status.HTTP_208_ALREADY_REPORTED, data=serializer.data)

        return Response(status=status.HTTP_201_CREATED, data="successfully created")


class LikeCancelView(APIView):
    """
        좋아요 취소

        ---
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(responses={200: "successfully updated", 400: "Bad Request"})
    def post(self, request, *args, **kwargs):
        feed = Feed.objects.get(id=kwargs.get('fid'))
        user = request.user
        like = feed.like.get(user=user.id)
        if like is not None:
            like.value = False
            like.created_at = datetime.datetime.now()
            like.save()
            user.something_with.remove(feed.user)
            user.save()
            return Response(status=status.HTTP_200_OK, data="successfully updated")
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")


class BothLikeView(APIView):
    """
        서로 좋아요 List

        ---
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(responses={200: ProfileSerializer})
    def get(self, request, *args, **kwargs):
        user = request.user
        somethings = user.something_with.all()
        serializer = ProfileSerializer(somethings, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FriendView(APIView):
    """
        친구 리스트

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: FriendRequestSerializer(), 204: 'No friend', 400: 'Bad Request'})
    def get(self, request, *args, **kwargs):
        user = None
        if kwargs.get('uid') == None:
            user = request.user
            if user is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=None)
        else:
            user = User.objects.get(uid=kwargs.get('uid'))
            if user is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="No Such User")
        if(hasattr(user, 'iv')):
            request_list = []
            if hasattr(user.iv, 'received_request'):
                received_list = user.iv.received_request.filter(
                    declined_on__isnull=True, canceled_on__isnull=True)
                request_list.extend(received_list)

            if hasattr(user.iv, 'sent_request'):
                sent_list = user.iv.sent_request.filter(
                    declined_on__isnull=True, canceled_on__isnull=True)
                request_list.extend(sent_list)
            serializer = FriendRequestSerializer(
                request_list, many=True, context={'user': user})
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT, data="No friend")


class FriendRequestView(APIView):
    """
        친구 요청 생성/수락/거절/취소

        ---
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=SendFriendRequestSerialzier, responses={400: 'aleady exists', 201: 'successfully requested'})
    def post(self, request, *args, **kwargs):
        phoneno = request.data['phoneno']
        user = request.user
        requestor_iv = user.iv
        requestee_iv = None
        try:
            requestee_iv = IdentityVerification.objects.get(phoneno=phoneno)
        except ObjectDoesNotExist:
            requestee_iv = IdentityVerification(phoneno=phoneno)
            requestee_iv.save()
        try:
            try:
                veri = requestor_iv.received_request.get(
                    requestor=requestee_iv)
                if veri is not None:
                    raise IntegrityError
            except ObjectDoesNotExist:
                pass
            friend_request = FriendRequest(
                requestor=requestor_iv,
                requestee=requestee_iv
            )
            friend_request.save()
            return Response(status=status.HTTP_201_CREATED, data="successfully requested")
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="aleady exists")

    @swagger_auto_schema(request_body=FriendRequestPatchSerializer, responses={400: 'Bad Request', 201: 'successfully requested'})
    def patch(self, request, *args, **wargs):
        user = request.user
        fr = FriendRequest.objects.get(id=request.data['id'])
        action = request.data['action']

        if action == 'APPROVE':
            fr.approved_on = datetime.datetime.now()
            fr.save()
            return Response(status=status.HTTP_202_ACCEPTED, data="successfully approved")
        elif action == 'DELETE':
            fr.declined_on = datetime.datetime.now()
            fr.save()
            return Response(status=status.HTTP_202_ACCEPTED, data="successfully deleted")
        elif action == 'CANCEL':
            fr.canceled_on = datetime.datetime.now()
            fr.save()
            return Response(status=status.HTTP_202_ACCEPTED, data="successfully canceled")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="action must be APPROVE or DELETE or CANCEL")
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")


class ChatView(APIView):
    """
        채팅

        ---
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(responses={200: ChatListSerializer, 400: 'Bad Request'})
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            serializer = ChatListSerializer(user)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")

    @swagger_auto_schema(request_body=ChatCreateAPISerializer, responses={400: 'Bad Request', 201: 'successfully requested'})
    def post(self, request, *args, **kwargs):
        user = request.user
        target = User.objects.get(uid=request.data['target_uid'])
        data = {
            'sender': user.id,
            'receiver': target.id
        }
        serializer = ChatCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data="successfully requested")
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

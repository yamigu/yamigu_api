from django import template
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *
from file_management.utils.file_helper import save_uploaded_file, rotate_image, get_file_path
from authorization.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError

from django.shortcuts import render
from rest_framework import generics
from django.views.generic import ListView
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from django.db import IntegrityError
import datetime
from fcm_django.models import FCMDevice
from .utils import firebase_message
from .pagination import SmallPagesPagination
import json


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
            if mr.status == MatchRequest.STATUS_CODE_MATCHING or mr.status == MatchRequest.STATUS_CODE_MATCHING_YAMI:
                serializer = MatchRequestSerializer(mr)
                return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_202_ACCEPTED, data="no match request")

    @swagger_auto_schema(request_body=MatchRequestSerializer, responses={201: "successfully requested", 400: "Bad Request"})
    def post(self, request, *args, **kwargs):
        user = request.user
        personnel = request.data['personnel_selected']
        date = request.data['date_selected']
        min_age = request.data['min_age']
        max_age = request.data['max_age']
        rstatus = MatchRequest.STATUS_CODE_MATCHING
        if user.num_of_free >= 1:
            user.num_of_free = user.num_of_free - 1
            rstatus = MatchRequest.STATUS_CODE_MATCHING
        elif user.num_of_yami >= 2:
            user.num_of_yami = user.num_of_yami - 2
            rstatus = MatchRequest.STATUS_CODE_MATCHING_YAMI
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='No yami or free tickets')
        rdata = {
            'free': user.num_of_free,
            'yami': user.num_of_yami
        }
        data = {
            'user': user.id,
            'status': rstatus,
            'personnel_selected': personnel,
            'date_selected': date,
            'min_age': min_age,
            'max_age': max_age,
        }
        serializer = MatchRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user.save()
            return Response(status=status.HTTP_201_CREATED, data=rdata)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @swagger_auto_schema(responses={202: "successfully canceled", 400: "Bad Request"})
    def patch(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, 'match_request'):
            mr = user.match_request.last()
            if mr.status == MatchRequest.STATUS_CODE_MATCHING:
                mr.status = MatchRequest.STATUS_CODE_CANCELED
                mr.save()
                user.num_of_free = user.num_of_free + 1
                user.save()
                rdata = {
                    'free': user.num_of_free,
                    'yami': user.num_of_yami
                }
                return Response(status=status.HTTP_202_ACCEPTED, data=rdata)
            elif mr.status == MatchRequest.STATUS_CODE_MATCHING_YAMI:
                mr.status = MatchRequest.STATUS_CODE_CANCELED
                mr.save()
                user.num_of_yami = user.num_of_yami + 2
                user.save()
                rdata = {
                    'free': user.num_of_free,
                    'yami': user.num_of_yami
                }
                return Response(status=status.HTTP_202_ACCEPTED, data=rdata)
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")


class FeedListView(generics.ListAPIView):
    """
        피드 List

        ---
    """
    permission_classes = [IsAuthenticated]
    pagination_class = SmallPagesPagination

    @swagger_auto_schema(responses={200: FeedListSerializer()})
    def get(self, request, *args, **kwargs):
        user = request.user
        users = User.objects.all().exclude(id=user.id)  # exclude me
        users = users.exclude(is_staff=True)  # exclude manager
        users = users.exclude(nickname__isnull=True)  # exclude no Nickname
        users = users.exclude(iv__isnull=True)  # exclude no IV

        something_id = []
        blocked_id = []
        nofeeds_id = []
        for something in user.something_with.all():
            something_id.append(something.id)
        for blocked in user.disconnected_with.all():
            blocked_id.append(blocked.id)
        for obj in users:
            if(obj.feed.all().count() == 0):
                nofeeds_id.append(obj.id)
        users = users.exclude(id__in=something_id)
        users = users.exclude(id__in=blocked_id)
        users = users.exclude(id__in=nofeeds_id)
        shields = user.shield.all()

        if shields.count() > 0:
            for shield in shields:
                users = users.exclude(iv__phoneno=shield.phoneno)
        serializer = FeedListSerializer(
            users, many=True, context={'user': user})
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


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
        user = request.user
        feed = Feed.objects.get(id=kwargs.get('fid'))
        if user.feed.all().count() == 1:
            return Response(status=status.HTTP_403_FORBIDDEN, data="last feed")
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


class FeedReadView(APIView):
    """
        피드 조회
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        feed = Feed.objects.get(id=kwargs.get('fid'))
        feed_read = None
        feed_read, is_follow = FeedRead.objects.get_or_create(
            user=user, feed=feed)
        feed_read.read_on = datetime.datetime.now()
        feed_read.save()
        return Response(status=status.HTTP_200_OK, data="successfully read")


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
        feeds = feed.user.feed.all()
        like_count = 0
        for feedd in feeds:
            like_count = like_count + feedd.like.all().count()

        if(like_count == 1):
            data = {
                'title': '야미구',
                'content': '축하해요, 누군가 첫번째로 좋아요를 눌렀어요!',
                'clickAction': {
                    'feed': True
                },
            }
            firebase_message.send_push(feed.user.id, data)
        elif(like_count == 3):
            data = {
                'title': '야미구',
                'content':  "{}개의 좋아요를 받았어요, 친구를 찾아보세요!".format(like_count),
                'clickAction': {
                    'feed': True
                },
            }
            firebase_message.send_push(feed.user.id, data)
        elif(like_count == 5):
            data = {
                'title': '야미구',
                'content':  "{}개의 좋아요를 받았어요, 친구를 찾아보세요!".format(like_count),
                'clickAction': {
                    'feed': True
                },
            }
            firebase_message.send_push(feed.user.id, data)
        elif(like_count == 10):
            data = {
                'title': '야미구',
                'content':  "{}개의 좋아요를 받았어요, 친구를 찾아보세요!".format(like_count),
                'clickAction': {
                    'feed': True
                },
            }
            firebase_message.send_push(feed.user.id, data)
        elif(like_count == 20):
            data = {
                'title': '야미구',
                'content':  "{}개의 좋아요를 받았어요, 친구를 찾아보세요!".format(like_count),
                'clickAction': {
                    'feed': True
                },
            }
            firebase_message.send_push(feed.user.id, data)
        elif(like_count == 30):
            data = {
                'title': '야미구',
                'content':  "{}개의 좋아요를 받았어요, 친구를 찾아보세요!".format(like_count),
                'clickAction': {
                    'feed': True
                },
            }
            firebase_message.send_push(feed.user.id, data)

        for target_like in feed.user.like.all():
            if (target_like.value):
                target_like_users.append(target_like.feed.user)

        if user in target_like_users:
            user.something_with.add(feed.user)
            user.save()
            feed_read = None
            try:
                feed_read = FeedRead.objects.get(user=user, feed=feed)
                feed_read.delete()
            except:
                pass
            try:
                feed_read2 = FeedRead.objects.get(
                    user=feed.user, feed=user.feed.last())
                feed_read2.delete()
            except:
                pass

            serializer = ProfileSerializer(feed.user)
            data = {
                'title': '야미구',
                'content':  "서로 좋아요한 친구가 생겼어요! 대화로 친해져보세요.",
                'clickAction': {
                    'feed': True
                },
            }
            firebase_message.send_push(feed.user.id, data)
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
        chat_sent = user.chat_sent.all()
        chat_recv = user.chat_recv.all()

        somethings = user.something_with.all()
        for chat in chat_sent:
            try:
                somethings = somethings.exclude(id=chat.receiver.id)
            except:
                pass
        for chat in chat_recv:
            try:
                somethings = somethings.exclude(id=chat.sender.id)
            except:
                pass
        serializer = ProfileSerializer(somethings, many=True)

        for user_data in serializer.data:
            user_data['has_new'] = False
            user_obj = somethings.get(uid=user_data['uid'])
            if user_obj.feed.last().read.filter(user=user).count() == 0:
                user_data['has_new'] = True
        data = sorted(serializer.data,
                      key=lambda user_data: user_data['has_new'], reverse=True)
        return Response(status=status.HTTP_200_OK, data=data)


class LikeCountView(APIView):
    """
        좋아요 개수

        ---
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            feeds = user.feed.all()
            like_count = 0
            for feed in feeds:
                like_count = like_count + feed.like.all().count()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
        return Response(status=status.HTTP_200_OK, data=like_count)


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
                    declined_on__isnull=True, canceled_on__isnull=True, deleted_on__isnull=True)
                request_list.extend(received_list)

            if hasattr(user.iv, 'sent_request'):
                sent_list = user.iv.sent_request.filter(
                    declined_on__isnull=True, canceled_on__isnull=True, deleted_on__isnull=True)
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
        requestee_iv, is_follow = IdentityVerification.objects.get_or_create(
            phoneno=phoneno)
        requestee_iv.save()
        try:
            try:
                veri = requestor_iv.received_request.get(
                    requestor=requestee_iv)
                if veri is not None:
                    raise IntegrityError
            except ObjectDoesNotExist:
                pass
            friend_request, is_follow2 = FriendRequest.objects.get_or_create(
                requestor=requestor_iv,
                requestee=requestee_iv
            )
            if(friend_request.deleted_on != None):
                friend_request.approved_on = None
                friend_request.deleted_on = None
            if(friend_request.canceled_on != None):
                friend_request.canceled_on = None
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
            friend = fr.requestor.user
            friend.num_of_yami = friend.num_of_yami + 10
            friend.save()
            return Response(status=status.HTTP_202_ACCEPTED, data="successfully approved")
        elif action == 'DECLINE':
            fr.declined_on = datetime.datetime.now()
            fr.save()
            return Response(status=status.HTTP_202_ACCEPTED, data="successfully declined")
        elif action == 'DELETE':
            fr.deleted_on = datetime.datetime.now()
            fr.save()
            return Response(status=status.HTTP_202_ACCEPTED, data="successfully deleted")
        elif action == 'CANCEL':
            fr.canceled_on = datetime.datetime.now()
            fr.save()
            return Response(status=status.HTTP_202_ACCEPTED, data="successfully canceled")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="action must be APPROVE or DELETE or CANCEL")
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")


class ChatDetailView(APIView):
    """
        채팅 디테일

        ---
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        chat = Chat.objects.get(id=kwargs.get('rid'))
        try:
            serializer = ChatDetailSerializer(chat)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))
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

    @swagger_auto_schema(request_body=ChatCreateAPISerializer, responses={400: 'Bad Request', 201: 'roomId'})
    def post(self, request, *args, **kwargs):
        user = request.user
        target = User.objects.get(uid=request.data['target_uid'])
        data = {
            'sender': user.id,
            'receiver': target.id,
            'greet': request.data['greet']
        }
        serializer = ChatCreateSerializer(data=data)
        if serializer.is_valid():

            serializer.save()
            if(user.num_of_yami >= 3):
                user.num_of_yami = user.num_of_yami - 3
                user.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='No yami')
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def patch(self, request, *args, **kwargs):
        user = request.user
        room_id = request.data['room_id']
        action = request.data['action']
        chat = Chat.objects.get(id=room_id)

        if action == 'APPROVE':
            chat.approved_on = datetime.datetime.now()
            chat.save()
            return Response(status=status.HTTP_202_ACCEPTED, data="successfully approved")
        elif action == 'DECLINE':
            chat.declined_on = datetime.datetime.now()
            chat.save()
            return Response(status=status.HTTP_200_OK, data="successfully declined")
        elif action == 'CANCEL':
            chat.canceled_on = datetime.datetime.now()
            chat.canceled_by = user
            chat.save()
            return Response(status=status.HTTP_200_OK, data="successfully canceled")
        elif action == 'CANCEL_CHECK':
            chat.cancel_check = True
            chat.save()
            return Response(status=status.HTTP_200_OK, data="successfully canceled")
        return Response(status=status.HTTP_400_BAD_REQUEST, data='Bad Request')


class ShieldView(APIView):
    """
        아는 사람 피하기

        ---
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=ShieldCreateSerializer, responses={400: 'Bad Request', 201: 'successfully created'})
    def post(self, request, *args, **kwargs):
        user = request.user
        phoneno = None
        belong = None
        try:
            phoneno = request.data.getlist('phoneno')
        except:
            pass
        try:
            belong = request.data['belong']
        except:
            pass
        if phoneno == None and belong == None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")
        data_list = []
        if(phoneno != None and len(phoneno) > 0):
            phoneno = list(set(phoneno))
            for phone in phoneno:
                data = {
                    'user': user.id,
                    'phoneno': phone,
                    'belong': '',
                }
                if user.shield.filter(phoneno=phone).count() == 0:
                    data_list.append(data)
        elif(belong is not None):
            data = {
                'user': user.id,
                'phoneno': '',
                'belong': belong,
            }
            if user.shield.filter(belong=belong).count() == 0:
                data_list.append(data)
        serializer = ShieldSerializer(data=data_list, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @swagger_auto_schema(responses={400: 'Bad Request', 200: ShieldSerializer})
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            serializer = ShieldSerializer(user.shield.all(), many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except:
            pass
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")

    @swagger_auto_schema(request_body=ShieldCreateSerializer, responses={400: 'Bad Request', 200: 'successfully deleted'})
    def patch(self, request, *args, **kwargs):
        user = request.user
        phoneno = None
        belong = None
        try:
            phoneno = request.data['phoneno']
        except:
            pass
        try:
            belong = request.data['belong']
        except:
            pass
        if phoneno != None and phoneno != '':
            if user.shield.filter(phoneno=phoneno).count() > 0:
                shield = user.shield.get(phoneno=phoneno)
                shield.delete()
                return Response(status=status.HTTP_200_OK, data="successfully deleted")
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="No data")
        elif belong != None and belong != '':
            if user.shield.filter(belong=belong).count() > 0:
                shield = user.shield.get(belong=belong)
                shield.delete()
                return Response(status=status.HTTP_200_OK, data="successfully deleted")
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="No data")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")

        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")


class ReportView(APIView):
    """
        신고

        ---
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=ReportCreateSerializer, responses={400: 'Bad Request', 201: 'successfully reported'})
    def post(self, request, *args, **kwargs):
        user = request.user
        who = User.objects.get(uid=request.data['who'])
        why = request.data['why']
        data = {
            'user': user.id,
            'who': who.id,
            'why': why
        }
        serializer = ReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user.disconnected_with.add(who)
            user.save()
            return Response(status=status.HTTP_201_CREATED, data="successfully reported")
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class BlockView(APIView):
    """
        차단

        ---
    """
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=BlockCreateSerializer, responses={400: 'Bad Request', 200: 'successfully blocked'})
    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            who = User.objects.get(uid=request.data['who'])
            user.disconnected_with.add(who)
            user.save()
            return Response(status=status.HTTP_200_OK, data="successfully blocked")
        except:
            pass
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad Request")


class SendPushView(APIView):
    """
        Push 알림 요청
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(uid=request.data['uid'])
            devices = FCMDevice.objects.filter(user=user)
            try:
                data = json.loads(request.data['data'])
            except TypeError:
                data = request.data['data']
            firebase_message.send_push(user.id, data, is_chat=True)
            return Response(status=status.HTTP_200_OK)
        except MultiValueDictKeyError:
            error_msg = json.dumps({
                'message': 'Bad Request',
            })
            return Response(data=error_msg, status=status.HTTP_400_BAD_REQUEST)


class ToggleNotificationView(APIView):
    """
        알림 토글
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        notification = None
        try:
            notification = user.notification
        except ObjectDoesNotExist:
            notification = Notification(user=user)
        serializer = NotificationSerializer(notification)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request, *args, **kwargs):
        user = request.user
        notification = None
        try:
            notification = user.notification
        except ObjectDoesNotExist:
            notification = Notification(user=user)
        toggle_what = request.data['what']
        result = None
        if toggle_what == 'like':
            result = not notification.like
            notification.like = not notification.like
        elif toggle_what == 'like_match':
            result = not notification.like_match
            notification.like_match = not notification.like_match
        elif toggle_what == 'request':
            result = not notification.request
            notification.request = not notification.request
        elif toggle_what == 'match':
            result = not notification.match
            notification.match = not notification.match
        elif toggle_what == 'chat':
            result = not notification.chat
            notification.chat = not notification.chat
        notification.save()
        return Response(status=status.HTTP_200_OK, data=result)


def selectOptions(mr):
    DAY_STRING = ['월', '화', '수', '목', '금', '토', '일']
    PERSONNEL_STRING = ['2:2', '3:3', '4:4']
    DATE_STRING = ['', '', '', '', '', '', '', '금요일', '토요일']

    personnel_int = mr.personnel_selected
    date_int = mr.date_selected
    requested_on = mr.requested_on
    personnel_selected = []
    date_selected = []
    if(personnel_int > 0):
        for i in range(0, 3):
            selected_per = ((personnel_int >> i) & 1) == 1
            if(selected_per):
                personnel_selected.append(PERSONNEL_STRING[i])
    if(date_int > 0):
        selected_friday = (date_int & 128) >> 7 == 1
        selected_saturday = (date_int & 256) >> 8 == 1
        if(selected_friday):
            date_selected.append(DATE_STRING[7])
            date_int = date_int - 128
        if(selected_saturday):
            date_selected.append(DATE_STRING[8])
            date_int = date_int - 256
        day_diff = (today - requested_on).days
        if(day_diff > 0):
            date_int = date_int >> day_diff
        for i in range(0, 7):
            selected_day = ((date_int >> i) & 1) == 1
            if(selected_day):
                date_selected.append(DATE_STRING[i])
    return personnel_selected, date_selected


def MatchRequestQueueView(request):
    DAY_STRING = ['월', '화', '수', '목', '금', '토', '일']
    PERSONNEL_STRING = ['2:2', '3:3', '4:4']
    DATE_STRING = ['', '', '', '', '', '', '', '금요일', '토요일']
    if request.method == "POST":
        woman = MatchRequest.objects.get(id=request.POST['woman'])
        man = MatchRequest.objects.get(id=request.POST['man'])
        now = datetime.datetime.now()

        woman.matched_with = man
        woman.matched_on = now
        # woman.status = MatchRequest.STATUS_CODE_MATCHED

        man.matched_with = woman
        man.matched_on = now
        # man.status = MatchRequest.STATUS_CODE_MATCHED

        man_user = man.user
        woman_user = woman.user

        data = {
            'sender': man_user.id,
            'receiver': woman_user.id,
            'chat_type': 1,
            'approved_on': now,
            'greet': '미팅 주선이 완료되었어요!'
        }
        serializer = ChatCreateSerializer(data=data)
        if serializer.is_valid():
            try:
                chat = serializer.save()
                woman.save()
                man.save()
                push_data = {
                    'title': '야미구',
                    'content': '미팅 주선이 완료되었어요!',
                    'clickAction': {
                        'roomId': chat.id
                    },
                }
                man_personnel_selected, man_date_selected = selectOptions(man)
                woman_personnel_selected, woman_date_selected = selectOptions(
                    woman)
                man_belong = ''
                woman_belong = ''
                man_belong = man_user.bv.belong + \
                    (' ' + man_user.bv.department) if man_user.bv.department != None else ''
                woman_belong = woman_user.bv.belong + \
                    (' ' + woman_user.bv.department) if woman_user.bv.department != None else ''
                man_age = datetime.datetime.today().year - \
                    int(man_user.iv.birthdate[:4]) + 1
                woman_age = datetime.datetime.today().year - \
                    int(woman_user.iv.birthdate[:4]) + 1
                selected_personnel_option = []
                selected_date_option = []
                if(len(man_personnel_selected) == 0):  # 남자 인원 상관없음
                    selected_personnel_option = woman_personnel_selected
                elif(len(woman_personnel_selected) == 0):  # 여자 인원 상관없음
                    selected_personnel_option = man_personnel_selected
                else:
                    man_personnel_selected_set = set(man_personnel_selected)
                    woman_personnel_selected_set = set(
                        woman_personnel_selected)
                    intersection = man_personnel_selected_set & woman_personnel_selected_set
                    selected_personnel_option = list(intersection)

                if(len(man_date_selected) == 0):  # 남자 인원 상관없음
                    selected_date_option = woman_date_selected
                elif(len(woman_date_selected) == 0):  # 여자 인원 상관없음
                    selected_date_option = man_date_selected
                else:
                    man_date_selected_set = set(man_date_selected)
                    woman_date_selected_set = set(
                        woman_date_selected)
                    intersection = man_date_selected_set & woman_date_selected_set
                    selected_date_option = list(intersection)
                selected_personnel_option_string = ''
                selected_date_option = ''
                for idx, option in enumerate(selected_personnel_option):
                    if idx > 0:
                        selected_personnel_option_string = selected_personnel_option_string + ', '
                    selected_personnel_option_string = selected_personnel_option_string + option
                for idx, option in enumerate(selected_date_option):
                    if idx > 0:
                        selected_date_option_string = selected_date_option_string + ', '
                    selected_date_option_string = selected_date_option_string + option
                if(len(selected_personnel_option)):
                    selected_personnel_option_string = "날짜 상관 없음"
                if(len(selected_date_option)):
                    selected_date_option_string = "인원 상관 없음"
                manager_message = "안녕하세요 :) 미팅 주선이 완료되어 채팅방으로 연결되었어요!\n\n남: {} {}살\n여: {} {}살\n- {}\n- {}\n\n서로 매너있는 대화 부탁드려요!\n약속을 잡고 즐거운 미팅하시길 바래요! 감사합니다.".format(
                    man_belong, man_age, woman_belong, woman_age, selected_personnel_option_string, selected_date_option_string)
                firebase_message.send_push(man_user.id, push_data)
                firebase_message.send_message(
                    [man_user, woman_user], chat.id, manager_message)
                # firebase_message.send_push(woman_user.id, data)
            except ValidationError:
                pass
        else:
            print(serializer.errors)
    users = User.objects.all()
    man_requests = []
    woman_requests = []

    today = datetime.datetime.today()
    for i in range(1, 7):
        the_day = today + datetime.timedelta(i)
        DATE_STRING[i-1] = the_day.strftime(
            '%m월%d일') + '({})'.format(DAY_STRING[the_day.weekday()])
    man_count = 0
    woman_count = 0
    for user in users:
        try:
            if(user.match_request.all().count() > 0 and (user.match_request.last().status == MatchRequest.STATUS_CODE_MATCHING or user.match_request.last().status == MatchRequest.STATUS_CODE_MATCHING_YAMI)):
                data = dict()
                data['pk'] = user.match_request.last().id
                data['selected'] = 'false'
                data['nickname'] = user.nickname
                data['belong'] = user.bv.belong
                data['department'] = user.bv.department if user.bv.department != None else ''
                data['min_age'] = user.match_request.last().min_age
                data['max_age'] = user.match_request.last().max_age
                data['age'] = datetime.datetime.today(
                ).year - int(user.iv.birthdate[:4]) + 1
                serializer = ImageSerializer(user.image.last().data)
                data['avata'] = serializer.data['src']
                personnel_int = user.match_request.last().personnel_selected
                date_int = user.match_request.last().date_selected
                requested_on = user.match_request.last().requested_on
                personnel_selected = []
                date_selected = []
                if(personnel_int > 0):
                    for i in range(0, 3):
                        selected_per = ((personnel_int >> i) & 1) == 1
                        if(selected_per):
                            personnel_selected.append(PERSONNEL_STRING[i])
                if(date_int > 0):
                    selected_friday = (date_int & 128) >> 7 == 1
                    selected_saturday = (date_int & 256) >> 8 == 1
                    if(selected_friday):
                        date_selected.append(DATE_STRING[7])
                        date_int = date_int - 128
                    if(selected_saturday):
                        date_selected.append(DATE_STRING[8])
                        date_int = date_int - 256
                    day_diff = (today - requested_on).days
                    if(day_diff > 0):
                        date_int = date_int >> day_diff
                    for i in range(0, 7):
                        selected_day = ((date_int >> i) & 1) == 1
                        if(selected_day):
                            date_selected.append(DATE_STRING[i])
                data['request_info'] = {
                    'personnel': personnel_selected,
                    'date': date_selected
                }

                if(user.iv.gender == 0):
                    data['index'] = woman_count
                    woman_requests.append(data)
                    woman_count = woman_count + 1
                elif(user.iv.gender == 1):
                    data['index'] = man_count
                    man_requests.append(data)
                    man_count = man_count + 1
        except Exception as e:
            print(e)
            pass
    context = {
        'man_requests': man_requests,
        'woman_requests': woman_requests,
    }
    template_name = 'core/matchrequest_queue.html'

    return render(request, template_name, context)

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from authorization.models import *
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from .serializers import *


class MatchRequestView(APIView):
    """
        미팅 주선 신청

        ---
    """
    @swagger_auto_schema(responses={200: MatchRequestSerializer(), 204: "No Match Request"})
    def get(self, request, *args, **kwargs):
        user = User.objects.get(uid='1150721062')

        if(hasattr(user, 'match_request')):
            mr = user.match_request.last()
            data = {
                'requested_on': mr.requested_on,
                'matched_on': mr.matched_on,
                'status': mr.status,
            }
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT, data="no match request")

    @swagger_auto_schema(request_body=MatchRequestSerializer)
    def post(self, request, *args, **kwags):
        user = User.objects.get(uid='1150721062')
        personnel = request.data['personnel']
        date = request.data['date']
        min_age = request.data['min_age']
        max_age = request.data['max_age']
        data = {
            'user': user,
            'status': MatchRequestSerializer.STATUS_CODE_MATCHING,
            'personnel_selected': personnel,
            'date_selected': date,
            'min_age': min_age,
            'max_age': max_age,
        }
        serializer = MatchRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data="successfully requested")
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class FeedListView(APIView):
    """
        피드 List

        ---
    """
    @swagger_auto_schema(responses={200: FeedListSerializer()})
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = FeedListSerializer(users, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FeedView(APIView):
    """
        피드 자세히 보기

        ---
    """
    @swagger_auto_schema(responses={200: FeedSerializer()})
    def get(self, request, *args, **kwargs):
        user = User.objects.get(uid=kwargs.get('uid'))
        serializer = FeedSerializer(user.feed.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class FeedCreateView(APIView):
    """
        피드 생성

        ---
    """
    @swagger_auto_schema(request_body=FeedCreateSerializer(), responses={201: "successfully created"})
    def post(self, request, *args, **kwargs):
        user = User.objects.get(uid='1150721062')
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

        return Response(status=status.HTTP_200_OK, data="successfully created")


class ShieldView(APIView):
    """
        아는 사람 피하기

        ---
    """

    def get(self, request, *args, **kwargs):
        user = User.objects.get(uid='1150721062')
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
        user = User.objects.get(uid='1150721062')
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
    @swagger_auto_schema(responses={200: LikeSerializer()})
    def get(self, request, *args, **kwargs):
        feed = Feed.objects.get(id=kwargs.get('fid'))
        likes = feed.like.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @swagger_auto_schema(responses={201: 'successfully created'})
    def post(self, request, *args, **kwargs):
        feed = Feed.objects.get(id=kwargs.get('fid'))
        user = User.objects.get(uid='1193712316')
        like = Like(user=user, feed=feed)
        like.save()
        return Response(status=status.HTTP_201_CREATED, data="successfully created")


class BothLikeView(APIView):
    """
        서로 좋아요 List

        ---
    """

    def get(self, request, *args, **kwargs):
        user = User.objects.get(uid='1150721062')
        user_like = []
        like_user = []
        user_like_set = {}
        like_user_set = {}
        if(hasattr(user, 'like')):
            user_like_feed_list = user.like.all()
            for like in user_like_feed_list:
                user_like.append(like.feed.user.uid)
            user_like_set = set(user_like)
        if(hasattr(user, 'feed')):
            feed_list_of_user = user.feed.all()
            for feed in feed_list_of_user:
                like_feed_user_list = feed.like.all()
                for like in like_feed_user_list:
                    like_user.append(like.user.uid)
            like_user_set = set(like_user)
        data = {'user_list': user_like_set & like_user_set}
        return Response(status=status.HTTP_200_OK, data=data)


class FriendView(APIView):
    """
        친구

        ---
    """
    @swagger_auto_schema(responses={200: FriendRequestSerializer(), 204: 'No friend'})
    def get(self, request, *args, **kwargs):
        user = User.objects.get(uid='1150721062')
        if(hasattr(user, 'iv')):
            request_list = []
            if hasattr(user.iv, 'received_request'):
                received_list = user.iv.received_request.all()
                request_list.extend(received_list)

            if hasattr(user.iv, 'sent_request'):
                sent_list = user.iv.sent_request.all()
                request_list.extend(sent_list)
            serializer = FriendRequestSerializer(
                request_list, many=True, context={'user': user})
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT, data="No friend")

    @swagger_auto_schema(request_body=SendFriendRequestSerialzier, responses={201: 'successfully requested'})
    def post(self, request, *args, **kwargs):
        phoneno = '01044851971'
        requestor_iv = User.objects.get(uid='1150721062').iv
        requestee_iv = None
        try:
            requestee_iv = IdentityVerification.objects.get(phoneno=phoneno)
        except ObjectDoesNotExist:
            requestee_iv = IdentityVerification(phoneno=phoneno)
            requestee_iv.save()
        friend_request = FriendRequest(
            requestor=requestor_iv,
            requestee=requestee_iv
        )
        friend_request.save()
        return Response(status=status.HTTP_201_CREATED, data="successfully requested")

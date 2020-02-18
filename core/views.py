from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from authorization.models import *
from django.core.exceptions import ObjectDoesNotExist


class MatchRequestView(APIView):
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
            return Response(status=status.HTTP_200_OK, data="no match request")

    def post(self, request, *args, **kwags):
        user = User.objects.get(uid='1150721062')

        match_request = MatchRequest(
            user=user,
            status=MatchRequest.STATUS_CODE_MATCHING
        )
        match_request.save()
        return Response(status=status.HTTP_200_OK, data="successfully requested")


class FeedListView(APIView):
    def get(self, request, *args, **kwargs):
        feed_list = []
        users = User.objects.all()
        for user in users:
            data = {}
            user_data = {}
            user_data['username'] = user.username
            user_data['nickname'] = user.nickname
            if(hasattr(user, 'iv')):
                user_data['birth'] = user.iv.birthdate
            if(hasattr(user, 'bv')):
                user_data['belong'] = user.bv.belong
                user_data['department'] = user.bv.department

            data['user'] = user_data
            data['feeds'] = []
            feed_for_user = user.feed.all()
            for feed in feed_for_user:
                feed_data = {}
                feed_data['img_src'] = feed.image.data.src
                feed_data['datetime'] = feed.created_at
                data['feeds'].append(feed_data)
                # TODO: 좋아요 했는지 여부 추가
            feed_list.append(data)

        return Response(status=status.HTTP_200_OK, data=feed_list)


class ShieldView(APIView):
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
    def get(self, request, *args, **kwargs):
        feed = Feed.objects.get(id=2)
        likes = feed.like.all()
        data = []
        for like in likes:
            data.append({'who': like.user.uid, 'is_unread': like.is_unread})
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, *args, **kwargs):
        feed = Feed.objects.get(id=2)
        user = User.objects.get(uid='1193712316')
        like = Like(user=user, feed=feed)
        like.save()
        return Response(status=status.HTTP_201_CREATED, data="successfully created")


class FriendView(APIView):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(uid='1150721062')
        data = []
        if(hasattr(user, 'iv')):
            request_list = []
            if hasattr(user.iv, 'received_request'):
                received_list = user.iv.received_request.all()
                request_list.extend(received_list)

            if hasattr(user.iv, 'sent_request'):
                sent_list = user.iv.sent_request.all()
                request_list.extend(sent_list)

            for request in request_list:
                temp = {}
                if(request.approved_on is not None):
                    temp['is_approved'] = True
                    friend = None
                    if(request.requestee == user.iv):
                        friend = request.requestor.user
                        birthdate = request.requestor.birthdate
                    else:
                        friend = request.requestee.user
                        birthdate = request.requestee.birthdate
                    friend_info = {
                        'nickname': friend.nickname,
                        'belong': friend.bv.belong,
                        'department': friend.bv.department,
                        'birthdate': birthdate,
                    }
                    temp['user_info'] = friend_info
                else:
                    temp['is_approved'] = False
                    friend_iv = None
                    if(request.requestee == user.iv):
                        friend_iv = request.requestor
                        temp['you_sent'] = False
                    else:
                        friend_iv = request.requestee
                        temp['you_sent'] = True
                    friend_info = {
                        'phoneno': friend_iv.phoneno
                    }
                    temp['user_info'] = friend_info
                data.append(temp)
        return Response(status=status.HTTP_200_OK, data=data)

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
        return Response(status=status.HTTP_200_OK, date="successfully requested")

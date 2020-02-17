from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from authorization.models import *


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
            feed_list.append(data)

        return Response(status=status.HTTP_200_OK, data=feed_list)

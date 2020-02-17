from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from authorization.models import *


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

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
            user_data.name = user.name
            user_data.birth = user.iv.birthdate
            user_data.belong = user.bv.belong
            user_data.department = user.bv.department
            data.user = user_data
            data.feeds = []
            feed_for_user = user.feed.all()
            for feed in feed_for_user:
                feed_data = {}
                feed_data.img_src = feed.image.data.src
                feed_data.text = feed.text.text
                data.feeds.append(feed_data)

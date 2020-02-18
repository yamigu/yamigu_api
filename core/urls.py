# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('match_request/', MatchRequestView.as_view()),
    path('feed/list/', FeedListView.as_view()),
    path('shield/', ShieldView.as_view()),
    path('like/', LikeView.as_view()),
    path('friend/', FriendView.as_view()),
]

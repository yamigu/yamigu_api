# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('match_request/', MatchRequestView.as_view()),
    path('feeds/', FeedListView.as_view()),
    path('feed/<uid>/', FeedView.as_view()),
    path('feed/', FeedCreateView.as_view()),
    path('shield/', ShieldView.as_view()),
    path('like/<fid>/', LikeView.as_view()),
    path('friend/', FriendView.as_view()),
    path('both_like/', BothLikeView.as_view()),
]

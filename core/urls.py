# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('match_request/', MatchRequestView.as_view()),
    path('feeds/', FeedListView.as_view()),
    path('feed/<uid>/', FeedView.as_view()),
    path('feed/<fid>/delete/', FeedDeleteView.as_view()),
    path('feed/<fid>/read/', FeedReadView.as_view()),
    path('feed/', FeedCreateView.as_view()),
    path('shield/', ShieldView.as_view()),
    path('like/<fid>/', LikeView.as_view()),
    path('like/<fid>/cancel/', LikeCancelView.as_view()),
    path('friends/', FriendView.as_view()),
    path('friends/<uid>/', FriendView.as_view()),
    path('friend/', FriendRequestView.as_view()),
    path('both_like/', BothLikeView.as_view()),
    path('chat/', ChatView.as_view()),
    path('chat/detail/<rid>/', ChatDetailView.as_view()),
    path('shield/', ShieldView.as_view()),
    path('report/', ReportView.as_view()),
    path('block/', BlockView.as_view()),
    path('send_push/', SendPushView.as_view()),
    path('toggle_notification/', ToggleNotificationView.as_view()),
    path('like_count/', LikeCountView.as_view()),
]

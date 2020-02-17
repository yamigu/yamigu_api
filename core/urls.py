# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('feed/list/', FeedListView.as_view()),
]

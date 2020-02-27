# authorization/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [
    path('validate/android/', OrderValidateAndroidView.as_view()),
    path('validate/ios/', OrderValidateIOSView.as_view()),
]

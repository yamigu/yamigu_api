# authorization/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
    path('oauth/kakao/', KakaoLoginView.as_view()),
    path('oauth/apple/', AppleLoginView.as_view()),

    path('user/info/', UserInfoView.as_view()),
    path('user/profile_image/', ProfileImageView.as_view()),
    path('user/signup/', SignupView.as_view()),
    path('user/belong_verification/', BelongVerificationView.as_view()),
    path('user/identity_verification/', IdentityVerificationView.as_view()),
]

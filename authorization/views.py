from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from .serializers import UserSerializer
from .models import *


class UserInfoView(APIView):
    """
        유저 정보 API

        ---
    """
    #permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=None)

        uid = user.uid

        try:
            auth.update_user(
                uid=uid,
                display_name=user.nickname,
            )
        except UserNotFoundError:
            auth.create_user(uid=user.uid)

        queryset = User.objects.select_related().get(id=user.id)
        serializer = UserSerializer(queryset, many=False)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ProfileImageView(APIView):
    def get(self, request, *args, **kwargs):
        #user = request.user
        user = User.objects.get(uid='1150721062')
        data = []
        images = user.image.all()
        for image in images:
            data.append({'src': image.data.src, 'is_main': image.is_main})
        return Response(status=status.HTTP_200_OK, data=data)


class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter


class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter

from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from .serializers import *
from .models import *
from file_management.utils.file_helper import save_uploaded_file, rotate_image, get_file_path
from file_management.models import *
from file_management.serializers import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema


class UserInfoView(APIView):
    """
        유저 정보

        ---
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = None
        if kwargs.get('uid') == None:
            user = request.user
            if user is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=None)
        else:
            user = User.objects.get(uid=kwargs.get('uid'))
            if user is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=None)
        serializer = ProfileSerializer(user)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class SignupView(APIView):
    """
        회원 가입

        ---
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.nickname = request.data['nickname']
        user.bv.is_student = True if request.data['is_student'] == 'true' else False
        user.bv.belong = request.data['belong']
        user.bv.department = request.data['department']
        user.bv.save()
        user.save()

        return Response(status=status.HTTP_201_CREATED, data='successfully created')


class ProfileImageView(APIView):
    """
        마이 프로필 사진

        ---
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        data = []
        images = user.image.all()
        for image in images:
            temp = ImageSerializer(image.data).data
            temp['number'] = image.number
            data.append(temp)
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, *args, **kwargs):
        user = request.user
        number = request.data['number']
        TAG = "Profile"
        file_name = save_uploaded_file(request.data['image'], TAG)
        image = Image(
            src=TAG + "/" + file_name
        )
        image.save()
        profile_image = None
        try:
            profile_image = user.image.get(number=number)
            profile_image.data = image
            now = datetime.today()
            profile_image.updated_on = now
        except ObjectDoesNotExist:
            profile_image = ProfileImage(
                user=user,
                data=image,
                number=number
            )
        profile_image.save()
        rotate_image(get_file_path(file_name, TAG))
        serializer = ImageSerializer(image)
        data = serializer.data
        data['number'] = number
        return Response(status=status.HTTP_200_OK, data=data)


class BelongVerificationView(APIView):
    """
        소속 정보

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: BelongVerificationSerializer(), 404: "Not Found"})
    def get(self, request, *args, **kwargs):
        user = request.user
        if(hasattr(user, 'bv')):
            serializer = BelongVerificationSerializer(user.bv)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=BelongVerificationSerializer, responses={200: "successfully uploaded", 400: "Bad Request"})
    def post(self, request, *args, **kwargs):
        user = request.user
        if(hasattr(user, 'bv')):
            TAG = "BV"
            file_name = save_uploaded_file(request.data['image'], TAG)
            image = Image(
                src=TAG + "/" + file_name
            )
            image.save()
            bv_image = BVImage(
                bv=user.bv,
                data=image
            )
            bv_image.save()
            rotate_image(get_file_path(file_name, TAG))

            data = {
                'belong': request.data['belong'],
                'department': request.data['department'],
                'is_student': request.data['is_student'],
            }
            serializer = BelongVerificationSerializer(user.bv, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK, data="successfully uploaded")
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class IdentityVerificationView(APIView):
    """
        본인 인증 정보

        ---
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: IdentityVerificationSerializer(), 404: "Not Found"})
    def get(self, request, *args, **kwargs):
        user = request.user
        if hasattr(user, 'iv'):
            serializer = IdentityVerificationSerializer(user.iv)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=IdentityVerificationSerializer, responses={200: "successfully created", 400: "Bad Request"})
    def post(self, request, *args, **kwargs):
        user = request.user
        data = {
            'user': user.id,
            'realname': request.data['realname'],
            'birthdate': request.data['birthdate'],
            'gender': request.data['gender'],
            'phoneno': request.data['phoneno'],
        }
        iv = IdentityVerification.objects.get(phoneno=request.data['phoneno'])
        if iv is not None:
            serializer = IdentityVerificationSerializer(iv, data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK, data="successfully requested")
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        serializer = IdentityVerificationSerializer(data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data="successfully requested")
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter


class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter

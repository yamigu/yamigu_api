from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from .serializers import UserSerializer, ProfileSerializer
from .models import *
from file_management.utils.file_helper import save_uploaded_file, rotate_image, get_file_path
from file_management.models import *
from file_management.serializers import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class UserInfoView(APIView):
    """
        유저 정보 API

        ---
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=None)

        uid = user.uid

        queryset = User.objects.select_related().get(id=user.id)
        serializer = ProfileSerializer(queryset)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class SignupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.nickname = request.data['nickname']
        user.is_student = True if request.data['is_student'] == 'true' else False
        user.bv.belong = request.data['belong']
        user.bv.department = request.data['department']
        user.bv.save()
        user.save()

        return Response(status=status.HTTP_201_CREATED, data='successfully created')


class ProfileImageView(APIView):
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
            profile_image = ProfileImage.objects.get(number=number)
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
        return Response(status=status.HTTP_200_OK, data="successfully updated")


class BelongVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if(hasattr(user, 'bv')):
            bv = user.bv
            data = {
                'belong': bv.belong,
                'department': bv.department,
                'verified': false
            }
            if(hasattr(bv, image)):
                bv_image = bv.image
                data['image'] = "http://127.0.0.1:8000/media/" + \
                    bv_image.data.src
                data['verified'] = bv_image.is_checked
            return Response(status=status.HTTP_200_OK, data=data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        user = request.user
        if(hasattr(user, 'bv')):
            bv = user.bv
            bv.belong = request.data['belong']
            bv.department = request.data['department']
            bv.save()
            TAG = "BV"
            file_name = save_uploaded_file(request.data['image'], TAG)
            image = Image(
                src=TAG + "/" + file_name
            )
            image.save()
            bv_image = BVImage(
                bv=bv,
                data=image
            )
            bv_image.save()
            rotate_image(get_file_path(file_name, TAG))
            return Response(status=status.HTTP_200_OK, data="successfully uploaded")
        return Response(status=status.HTTP_400_BAD_REQUEST)


class IdentityVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        realname = request.data['name']
        birthdate = request.data['birthdate']
        gender = request.data['gender']
        phoneno = request.data['mobileno']

        iv = IdentityVerification(
            user=user,
            realname=realname,
            birthdate=birthdate,
            gender=gender,
            phoneno=phoneno
        )
        iv.save()
        return Response(status=status.HTTP_200_OK, data="successfully requested")


class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter


class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter

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
from core.models import Feed, FeedImage
from core.serializers import FeedSerializer, FriendListSerializer
from file_management.utils.file_helper import save_uploaded_file, rotate_image, get_file_path
from file_management.models import *
from file_management.serializers import *
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema

import firebase_admin
from firebase_admin import auth
from firebase_admin._auth_utils import UserNotFoundError

import json


def create_token_uid(uid):

    # [START create_token_uid]

    custom_token = auth.create_custom_token(uid)
    custom_token = custom_token.decode('utf-8')
    # [END create_token_uid]
    return custom_token


class FireBaseAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if hasattr(user, 'firebase_token'):
            firebase_token = user.firebase_token
            if (datetime.now() - firebase_token.issued_on.replace(tzinfo=None)).seconds > 3500:
                firebase_token.value = create_token_uid(user.uid)
                firebase_token.issued_on = datetime.now()
                firebase_token.save()
            return Response(status=status.HTTP_200_OK, data=firebase_token.value)
        else:
            firebase_token = FirebaseToken(
                user=user,
                value=create_token_uid(user.uid),
                issued_on=datetime.now()
            )
            firebase_token.save()
            return Response(status=status.HTTP_200_OK, data=firebase_token.value)


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
        data = serializer.data
        if kwargs.get('uid') != None:
            data = dict(data)
            data['friends'] = FriendListSerializer(user).data['friends']
        return Response(status=status.HTTP_200_OK, data=data)


class SignupView(APIView):
    """
        회원 가입

        ---
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.nickname = request.data['nickname']
        user.location = Location.objects.get(name=request.data['location'])
        user.save()
        try:
            user.bv.is_student = True if request.data['is_student'] == 'true' else False
            user.bv.belong = request.data['belong']
            user.bv.department = request.data['department']

            user.bv.save()

        except ObjectDoesNotExist:
            bv = BelongVerification(
                user=user,
                belong=request.data['belong'],
                department=request.data['department'],
                is_student=True if request.data['is_student'] == 'true' else False
            )
            bv.save()

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
        number = int(request.data['number'])
        TAG = "Profile"
        file_name = save_uploaded_file(request.data['image'], TAG)
        image = Image(
            src=TAG + "/" + file_name
        )
        image.save()
        profile_image = None
        is_new = False
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
            if number == 1:
                is_new = True

        profile_image.save()
        rotate_image(get_file_path(file_name, TAG))
        serializer = ImageSerializer(image)
        data = serializer.data
        data['number'] = number

        before = None
        if(hasattr(user, 'feed')):
            before = user.feed.last()

        feed = Feed(
            user=user,
            before=before
        )
        feed.save()
        feed_image = FeedImage(
            feed=feed,
            data=image
        )
        feed_image.save()
        fserializer = FeedSerializer(feed)
        data["feed"] = fserializer.data
        # if is_new:
        #     user.num_of_yami = user.num_of_yami + 5
        #     user.save()
        #     data["bonus"] = 5
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


class IdentityVerificationCreateView(APIView):
    @swagger_auto_schema(request_body=IdentityVerificationSerializer, responses={200: "successfully created", 400: "Bad Request"})
    def post(self, request, *args, **kwargs):
        user = User.objects.get(uid=request.data['uid'])
        data = {
            'user': user.id,
            'realname': request.data['name'],
            'birthdate': request.data['birthdate'],
            'gender': request.data['gender'],
            'phoneno': request.data['mobileno'],
        }
        try:
            iv = IdentityVerification.objects.get(
                phoneno=request.data['mobileno'])
            serializer = IdentityVerificationSerializer(iv, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK, data="successfully requested")
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        except ObjectDoesNotExist:
            serializer = IdentityVerificationSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK, data="successfully requested")
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class YamiView(APIView):
    """
        야미 갯수 정보

        ---
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            return Response(status=status.HTTP_200_OK, data=user.num_of_yami)
        except:
            pass
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Unknown Error")


class FreeTicketView(APIView):
    """
        무료 티켓 정보

        ---
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            return Response(status=status.HTTP_200_OK, data=user.num_of_free)
        except:
            pass
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Unknown Error")


class FCMCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            fcm_device = user.fcmdevice_set.get(
                registration_id=request.data['registration_id'], device_id=request.data['device_id'])
            return Response(status=status.HTTP_200_OK, data="aleady registered device")
        except:
            return Response(status=status.HTTP_204_NO_CONTENT, data="no device registered")


class NicknameValidationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        users = User.objects.filter(nickname=request.data['nickname'])
        if users.count() > 0:
            return Response(status=status.HTTP_409_CONFLICT, data="aleady exists")
        return Response(status=status.HTTP_200_OK, data="available nickname")


class HeightEnterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        height = request.data['height']
        user.height = height
        user.save()
        return Response(status=status.HTTP_200_OK, data="successfully requested")


class LocationEnterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        location_name = request.data['location']
        user.location = Location.objects.get(name=location_name)
        user.save()
        return Response(status=status.HTTP_200_OK, data="successfully requested")


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.auth_token.delete()
        user.save()
        return Response(status=status.HTTP_200_OK, data="successfully requested")


class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        user.auth_token.delete()
        user.delete()
        return Response(status=status.HTTP_200_OK, data="successfully requested")


class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter


class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter

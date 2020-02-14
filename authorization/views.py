from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from .serializers import UserSerializer


class UserInfoView(APIView):
    """
        유저 정보 API
        
        ---
    """
    #permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user is None:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)

        uid = user.uid

        try:
        	auth.update_user(
        		uid=uid,
        		display_name=user.nickname,
     	   	)
        except UserNotFoundError:
            try:
       		    auth.create_user(uid=user.uid, photo_url=user.image)
       	    except ValueError:
       		    auth.create_user(uid=user.uid)
    
        queryset = User.objects.select_related().get(id=user.id)
        serializer = UserSerializer(queryset, many=False)
        return Response(serializer.data)

class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter

# authorization/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from .views import *


urlpatterns = [
    path('accounts/', include('allauth.urls'), name='socialaccount_signup'),
    path('oauth/kakao/', KakaoLoginView.as_view()),
    path('oauth/apple/', AppleLoginView.as_view()),
    path('withdraw/', WithdrawView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('firebase/token/', FireBaseAuthView.as_view()),
    path('user/info/height/', HeightEnterView.as_view()),
    path('user/info/location/', LocationEnterView.as_view()),
    path('user/info/<uid>/', UserInfoView.as_view()),
    path('user/info/', UserInfoView.as_view()),
    path('user/profile_image/', ProfileImageView.as_view()),
    path('user/signup/', SignupView.as_view()),
    path('user/belong_verification/', BelongVerificationView.as_view()),
    path('user/identity_verification/', IdentityVerificationView.as_view()),
    path('user/identity_verification/create/',
         IdentityVerificationCreateView.as_view()),
    path('user/yami/', YamiView.as_view()),
    path('user/free/', FreeTicketView.as_view()),
    path('fcm/check_device/', FCMCheckView.as_view()),
    path('fcm/register_device/',
         FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
    path('validation/nickname/', NicknameValidationView.as_view()),
    path('manager/certificate/user/accept/',
         CertificateAcceptAdminView.as_view()),
    path('manager/certificate/user/decline/',
         CertificateDeclineAdminView.as_view()),
    path('migrate/', MigrateView.as_view()),
    path('migrate_bv/<uid>/', MigrateBVView.as_view()),
    path('migrate_avata/<uid>/', MigrateAvataView.as_view()),
]

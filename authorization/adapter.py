from .models import User

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super(SocialAccountAdapter, self).save_user(
            request, sociallogin, form)
        social_app_name = sociallogin.account.provider.upper()
        if(social_app_name == 'KAKAO'):
            User.objects.create_kakao_user(
                user_pk=user.pk, extra_data=sociallogin.account.extra_data)
        elif(social_app_name == 'APPLE'):
            User.objects.create_apple_user(
                user_pk=user.pk, extra_data=sociallogin.account.extra_data)

    def pre_social_login(self, request, sociallogin):
        try:
            social_app_name = sociallogin.account.provider.upper()
            user = None
            if(social_app_name == 'KAKAO'):
                user = User.objects.get(
                    uid=sociallogin.account.extra_data['id'])
            elif(social_app_name == 'APPLE'):
                user = User.objects.get(
                    uid=str(sociallogin.account.extra_data['sub']).replace('.', ''))
            if user:
                perform_login(request, user, email_verification='optional')
        except User.DoesNotExist:
            user = User.objects.get(id=request.user.id)
            sociallogin.connect(request, user)

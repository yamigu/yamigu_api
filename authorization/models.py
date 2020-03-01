from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext as _
from django.conf import settings
import os
from file_management.models import Image


class UserManager(BaseUserManager):
    def create_user(self, email, username, is_student, uid=None, nickname=None, password=None):
        user = self.model(
            username=username,
            email=email,
            is_student=is_student,
            nickname=nickname,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username=username,
            is_student=False,
            nickname='manager_'+username,
            email=username+'@yamigu.com',
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_kakao_user(self, user_pk, extra_data):
        user = User.objects.get(pk=user_pk)
        user.username = 'kakao-' + \
            extra_data['properties']['nickname'] + str(extra_data['id'])
        user.uid = str(extra_data['id'])
        user.save(using=self._db)
        return user

    def create_apple_user(self, user_pk, extra_data):
        user = User.objects.get(pk=user_pk)
        user.username = 'apple-' + extra_data['sub']
        user.uid = str(extra_data['sub'])
        user.save(using=self._db)
        return user


class Location(models.Model):
    code = models.SmallIntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return '{}({})'.format(self.name, self.code)


class User(AbstractBaseUser, PermissionsMixin):
    uid = models.CharField(max_length=100, null=True, unique=True)
    username = models.CharField(max_length=100, null=True, unique=True)
    nickname = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=70, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    hide_department = models.BooleanField(default=False)
    num_of_yami = models.IntegerField(default=0)
    num_of_free = models.IntegerField(default=0)
    something_with = models.ManyToManyField("self")
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True)
    token = Token

    objects = UserManager()
    USERNAME_FIELD = 'username'


class ProfileImage(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='image')
    data = models.OneToOneField(
        Image, on_delete=models.CASCADE, related_name='profile')
    number = models.SmallIntegerField(default=0)
    updated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.nickname + '\'s {}'.format(self.number)


class BelongVerification(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='bv')
    is_student = models.BooleanField(default=True)
    belong = models.CharField(max_length=255)
    department = models.CharField(max_length=255)


class BVImage(models.Model):
    bv = models.ForeignKey(
        BelongVerification, on_delete=models.CASCADE, related_name='image')
    data = models.OneToOneField(
        Image, on_delete=models.CASCADE, related_name='bv')
    is_checked = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    checked_on = models.DateTimeField(blank=True, null=True)
    declined_on = models.DateTimeField(blank=True, null=True)


class IdentityVerification(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='iv', blank=True, null=True)
    realname = models.CharField(max_length=255, blank=True, null=True)
    birthdate = models.CharField(max_length=8, blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True)
    phoneno = models.CharField(max_length=14, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)


class FirebaseToken(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="firebase_token")
    value = models.CharField(max_length=2048)
    issued_on = models.DateTimeField()

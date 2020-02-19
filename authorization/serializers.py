# party/serializers.py
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CurrentUserDefault, CharField, SerializerMethodField
from django.contrib.auth import get_user_model
from file_management.serializers import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('nickname', 'is_student', 'num_of_yami', 'num_of_free')


class ProfileSerializer(ModelSerializer):
    birthdate = SerializerMethodField('get_birthdate')
    belong = SerializerMethodField('get_belong')
    department = SerializerMethodField('get_department')
    avata = SerializerMethodField('get_avata')

    def get_birthdate(self, user):
        if(hasattr(user, 'iv')):
            return user.iv.birthdate
        return None

    def get_belong(self, user):
        if(hasattr(user, 'bv')):
            return user.bv.belong
        return None

    def get_department(self, user):
        if(hasattr(user, 'bv')):
            return user.bv.department
        return None

    def get_avata(self, user):
        if(hasattr(user, 'image')):
            if(user.image.last() is not None):
                return ImageSerializer(user.image.last().data).data['src']
        return None

    class Meta:
        model = get_user_model()
        fields = ('nickname', 'birthdate', 'belong', 'department', 'avata')

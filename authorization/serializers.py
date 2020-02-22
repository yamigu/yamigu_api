# party/serializers.py
from rest_framework.serializers import ModelSerializer, SerializerMethodField, StringRelatedField, BooleanField, ReadOnlyField
from django.contrib.auth import get_user_model
from file_management.serializers import *
from .models import *


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('nickname', 'is_student', 'num_of_yami', 'num_of_free')


class ProfileSerializer(ModelSerializer):
    birthdate = SerializerMethodField('get_birthdate')
    gender = SerializerMethodField('get_gender')
    belong = SerializerMethodField('get_belong')
    department = SerializerMethodField('get_department')
    avata = SerializerMethodField('get_avata')

    def get_birthdate(self, user):
        if(hasattr(user, 'iv')):
            return user.iv.birthdate
        return None

    def get_gender(self, user):
        if(hasattr(user, 'iv')):
            return user.iv.gender
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
        fields = ('uid', 'nickname', 'birthdate', 'gender',
                  'belong', 'department', 'avata')


class BVImageSerializer(ModelSerializer):
    class Meta:
        model = BVImage
        fiels = '__all__'


class BelongVerificationSerializer(ModelSerializer):
    verified = BooleanField(source='image.is_checked',
                            read_only=True, required=False)

    class Meta:
        model = BelongVerification
        fields = ('is_student', 'belong', 'department', 'verified', 'image')
        extra_kwargs = {'image': {'required': False}}


class IdentityVerificationSerializer(ModelSerializer):
    class Meta:
        model = IdentityVerification
        fields = '__all__'

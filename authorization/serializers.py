# party/serializers.py
from rest_framework.serializers import ModelSerializer, SerializerMethodField, StringRelatedField, BooleanField, ReadOnlyField, CharField
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
    verified = SerializerMethodField('get_verified')
    location = SerializerMethodField('get_location')

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
        try:
            return ImageSerializer(user.image.get(number=1).data).data['src']
        except:
            return None

    def get_verified(self, user):
        if(hasattr(user, 'bv')):
            if(hasattr(user.bv, 'image')):
                if(user.bv.image.count() > 0):
                    if(user.bv.image.last().is_checked):
                        return 2
                    return 1
        return 0

    def get_location(self, user):
        if hasattr(user.location, 'name'):
            return user.location.name
        return None

    class Meta:
        model = get_user_model()
        fields = ('uid', 'nickname', 'birthdate', 'gender',
                  'belong', 'department', 'avata', 'verified', 'location', 'height')


class BVImageSerializer(ModelSerializer):
    class Meta:
        model = BVImage
        fiels = '__all__'


class BelongVerificationSerializer(ModelSerializer):

    verified = SerializerMethodField(
        'get_verified', read_only=True, required=False)
    image = SerializerMethodField('get_image')

    def get_image(self, bv):
        if(hasattr(bv, 'image')):
            if(bv.image.count() > 0):
                serializer = ImageSerializer(bv.image.last().data)
                return serializer.data
        return None

    def get_verified(self, bv):
        if(hasattr(bv, 'image')):
            if(bv.image.count() > 0):
                if(bv.image.last().is_checked):
                    return 2
                return 1
        return 0

    class Meta:
        model = BelongVerification
        fields = ('is_student', 'belong',
                  'department', 'verified', 'image')
        extra_kwargs = {'image': {'required': False}}


class IdentityVerificationSerializer(ModelSerializer):
    class Meta:
        model = IdentityVerification
        fields = '__all__'

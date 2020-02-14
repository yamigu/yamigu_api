# party/serializers.py
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CurrentUserDefault, CharField
from django.contrib.auth import get_user_model

class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'


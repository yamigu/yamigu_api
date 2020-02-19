from rest_framework.serializers import ModelSerializer
from .models import *


class MatchRequestSerializer(ModelSerializer):
    class Meta:
        model = MatchRequest
        fields = "__all__"
        read_only_fields = ('status', 'matched_on')

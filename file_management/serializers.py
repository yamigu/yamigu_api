from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import *


class ImageSerializer(ModelSerializer):
    src = SerializerMethodField('get_src')

    def get_src(self, image):
        if 'http' in image.src:
            return image.src
        return 'http://13.124.126.30:8080/media/' + image.src

    class Meta:
        model = Image
        fields = ('src',)

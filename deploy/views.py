from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import subprocess
import os


class HookView(APIView):
    def post(self, request, *args, **kwargs):
        SCRIPT_PATH = os.path.join(settings.BASE_DIR, 'deploy/hooks.sh')

        payload = request.data['payload']
        ref = payload['ref']
        if ref == 'refs/heads/deploy':
            output = subprocess.run(['bash', SCRIPT_PATH]).stdout
            return Response(status=status.HTTP_200_OK, data=output)

        return Response(status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


import xmlbuilder
import httplib2
import json
import os
import re
import itunesiap

from .models import *
# Create your views here.

products = {
    'yami_10': 10,
    'yami_30': 30,
    'yami_50': 50,
    'yami_100': 100,
}


class OrderValidateAndroidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        payload = json.loads(request.data['payload'])
        product_id = payload['productId']
        purchase_token = payload['purchaseToken']
        transaction_id = payload['transactionId']
        scopes = ['https://www.googleapis.com/auth/androidpublisher']

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            settings.GOOGLE_KEY_STORE, scopes)
        try:
            http = httplib2.Http()
            http_auth = credentials.authorize(http)
            service = build('androidpublisher', 'v3',
                            http=http_auth)
            product = service.purchases().products().get(packageName='com.yamigu.yamigu_app', productId=product_id,
                                                         token=purchase_token)
            result = product.execute()
            order = Order(
                user=user,
                product_id=product_id,
                transaction_id=transaction_id,
            )
            order.save()
            user.num_of_yami = user.num_of_yami + products[product_id]
            user.save()
            return Response(status=status.HTTP_200_OK, data=result)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(e))

        return Response(status=status.HTTP_400_BAD_REQUEST)


class OrderValidateIOSView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_key(re):
        return re.purchase_date_ms

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.data['payload'])
        transaction_id = payload['transactionId']
        raw_data = payload['rawData']

        # for sandbox environment.
        with itunesiap.env.sandbox:
            response = itunesiap.verify(raw_data)
        # response = itunesiap.verify(raw_data)  # base64-encoded data

        # 넘어온 in_app 영수증 리스트에서 구매 시각이 가장 마지막인 영수증을 가져와서 transaction_id를 비교한다.
        # 오름 차순으로 정렬해서 구매시각이 가장 마지막 영수증을 가져옵니다.
        receipts = sorted(response.receipt.in_app, key=self._get_key)
        last_receipt = receipts[len(receipts) - 1]
        if last_receipt.transaction_id != transaction_id:
            #  구매시각이 가장 마지막인 영수증의 transaction_id 가 일치 하지 않는다.
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)

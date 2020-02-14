from django.db import models
from authorization.models import User


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='order', null=True)
    purchased_on = models.DateTimeField(auto_now_add=True)
    refunded_on = models.DateTimeField()

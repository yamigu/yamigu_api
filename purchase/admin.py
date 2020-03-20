from django.contrib import admin
from .models import *
from core.admin import admin_site

# Register your models here.
admin_site.register(Order)

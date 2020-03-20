from django.contrib import admin
from django.urls import path, include
from .models import *
from .views import *


class CustomAdminSite(admin.AdminSite):

    def get_urls(self):
        urls = super(CustomAdminSite, self).get_urls()
        custom_urls = [
            path('core/meetings/',
                 self.admin_view(MatchRequestQueueView)),
        ]
        return urls + custom_urls


admin_site = CustomAdminSite(name='customadmin')


admin_site.register(FriendRequest)
admin_site.register(Shield)
admin_site.register(MatchRequest)
admin_site.register(Feed)
admin_site.register(Like)
admin_site.register(FeedImage)
admin_site.register(FeedText)
admin_site.register(FeedRead)
admin_site.register(Chat)
admin_site.register(Notification)
admin_site.register(Report)

from django.contrib import admin
from django.urls import path, include
from authorization.urls import urlpatterns as auth_url_patterns
from core.urls import urlpatterns as core_url_patterns
from deploy.urls import urlpatterns as deploy_url_patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('authorization/', include(auth_url_patterns)),
    path('core/', include(core_url_patterns)),
    path('deploy/', include(deploy_url_patterns)),
]

from django.contrib import admin
from django.urls import path, include
from authorization.urls import urlpatterns as auth_url_patterns
from core.urls import urlpatterns as core_url_patterns
from deploy.urls import urlpatterns as deploy_url_patterns
from purchase.urls import urlpatterns as purchase_url_patterns
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from core.views import *
from core.admin import admin_site

schema_view = get_schema_view(
    openapi.Info(
        title="yamigu API",
        default_version='v1',
        description="Yamigu Inc.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="khc146@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
)
urlpatterns = [
    path('admin/', admin_site.urls),
    path('admin2/', admin.site.urls),
    path('authorization/', include(auth_url_patterns)),
    path('core/', include(core_url_patterns)),
    path('deploy/', include(deploy_url_patterns)),
    path('purchase/', include(purchase_url_patterns)),
    path('docs/', schema_view.with_ui('redoc',
                                      cache_timeout=0), name='schema-swagger-ui'),
] + staticfiles_urlpatterns()

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)

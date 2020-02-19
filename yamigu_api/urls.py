from django.contrib import admin
from django.urls import path, include
from authorization.urls import urlpatterns as auth_url_patterns
from core.urls import urlpatterns as core_url_patterns
from deploy.urls import urlpatterns as deploy_url_patterns
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

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
    path('admin/', admin.site.urls),
    path('authorization/', include(auth_url_patterns)),
    path('core/', include(core_url_patterns)),
    path('deploy/', include(deploy_url_patterns)),
    path('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(
        cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
                                         cache_timeout=0), name='schema-swagger-ui'),
]

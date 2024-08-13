from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings
import re
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Django Rest API",
      default_version='v1',
      description="Django Rest API for a big enterprise in the oil and gas sector.",
      contact=openapi.Contact(email="pedrobarros232@hotmai.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   path('', include('home.urls')),
   path('admin/', admin.site.urls),
   path('api/', include('custom_auth.urls')),
   path('api/', include('sensor.urls')),
   path('api/health_checker/', include('health_check.urls')),
   path('api/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Django Rest API'
admin.site.index_title = 'Django Rest API Admin'
admin.site.site_title = 'Django Rest API'
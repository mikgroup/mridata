from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import re_path

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'', include('mridata.urls')),
    re_path(r'^accounts/', include('registration.backends.simple.urls')),
    re_path(r'^s3direct/', include('s3direct.urls')),
]

if not settings.USE_AWS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

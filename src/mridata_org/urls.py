from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('mridata.urls')),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^s3direct/', include('s3direct.urls')),
]

if not settings.USE_AWS:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^about$', views.about, name='about'),
    url(r'^api$', views.api, name='api'),
    url(r'^faq$', views.faq, name='faq'),
    url(r'^terms$', views.terms, name='terms'),
    url(r'^upload/ismrmrd$', views.upload_ismrmrd, name='upload_ismrmrd'),
    url(r'^upload/philips$', views.upload_philips, name='upload_philips'),
    url(r'^upload/siemens$', views.upload_siemens, name='upload_siemens'),
    url(r'^upload/ge$', views.upload_ge, name='upload_ge'),
    url(r'^upload/get_temp_credentials$', views.get_temp_credentials, name='get_temp_credentials'),
    url(r'^list$', views.data_list, name='data_list'),
    url(r'^data/(?P<uuid>.+)$', views.data, name='data'),
    url(r'^download/(?P<uuid>[\w-]+)$', views.data_download, name='data_download'),
    url(r'^delete/(?P<uuid>[\w-]+)$', views.data_delete, name='data_delete'),
    url(r'^edit/(?P<uuid>[\w-]+)$', views.data_edit, name='data_edit'),
    url(r'^clear_log$', views.clear_log, name='clear_log'),
    url(r'^check_refresh$', views.check_refresh, name='check_refresh'),
    url(r'^tags$', views.tags, name='tags'),
    url(r'^tag_delete/(?P<uuid>.+)/(?P<tag>.+)$', views.tag_delete, name='tag_delete'),
    url(r'^poll_for_download/(?P<uuid>.+)$', views.poll_for_download, name='poll_for_download')

]

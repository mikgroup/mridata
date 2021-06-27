from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.main, name='main'),
    re_path(r'^about$', views.about, name='about'),
    re_path(r'^api$', views.api, name='api'),
    re_path(r'^faq$', views.faq, name='faq'),
    re_path(r'^terms$', views.terms, name='terms'),
    re_path(r'^upload/ismrmrd$', views.upload_ismrmrd, name='upload_ismrmrd'),
    re_path(r'^upload/philips$', views.upload_philips, name='upload_philips'),
    re_path(r'^upload/siemens$', views.upload_siemens, name='upload_siemens'),
    re_path(r'^upload/ge$', views.upload_ge, name='upload_ge'),
    re_path(r'^upload/get_temp_credentials$', views.get_temp_credentials, name='get_temp_credentials'),
    re_path(r'^list$', views.data_list, name='data_list'),
    re_path(r'^download/(?P<uuid>[\w-]+)$', views.data_download, name='data_download'),
    re_path(r'^delete/(?P<uuid>[\w-]+)$', views.data_delete, name='data_delete'),
    re_path(r'^edit/(?P<uuid>[\w-]+)$', views.data_edit, name='data_edit'),
    re_path(r'^clear_log$', views.clear_log, name='clear_log'),
    re_path(r'^check_refresh$', views.check_refresh, name='check_refresh'),
    re_path(r'^tags$', views.tags, name='tags'),
    re_path(r'^tag_delete/(?P<uuid>.+)/(?P<tag>.+)$', views.tag_delete, name='tag_delete'),
    re_path(r'^search_tag/(?P<tag>.+)$', views.search_tag, name='search_tag'),

]

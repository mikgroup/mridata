from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.data_list, name='data_list'),
    url(r'^about/$', views.about, name='about'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^terms/$', views.terms, name='terms'),
    url(r'^upload_ismrmrd/$', views.upload_ismrmrd, name='upload_ismrmrd'),
    url(r'^upload_philips/$', views.upload_philips, name='upload_philips'),
    url(r'^upload_siemens/$', views.upload_siemens, name='upload_siemens'),
    url(r'^upload_ge/$', views.upload_ge, name='upload_ge'),
    url(r'^data/(?P<uuid>[\w-]+)/$', views.data, name='data'),
    url(r'^data/(?P<uuid>[\w-]+)/download/$', views.data_download, name='data_download'),
    url(r'^data/(?P<uuid>[\w-]+)/delete/$', views.data_delete, name='data_delete'),
    url(r'^data/(?P<uuid>[\w-]+)/edit/$', views.data_edit, name='data_edit'),
    url(r'^temp_data/(?P<uuid>[\w-]+)/delete$', views.temp_data_delete, name='temp_data_delete'),
    url(r'^check_refresh$', views.check_refresh, name='check_refresh'),
]

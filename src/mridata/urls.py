from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.data_list, name='data_list'),
    url(r'^about/$', views.about, name='about'),
    url(r'^info/$', views.info, name='info'),
    url(r'^upload_ismrmrd/$', views.upload_ismrmrd, name='upload_ismrmrd'),
    url(r'^upload_philips/$', views.upload_philips, name='upload_philips'),
    url(r'^upload_siemens/$', views.upload_siemens, name='upload_siemens'),
    url(r'^upload_ge/$', views.upload_ge, name='upload_ge'),
    url(r'^data/(?P<uuid>[\w-]+)/$', views.data, name='data'),
    url(r'^data_description/(?P<uuid>[\w-]+)/$', views.data_description, name='data_description'),
    url(r'^delete/(?P<uuid>[\w-]+)/$', views.data_delete, name='data_delete'),
    url(r'^data/(?P<uuid>[\w-]+)/edit/$', views.data_update_form, name='data_update_form'),
    url(r'^temp_data_delete/(?P<uuid>[\w-]+)/$', views.temp_data_delete, name='temp_data_delete'),
]

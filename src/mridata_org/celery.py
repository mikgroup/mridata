from __future__ import absolute_import
import os
from django.conf import settings
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mridata_org.settings')
app = Celery('mridata_org')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

if settings.DEBUG:
    @app.task(bind=True)
    def debug_task(self):
        print('Request: {0!r}'.format(self.request))

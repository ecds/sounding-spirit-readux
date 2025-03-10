"""
Celery config for ingest tasks.
"""
import os
from celery import Celery
from django.conf import settings
# import config.settings.local as settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
app = Celery('apps.iiif.manifest', result_extended=True)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
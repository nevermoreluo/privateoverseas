# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'overseas.settings')

from django.conf import settings

# fix error AppRegistryNotReady
# http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
import django
django.setup()

app = Celery('overseas')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore
import time
import hashlib
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from overseas.models.access import InfUser


def get_token():
    timestamp = time.time()
    data = '{}{}'.format(timestamp, settings.SECRET_KEY).encode('utf8')
    return (int(timestamp), hashlib.md5(data).hexdigest())


def get_passwd(passwd):
    return hashlib.md5('{}{}'.format(passwd, settings.SECRET_KEY).encode('utf8')).hexdigest()


def check_passwd(login_email, password, reset_token=False):
    passwd = hashlib.md5('{}{}'.format(password, settings.SECRET_KEY).encode('utf8')).hexdigest()
    try:
        user = InfUser.objects.get(login_email=login_email, password=passwd)
    except ObjectDoesNotExist:
        return False, None
    if reset_token:
        user.last_login, user.token = get_token()
        user.save()
    return True, user

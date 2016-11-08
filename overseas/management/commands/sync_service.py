# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

from utils.level3_info import sync_service
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        sync_service()

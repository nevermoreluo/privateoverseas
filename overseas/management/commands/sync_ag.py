# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

from django.core.management.base import BaseCommand

import logging

from utils.level3_api import Level3
from overseas.models.access import AccessGroup

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        ag = Level3.accessGroups()
        agid = ag.get('id')
        access_group, created = AccessGroup.objects.get_or_create(agid=agid)
        access_group.name = ag.get('name', '')
        access_group.desc = ag.get('description', '')
        access_group.api_correlation_id = ag.get(
            'apiCorrelationId', '')
        access_group.save()
        if created:
            logger.info('Create an access group: {}'.format(ag['id']))
        else:
            logger.info('Access group {} already exist, update desc info.'.format(ag['id']))

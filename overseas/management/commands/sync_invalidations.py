# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

from django.core.management.base import BaseCommand

from datetime import datetime
from utils.level3_api import Level3
from overseas.models.access import NetworkIdentifiers
from overseas.models.invalidations import Invalidations


class Command(BaseCommand):

    def handle(self, *args, **options):
        nis = NetworkIdentifiers.objects.filter(active=True).all()
        for ni in nis:
            resp = Level3.invalidations(str(ni), method='GET')
            try:
                invalidations = resp['accessGroup']['services']['service']['networkIdentifiers'][
                    'ni']['invalidations']['invalidation']
            except:
                response_data = {'err': 501,
                                 'message': 'Unexcept resp %s' % str(resp)}
                break
            invalidations = invalidations if isinstance(
                invalidations, list) else [invalidations]
            ni_name = ni.ni
            for inval in invalidations:
                taskid = inval.get('@id', '')
                if not taskid:
                    break
                inv, created = Invalidations.objects.get_or_create(taskid=taskid)
                if created:
                    inv.force = '@AG' in taskid
                inv.percentComplete = inval.get('percentComplete', '0')
                inv.time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                urls = inval.get('paths', {}).get('path', [])
                urls = urls if isinstance(urls, list) else [urls]
                inv.url = '|'.join(['http://' + ni_name + url for url in urls])
                inv.save()

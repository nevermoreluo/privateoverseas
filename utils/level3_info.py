# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# Date: 2016-09-04
# auth: nevermore


from datetime import datetime
from django.utils import timezone
from django.conf import settings

import time
import logging

from utils.level3_api import Level3, ForbiddenException

from overseas.models.access import (NetworkIdentifiers, City,
                                    NiInfo, AccessGroup, Service)

logger = logging.getLogger(__name__)


def _create_ni_info(active, data):
    logger.info('begin update data from level3 ')
    net = active.split('/')[-1]
    n = NetworkIdentifiers.objects.get(ni=net)
    time_span = settings.LEVEL3_TIME_SPAN * 60.0
    try:
        points = data.select('data > point')
    except:
        print(data, active)
        return
    for point in points:
        t = point.get('id')
        if not t:
            continue
        metro_data = point.select('item > regions > region > metros > metro')
        tamp = int(time.mktime(time.strptime(t, "%m/%d/%Y %H:%M:%S"))) + 8 * 3600
        my_datetime = timezone.make_aware(
            datetime.fromtimestamp(tamp), timezone.get_current_timezone())
        for data in metro_data:
            city_en = ''.join(data.get('id', '').split()).replace('_', '')
            city, created = City.objects.get_or_create(name_en=city_en)
            ni, created = NiInfo.objects.get_or_create(
                ni=n, timestamp=tamp, city=city)

            requests = int(getattr(data.find('requests'), 'text', 0))
            # GB -> Byte 1024*1024*1024=1073741824
            volume = int(float(getattr(data.find('volume'), 'text', 0)) * 1073741824)
            # 返回值为Mbps
            throughput = float(getattr(data.find('averagethroughput'), 'text', 0))
            bandwidth = int(volume * 8 / time_span)
            message = 'create ni info %s' if created else 'update ni info %s'
            ni.time = my_datetime
            ni.volume = volume or ni.volume
            ni.requests = requests or ni.requests
            ni.throughput = throughput or ni.throughput
            ni.bandwidth = bandwidth or ni.bandwidth

            ni.save()
            logger.info(message % str(ni))


def level3_sync(active, timestamp, timedelta):
    time_span = settings.LEVEL3_TIME_SPAN * 60.0
    timestamp = int(timestamp / time_span) * time_span
    try:
        data = Level3.usage_report(active, timestamp,
                                   timestamp + timedelta, json=False, bs4=True,
                                   options={'geo': 'metro'})
        _create_ni_info(active, data)
    except RuntimeError:
        logger.info(('No usage data was found'
                     ' for specified criteria %s.') % timestamp)
        return
    except ForbiddenException:
        time.sleep(15)
        level3_sync(active, timestamp, timedelta)


def level3_sync_5min(active, timestamp, span=None):
    time_span = settings.LEVEL3_TIME_SPAN * 60.0
    level3_sync(active, timestamp - time_span, time_span)


def level3_sync_hourly(active, timestamp, span=None):
    timestamp = int(timestamp / 3600) * 3600
    level3_sync(active, timestamp - 7200, 7200)


def level3_sync_8hour(active, timestamp, span=None):
    timestamp = int(timestamp / 28800) * 28800
    level3_sync(active, timestamp - 36300, 36300)


def sync_daily(active, timestamp, span=1):
    time_span = settings.LEVEL3_TIME_SPAN * 60.0
    day_s = 60 * 60 * 24
    timestamp = int(timestamp / time_span) * time_span
    for i in range(span):
        level3_sync(active, timestamp, day_s)
        timestamp += day_s


def sync_service():
    ags = AccessGroup.objects.all()
    for ag in ags:
        soup = Level3.servicesHierarchy(str(ag.agid))
        ni_resources = soup.select('accessgroup > services > service > networkidentifiers')

        for netid in ni_resources:
            serviceResources = [
                (i.serviceresource.text, i.active.text == 'Y') for i in netid.select('ni')]
            # active = netid.get('ni', {}).get('active') == 'Y'
            for serviceResource, active in serviceResources:
                _, agid, service, ni = serviceResource.split('/')
                ser, created = Service.objects.get_or_create(
                    scid=service, access_group=ag)
                if created:
                    logger.info('Created service %s' % service)
                ni, created = NetworkIdentifiers.objects.get_or_create(
                    ni=ni, service=ser)
                if created:
                    logger.info('Created NetworkIdentifiers %s' % ni)
                ni.active = active
                ni.save()

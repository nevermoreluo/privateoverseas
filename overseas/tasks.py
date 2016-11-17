# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# Date: 2016-09-01
# auth: nevermore

import os
import time
import glob
import gzip
import datetime
import logging
from multiprocessing.dummy import Pool as ThreadPool

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned

from overseas.celery import app
from overseas.models.access import NetworkIdentifiers, NiInfo
from utils.level3_info import level3_sync_5min, sync_service, sync_daily, level3_sync_hourly, level3_sync_8hour

logger = logging.getLogger(__name__)


@app.task
def sync_level3():
    sync_service()
    # base_threadpool_sync(level3_sync_5min, int(time.time()))
    # useage report 无法实时返回暂时注销
    # nis = NetworkIdentifiers.get_level3_ni()
    # for ni in nis:
    #     level3_sync_5min(str(ni), int(time.time()))


@app.task
def sync_level3_log(days=1):
    cmd = ('/usr/bin/rsync -vzrtopg --progress '
           '--password-file=/var/log/rsync_level3/rsyncd.pas '
           'lingrui@202.55.17.10::lingrui_home/* '
           '%s') % settings.RSYNC_LOG_DIR
    os.system(cmd)

    sync_service()
    nis = NetworkIdentifiers.get_level3_ni()
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=days)).strftime("%Y/%m/%d/")
    for ni in nis:
        nidir = settings.RSYNC_DAILY_DIR + ni.ni
        yesterday_file = yesterday + ni.ni
        abs_filename = settings.RSYNC_LOG_DIR + yesterday_file
        if os.path.exists(abs_filename):
            zipfiles = sorted(glob.glob(abs_filename + '/*.gz'))
            if zipfiles:
                gzfile = '%s/%s.log.gz' % (nidir, yesterday_file.replace('/', '-', 4))
                with gzip.GzipFile(gzfile, mode='ab+', compresslevel=9) as wf:
                    for zipfile in zipfiles:
                        with gzip.GzipFile(zipfile, mode="rb") as f:
                            wf.writelines(sorted(f.readlines()[2:]))


class BaseSync(object):
    def __init__(self, func, timestamp, span=1):
        self.func = func
        self.timestamp = timestamp
        self.span = span

    def __call__(self, ni):
        try:
            self.func(str(ni), self.timestamp, span=self.span)
        except MultipleObjectsReturned:
            nis = NiInfo.objects.filter(timestamp__gte=self.timestamp,
                                        ni=ni).all()
            nis_arg = [(ni.ni, ni.timestamp, ni.city) for ni in nis]
            s = {i for i in nis_arg if nis_arg.count(i) > 1}
            mult_nis = [list(NiInfo.objects.filter(ni=n, city=c, timestamp=t).all()) for n, t, c in s]
            [i[0].delete() for i in mult_nis]
            self.func(str(ni), self.timestamp, span=self.span)


def base_threadpool_sync(func, timestamp, span=1, workers=3):
    sync_service()

    # Make the Pool of workers
    pool = ThreadPool(workers)
    nis = NetworkIdentifiers.get_level3_ni()
    base_sync = BaseSync(func, timestamp, span=span)
    logger.info('Begin threadpool workers!')
    results = pool.map(base_sync, nis)
    # close the pool and wait for the work to finish
    pool.close()
    pool.join()
    logger.info('Finsh threadpool workers!')


@app.task
def sync_level3_daily():
    sync_service()
    # nis = NetworkIdentifiers.get_level3_ni()
    timestamp = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d 08:00:00', time.localtime(time.time())), '%Y-%m-%d %H:%M:%S'))) - 86400
    base_threadpool_sync(sync_daily, timestamp, span=1)
    # for ni in nis:
    #     try:
    #         sync_daily(str(ni), timestamp, span=1)
    #     except MultipleObjectsReturned:
    #         nis = NiInfo.objects.filter(timestamp__gte=timestamp,
    #                                     ni=ni).all()
    #         nis_arg = [(ni.ni, ni.timestamp, ni.city) for ni in nis]
    #         s = {i for i in nis_arg if nis_arg.count(i) > 1}
    #         mult_nis = [list(NiInfo.objects.filter(ni=n, city=c, timestamp=t).all()) for n, t, c in s]
    #         [i[0].delete() for i in mult_nis]
    #         sync_daily(str(ni), timestamp, span=1)


@app.task
def sync_level3_hourly():
    sync_service()
    base_threadpool_sync(level3_sync_hourly, int(time.time()))
    # nis = NetworkIdentifiers.get_level3_ni()
    # for ni in nis:
    #     level3_sync_hourly(str(ni), int(time.time()))


@app.task
def sync_level3_8hourly():
    sync_service()
    base_threadpool_sync(level3_sync_8hour, int(time.time()))
    # nis = NetworkIdentifiers.get_level3_ni()
    # for ni in nis:
    #     level3_sync_8hour(str(ni), int(time.time()))


# def base_sync(ni, timestamp=1477958400, span=14):
#     try:
#         sync_daily(str(ni), timestamp, span=span)
#     except MultipleObjectsReturned:
#         nis = NiInfo.objects.filter(timestamp__gte=timestamp,
#                                     ni=ni).all()
#         nis_arg = [(ni.ni, ni.timestamp, ni.city) for ni in nis]
#         s = {i for i in nis_arg if nis_arg.count(i) > 1}
#         mult_nis = [list(NiInfo.objects.filter(ni=n, city=c, timestamp=t).all()) for n, t, c in s]
#         [i[0].delete() for i in mult_nis]
#         sync_daily(str(ni), timestamp, span=span)


@app.task
def sync_level3_temp():
    base_threadpool_sync(sync_daily, 1475280000, span=15, workers=3)
    # sync_service()
    # from multiprocessing.dummy import Pool as ThreadPool
    # # Make the Pool of workers
    # pool = ThreadPool(6)
    # nis = NetworkIdentifiers.get_level3_ni()
    # results = pool.map(base_sync, nis)
    # #close the pool and wait for the work to finish 
    # pool.close()
    # pool.join()




# @app.task
# def sync_ipip():
#     # NOTE the stream=True parameter
#     r = requests.get(settings.IPIP_DOWNLOAD_API_URL, stream=True)
#     with open(settings.IPIP_DATX_PATH, 'wb') as f:
#         for chunk in r.iter_content(chunk_size=1024):
#             # filter out keep-alive new chunks
#             if chunk:
#                 f.write(chunk)
#                 # f.flush() commente
#     return settings.IPIP_DATX_PATH

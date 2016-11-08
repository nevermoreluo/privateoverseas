#!/usr/bin/env python
# _*_ coding:utf8 _*_

import os
import time
from overseas.models.access import NiInfo, NetworkIdentifiers, Tan14User, CDN, City


def m(startTime, endTime, domains):
    s = time.time()
    cs = City.objects.all()
    rel = []
    for c in cs:
        nis = NiInfo.objects.get_info(startTime, endTime, domains).filter(city=c).all()
        if nis:
            rel.append({'requests': sum(ni.requests for ni in nis),
                        'vaule': sum(ni.volume for ni in nis),
                        'city': c.name_en,
                        'city_cn': c.name_cn})
    e = time.time()
    print(rel)
    print(e - s)

def old(startTime, endTime, domains):
    s = time.time()
    rel = NiInfo.get_niinfo_date(startTime, endTime, domains, 'volume', 'city')
    e = time.time()
    print(rel)
    print(e - s)


if __name__ == '__main__':
    domains = ['cdn.exrqs.com', 'dw.sd2gf54.com', '*.kakabifen.com']
    startTime = 1476720000
    endTime = 1476806399
    print('=' * 30)
    print('Old:')
    old(startTime, endTime, domains)
    print('=' * 30)
    print('New:')
    m(startTime, endTime, domains)
    
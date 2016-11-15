# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore
import os
import requests
import logging
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from utils.mail import Mail

logger = logging.getLogger(__name__)


class Tan14User(models.Model):
    login_email = models.CharField(_(u'登录邮箱'), max_length=100, unique=True)
    password = models.CharField(_(u'密码'), max_length=200)
    token = models.CharField(_(u'口令'), max_length=200, blank=True, null=True)
    last_login = models.PositiveIntegerField(_(u'最后登录时间戳'),
                                             blank=True, null=True)
    operate_right = models.BooleanField(_(u'是否可刷新、预加载'), default=True)
    record_date = models.DateTimeField(_(u'注册日期'), auto_now_add=True)
    active = models.BooleanField(_(u'是否可用'), default=True)

    @property
    def join_date(self):
        return (self.record_date + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')

    def set_password(self, password, remove_key=False):
        from utils.user_tools import get_passwd
        self.password = get_passwd(password)
        if remove_key:
            self.token = None
        self._set_ps = True
        self.save()

    def save(self, *args, **kw):
        if not hasattr(self, '_set_ps'):
            if self.pk and (self.password == Tan14User.objects.get(pk=self.pk).password):
                pass
            else:
                from utils.user_tools import get_passwd
                self.password = get_passwd(self.password)
                self._set_ps = True
        msg = 'modify mcuser %s' if self.pk else 'created mcuser %s'
        logger.info(msg % self.login_email)
        return super(Tan14User, self).save(*args, **kw)

    def __str__(self):
        return self.login_email

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))

    class Meta:
        verbose_name = u"用户"
        verbose_name_plural = u"用户"

    def level3_domains(self):
        return list({i.ni.ni for i in self.cdn_set.filter(ni__service_id__isnull=False)})

    def json(self):
        return {'err': 0,
                'user': self.login_email,
                'operate_right': self.operate_right,
                'token': self.token,
                'last_login': self.last_login}

    def _json(self):
        cdns = self.cdn_set.all()
        cdn_names = list(set(cdn.cdn_name for cdn in cdns))

        results = []
        for cdn_name in cdn_names:
            c = cdns.filter(cdn_name=cdn_name).all()
            results += [{'cdn': cdn_name,
                         'domains': [{'domain': getattr(cdn.ni, 'ni', ''),
                                      'state': 'Active' if getattr(cdn.ni, 'active', '') else 'Delete'} for cdn in c if getattr(cdn.ni, 'ni', '')]}]
        return {'err': 0,
                'user': self.login_email,
                'operate_right': self.operate_right,
                'results': results}

    def cdn_json(self):
        return {'err': 0,
                'user': self.login_email,
                'operate_right': self.operate_right,
                'cdns': list(set(map(str, self.cdn_set.all())))}


CDN_TYPE = (
    ('level3', 'level3'),
    ('tan14', 'tan14'),
)


class CDN(models.Model):
    cdn_name = models.CharField(verbose_name=u'CDN', max_length=100, choices=CDN_TYPE)
    tan14_user = models.ForeignKey(Tan14User, blank=True, null=True)
    ni = models.ForeignKey('NetworkIdentifiers', verbose_name=u'域名', blank=True, null=True)
    active = models.BooleanField(verbose_name=u'可用', default=True)

    def clean(self):
        cdns = [(c.cdn_name, c.ni.ni) for c in CDN.objects.filter(tan14_user=self.tan14_user)]
        if self.pk is None:
            if (self.cdn_name, getattr(self.ni, 'ni', '')) in cdns:
                raise ValidationError(_(u'无法保存重复的域名,请检查后再保存'))
        else:
            c = CDN.objects.get(pk=self.pk)
            old_data = (self.cdn_name, getattr(self.ni, 'ni', ''))
            if old_data != (c.cdn_name, getattr(c.ni, 'ni', '')) and cdns.count(old_data) > 0:
                raise ValidationError(_(u'无法保存重复的域名,请检查后再保存'))

    def __str__(self):
        return self.cdn_name

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))

    def json(self):
        return {'err': 0,
                'cdn': self.cdn_name,
                'domain': self.ni,
                'user': self.tan14_user,
                'id': self.pk}


class AccessGroup(models.Model):

    agid = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=200)
    api_correlation_id = models.CharField(max_length=100)
    active = models.BooleanField(_(u'是否可用'), default=True)

    def __str__(self):
        return str(self.agid)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))


class Service(models.Model):

    scid = models.CharField(max_length=50, unique=True)
    access_group = models.ForeignKey(AccessGroup)
    active = models.BooleanField(_(u'是否可用'), default=True)

    def __str__(self):
        return '/'.join((str(self.access_group), self.scid))

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))


class NetworkIdentifiers(models.Model):
    ni = models.CharField(max_length=100, unique=True)
    service = models.ForeignKey(Service, blank=True, null=True)
    active = models.BooleanField(_(u'是否可用'), default=True)

    def save(self, *args, **kw):
        if not self.pk and self.service:
            # This code only happens if the objects is
            # not in the database yet. Otherwise it would
            # have pk
            # makedir only if object created and belong to level3
            # create rsync log dir
            os.makedirs(settings.RSYNC_DAILY_DIR + self.ni)
        super(NetworkIdentifiers, self).save(*args, **kw)

    def __str__(self):
        return '%s/%s' % (str(self.service), self.ni)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))

    @classmethod
    def all_ni(cls):
        return [ni.ni for ni in cls.objects.all()]

    @classmethod
    def get_level3_ni(cls):
        return cls.objects.filter(service_id__isnull=False, active=True).all()


class NiInfoManager(models.Manager):

    def get_queryset(self):
        return super(NiInfoManager, self).get_queryset()

    def get_info(self, startTime, endTime, data_domains):
        return self.get_queryset().only('volume', 'bandwidth', 'city', 'ni', 'timestamp').filter(timestamp__gte=startTime,
                                          timestamp__lte=endTime,
                                          ni__ni__in=data_domains)


class NiInfo(models.Model):
    requests = models.PositiveIntegerField(default=0)
    throughput = models.FloatField(default=0)
    bandwidth = models.PositiveIntegerField(default=0)
    volume = models.FloatField(default=0)
    time = models.DateTimeField(null=True)
    timestamp = models.PositiveIntegerField(default=0)
    ni = models.ForeignKey(NetworkIdentifiers)
    city = models.ForeignKey('City', blank=True, null=True)

    objects = NiInfoManager()

    def __str__(self):
        return '/'.join((str(self.ni), str(self.time)))

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, '/'.join((self.ni.ni, str(self.time))))

    @classmethod
    def get_niinfo_date(cls, startTime, endTime, data_domains, attr, key):
        time_span = settings.LEVEL3_TIME_SPAN * 60
        startTime = int(startTime / time_span) * time_span
        endTime = int(endTime / time_span) * time_span

        if key != 'city':
            nis = cls.objects.get_info(startTime, endTime, data_domains).values()
            # use python Comprehensions speed-up of response
            # fix request timeout error when get a long period of time
            ni_results = [(ni.get(key.lower(), 0), ni.get(attr, 0))
                          for ni in nis]
            # sum countries value for each timeStamp
            userful_dict = {i: sum(va for ke, va in ni_results if ke == i) for i in
                        set(t for t, v in ni_results)}

            # build timeStamp,value dict default value 0
            all_results = {t: 0 for t in range(startTime, endTime + 1, time_span)}

            # update userful value
            all_results.update(userful_dict)
            # build results
            results = [{key: k, 'value': v}
                       for k, v in sorted(all_results.items(), key=lambda x: x[0])]


            # # mix domains resp_data
            # nis = cls.objects.get_info(startTime, endTime, data_domains).all()
            # # use python Comprehensions speed-up of response
            # # fix request timeout error when get a long period of time
            # ni_results = [(getattr(ni, key.lower(), 0), getattr(ni, attr, 0))
            #               for ni in nis]
            # # sum countries value for each timeStamp
            # userful_dict = {i: sum(va for ke, va in ni_results if ke == i) for i in
            #             set(t for t, v in ni_results)}

            # # build timeStamp,value dict default value 0
            # all_results = {t: 0 for t in range(startTime, endTime + 1, time_span)}

            # # update userful value
            # all_results.update(userful_dict)
            # # build results
            # results = [{key: k, 'value': v}
            #            for k, v in sorted(all_results.items(), key=lambda x: x[0])]
        else:
            cs = City.objects.all()
            results = []
            for c in cs:
                nis = NiInfo.objects.get_info(startTime, endTime, data_domains).filter(city=c).all()
                if nis:
                    results.append({'requests': sum(ni.requests for ni in nis),
                                    'value': sum(getattr(ni, attr, 0) for ni in nis),
                                    'city': c.name_en,
                                    'city_cn': c.name_cn})
        return results

    class Meta:
        verbose_name = u"信息"
        verbose_name_plural = u"信息"


class City(models.Model):
    name_en = models.CharField(max_length=100)
    name_cn = models.CharField(max_length=100, null=True)
    country_en = models.CharField(max_length=100, null=True)
    country_cn = models.CharField(max_length=100, null=True)

    def __gt__(self, other):
        return self.name_en > other.name_en

    def __lt__(self, other):
        return self.name_en < other.name_en

    def save(self, *args, **kwargs):
        if not self.name_cn:
            try:
                youdao = requests.get(
                    ''.join([settings.YOUDAO_BASEURL, self.name_en])).json()
                name_cn = youdao.get('translation', [])[0]
                if any(u'\u4e00' <= char <= u'\u9fff' for char in name_cn):
                    self.name_cn = name_cn
                else:
                    raise RuntimeError('Cannot translate %s to chinese!' % self.name_en)
            except:
                Mail.send(['lelun.chen@maichuang.net', '656763371@qq.com'],
                           'Failure Overseas City Translation',
                           'Youdao cannot translation %s.' % self.name_en)
        # need add method for country map
        # if not self.country_cn:
        super(City, self).save(*args, **kwargs)

    def __str__(self):
        return self.name_en

    def __repr__(self):
        return '<City: %s[%s]>' % (self.name_en, self.name_cn)

    class Meta:
        verbose_name = u"城市"
        verbose_name_plural = u"城市"

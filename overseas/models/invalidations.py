# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

from django.db import models


class Invalidations(models.Model):
    taskid = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    percentComplete = models.CharField(max_length=100, default='0')
    force = models.BooleanField(default=False)
    time = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.url

    def __repr__(self):
        return '<%s: %s[%s]:%s>' % (self.__class__.__name__, str(self), self.taskid, self.percentComplete)

    class Meta:
        verbose_name = u"刷新任务"
        verbose_name_plural = u"刷新任务"

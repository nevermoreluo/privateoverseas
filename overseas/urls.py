# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

"""overseas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from overseas.views import (FluxsView, BandwidthsView, NetworkId,
                            RefreshView, RefreshListView, UserDomainView,
                            UserCDNView, UserView,
                            LogDownloadView, LogListView,
                            LoginView, LogoutView, LoginCheckView, abtest)


admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    # 标准admin管理系统
    url(r'^', admin.site.urls),
    # 登陸
    url(r'^level3/login$', LoginView.as_view(), name='login'),
    # 注銷
    url(r'^level3/logout$', LogoutView.as_view(), name='logout'),
    # 賬號是否登陸
    url(r'^level3/logincheck$', LoginCheckView.as_view(), name='logincheck'),
    # 查询带宽接口
    url(r'^level3/bandwidths$', BandwidthsView.as_view(), name='bandwidths'),
    # 查询流量接口，按时间
    url(r'^level3/fluxs$', FluxsView.as_view(), name='fluxs'),

    # 查询流量区域分布接口
    url(r'^level3/fluxs/area$', FluxsView.as_view(), {'key': 'city'}, name='fluxs_area'),
    # 查询流量区域分布接口
    url(r'^level3/bandwidths/area$', BandwidthsView.as_view(), {'key': 'city'}, name='bandwidths_area'),

    # 获取所有域名接口
    url(r'^level3/domains', NetworkId.as_view(), name='ni'),
    # 刷新接口
    url(r'^level3/refresh$', RefreshView.as_view(), name='refresh'),
    # 获取刷新任务状态接口
    url(r'^level3/refresh_list', RefreshListView.as_view(), name='refresh_list'),
    # 预加载接口
    url(r'^level3/preload$', RefreshView.as_view(), {'force': 1}, name='preload'),
    # 获取预加载任务状态接口
    url(r'^level3/preload_list', RefreshListView.as_view(), {'force': True}, name='preload_list'),
    # 用户与域名关联接口
    url(r'^level3/user_domains', UserDomainView.as_view(), name='user_domains'),
    # 用户与cdn绑定接口
    url(r'^level3/user_cdns', UserCDNView.as_view(), name='user_cdns'),

    # url(r'^level3/cdn', cdn, name='cdn'),
    # 新增用户接口
    url(r'^level3/user$', UserView.as_view(), name='user'),
    # 日志下载
    url(r'^level3/log/(?P<filename>.{8,60})$', LogDownloadView.as_view(), name='log'),
    # 获取下载日志列表
    url(r'^level3/logdownload/$', LogListView.as_view(), name='log_list'),
    # test
    url(r'^level3/test/$', abtest, name='test')
]

# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

from django.contrib import admin
from django import forms

from overseas.models.access import AccessGroup, Service, NetworkIdentifiers, NiInfo, CDN, InfUser


class AccessGroupAdmin(admin.ModelAdmin):
    list_display = ['agid', 'desc', 'active']


class CDNAdmin(admin.ModelAdmin):
    list_display = ['cdn_name', 'ni', 'active']


class CDNInline(admin.TabularInline):
    model = CDN
    extra = 0


class InfUserAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'operate_right', 'active', 'joined', 'last']
    # inlines = [
    #     CDNInline
    # ]
    # form = Tan14UserAdminForm
    fields = ['login_email', 'password', 'joined', 'last',
              'cdn', 'operate_right', 'active']
    readonly_fields = ['joined', 'last']
    list_filter = ['active', 'record_date', 'operate_right']
    filter_horizontal = ['cdn']

    class Meta:
        model = InfUser


class NetworkIdentifiersAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'active']
    list_filter = ['active', 'service']
    readonly_fields = ['ni', 'service', 'active']

    class Meta:
        model = NetworkIdentifiers


# admin.site.register(AccessGroup, AccessGroupAdmin)
# admin.site.register(CDN, CDNAdmin)
admin.site.register(InfUser, InfUserAdmin)
admin.site.register(NetworkIdentifiers, NetworkIdentifiersAdmin)
# models = Service, NiInfo
# [admin.site.register(i) for i in models]
# admin.site.register(Service)
# admin.site.register(NetworkIdentifiers)
# admin.site.register(NiInfo)
# admin.site.register(CDN)

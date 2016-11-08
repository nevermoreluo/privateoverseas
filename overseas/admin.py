# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

from django.contrib import admin
from overseas.models.access import AccessGroup, Service, NetworkIdentifiers, NiInfo, CDN, Tan14User


class AccessGroupAdmin(admin.ModelAdmin):
    list_display = ['agid', 'desc', 'active']


class CDNAdmin(admin.ModelAdmin):
    list_display = ['cdn_name', 'tan14_user', 'ni', 'active']


class CDNInline(admin.TabularInline):
    model = CDN
    extra = 0


class Tan14UserAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    inlines = [
        CDNInline
    ]

    class Meta:
        model = Tan14User


admin.site.register(AccessGroup, AccessGroupAdmin)
# admin.site.register(CDN, CDNAdmin)
admin.site.register(Tan14User, Tan14UserAdmin)
models = Service, NetworkIdentifiers, NiInfo
[admin.site.register(i) for i in models]
# admin.site.register(Service)
# admin.site.register(NetworkIdentifiers)
# admin.site.register(NiInfo)
# admin.site.register(CDN)

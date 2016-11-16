# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# auth: nevermore

from django.contrib import admin
from django import forms

from overseas.models.access import AccessGroup, Service, NetworkIdentifiers, NiInfo, CDN, Tan14User


class AccessGroupAdmin(admin.ModelAdmin):
    list_display = ['agid', 'desc', 'active']


class CDNAdmin(admin.ModelAdmin):
    list_display = ['cdn_name', 'tan14_user', 'ni', 'active']


class CDNInline(admin.TabularInline):
    model = CDN
    extra = 0


# from django.contrib.admin.widgets import FilteredSelectMultiple


# class Tan14UserAdminForm(forms.ModelForm):
#     class Meta:
#         model = Tan14User
#         fields = '__all__'

#     domian = forms.ModelMultipleChoiceField(
#         queryset=CDN.objects.all(),
#         required=False,
#         widget=FilteredSelectMultiple(
#             verbose_name='domains',
#             is_stacked=False
#         )
#     )

#     def __init__(self, *args, **kwargs):
#         super(Tan14UserAdminForm, self).__init__(*args, **kwargs)
#         if self.instance.pk:
#             self.fields['domian'].initial = self.instance.cdn_set.all()

#     def save(self, commit=True):
#         tan14user = super(Tan14UserAdminForm, self).save(commit=False)
#         if commit:
#             tan14user.save()

#         if tan14user.pk:
#             tan14user.cdn_set = self.cleaned_data['domian']
#             self.save_m2m()

#         return tan14user


class Tan14UserAdmin(admin.ModelAdmin):
    list_display = ['__str__']
    # inlines = [
    #     CDNInline
    # ]
    # form = Tan14UserAdminForm
    filter_horizontal = ['cdn']

    class Meta:
        model = Tan14User


class NetworkIdentifiersAdmin(admin.ModelAdmin):
    list_display = ['ni', 'active']
    list_filter = ['active']

    class Meta:
        model = NetworkIdentifiers


admin.site.register(AccessGroup, AccessGroupAdmin)
# admin.site.register(CDN, CDNAdmin)
admin.site.register(Tan14User, Tan14UserAdmin)
admin.site.register(NetworkIdentifiers, NetworkIdentifiersAdmin)
models = Service, NiInfo
[admin.site.register(i) for i in models]
# admin.site.register(Service)
# admin.site.register(NetworkIdentifiers)
# admin.site.register(NiInfo)
# admin.site.register(CDN)

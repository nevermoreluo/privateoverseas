# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-18 08:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('overseas', '0018_auto_20160918_1537'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='name',
        ),
        migrations.AlterField(
            model_name='cdn',
            name='cdn_name',
            field=models.CharField(max_length=100),
        ),
    ]

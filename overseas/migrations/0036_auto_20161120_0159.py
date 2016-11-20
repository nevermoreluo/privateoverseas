# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-19 17:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('overseas', '0035_auto_20161116_1132'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tan14User',
            new_name='InfUser',
        ),
        migrations.AlterField(
            model_name='cdn',
            name='cdn_name',
            field=models.CharField(choices=[('level3', 'level3')], max_length=100, verbose_name='CDN'),
        ),
    ]
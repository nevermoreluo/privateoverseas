# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-16 03:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('overseas', '0034_auto_20161116_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tan14user',
            name='cdn',
            field=models.ManyToManyField(blank=True, to='overseas.CDN'),
        ),
    ]

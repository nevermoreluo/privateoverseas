# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-09 01:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('overseas', '0007_auto_20160906_0546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='niinfo',
            name='bandwidth',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='niinfo',
            name='throughput',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

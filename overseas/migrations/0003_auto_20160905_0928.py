# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-05 09:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('overseas', '0002_auto_20160905_0827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='niinfo',
            name='bandwidth',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='niinfo',
            name='peak_bandwidth',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='niinfo',
            name='peak_throughput',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='niinfo',
            name='requests',
            field=models.PositiveIntegerField(default=0, unique=True),
        ),
        migrations.AlterField(
            model_name='niinfo',
            name='throughput',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=20),
        ),
    ]

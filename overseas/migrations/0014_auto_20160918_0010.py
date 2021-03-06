# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-17 16:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('overseas', '0013_auto_20160914_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='CDN',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cdn_name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='networkidentifiers',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='overseas.Service'),
        ),
        migrations.AddField(
            model_name='networkidentifiers',
            name='cdn',
            field=models.ManyToManyField(blank=True, null=True, to='overseas.CDN'),
        ),
    ]

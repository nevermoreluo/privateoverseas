# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-05 08:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('overseas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NiInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requests', models.PositiveIntegerField(unique=True)),
                ('throughput', models.DecimalField(decimal_places=4, max_digits=20)),
                ('peak_throughput', models.DecimalField(decimal_places=4, max_digits=20)),
                ('bandwidth', models.DecimalField(decimal_places=4, max_digits=20)),
                ('peak_bandwidth', models.DecimalField(decimal_places=4, max_digits=20)),
                ('time', models.DateTimeField()),
                ('ni', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='overseas.NetworkIdentifiers')),
            ],
        ),
        migrations.RemoveField(
            model_name='geo',
            name='ni',
        ),
        migrations.DeleteModel(
            name='Geo',
        ),
    ]

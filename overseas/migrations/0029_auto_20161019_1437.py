# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-19 06:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('overseas', '0028_auto_20161018_1110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tan14user',
            old_name='active',
            new_name='operate_right',
        ),
    ]

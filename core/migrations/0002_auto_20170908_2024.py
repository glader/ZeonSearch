# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-08 15:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='record',
            old_name='operations',
            new_name='transcription',
        ),
    ]
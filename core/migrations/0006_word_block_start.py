# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-08 18:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_wordnormal_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='block_start',
            field=models.BooleanField(default=False, verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e \u0431\u043b\u043e\u043a\u0430'),
        ),
    ]
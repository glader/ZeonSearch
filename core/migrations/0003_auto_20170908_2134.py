# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-08 16:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20170908_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wordnormal',
            name='normal',
            field=models.CharField(db_index=True, max_length=100, verbose_name='\u041d\u043e\u0440\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u0444\u043e\u0440\u043c\u0430'),
        ),
    ]

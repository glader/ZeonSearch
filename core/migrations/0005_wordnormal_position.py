# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-08 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_wordnormal_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='wordnormal',
            name='position',
            field=models.PositiveIntegerField(default=1, verbose_name='\u041f\u043e\u0437\u0438\u0446\u0438\u044f'),
            preserve_default=False,
        ),
    ]
# coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from core import models


@admin.register(models.Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('filename',)


@admin.register(models.Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'block_start')
    raw_id_fields = ('record',)
    list_filter = ('record',)


@admin.register(models.WordNormal)
class WordNormalAdmin(admin.ModelAdmin):
    list_display = ('word', 'normal')
    raw_id_fields = ('word',)

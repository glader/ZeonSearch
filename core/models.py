# coding: utf-8
from __future__ import unicode_literals

from django.db import models


class Record(models.Model):
    url = models.URLField(verbose_name='Адрес')
    author = models.CharField(verbose_name='Кто проводил', max_length=100)
    filename = models.CharField(verbose_name='Файл', max_length=100)
    transcription = models.TextField(verbose_name='Транслитерация')
    dt = models.DateField(verbose_name='Дата проведения')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __unicode__(self):
        return self.filename


class Word(models.Model):
    record = models.ForeignKey(Record, verbose_name='Запись', on_delete=models.CASCADE)
    word = models.CharField(verbose_name='Слово', max_length=100)
    position = models.PositiveIntegerField(verbose_name='Позиция')
    offset = models.PositiveIntegerField(verbose_name='Смещение', help_text='от начала файла, в секундах')
    block_start = models.BooleanField(verbose_name='Начало блока', default=False)

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'

    def __unicode__(self):
        return self.word


class WordNormal(models.Model):
    record = models.ForeignKey(Record, verbose_name='Запись', on_delete=models.CASCADE)
    word = models.ForeignKey(Word, verbose_name='Слово', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(verbose_name='Позиция')
    normal = models.CharField(verbose_name='Нормальная форма', max_length=100, db_index=True)

    class Meta:
        verbose_name = 'Нормальная форма'
        verbose_name_plural = 'Нормальные формы'

# coding: utf-8

import json
import os
from datetime import date

import pymorphy2
from django.core.management.base import BaseCommand

from core import models

FILES_DIR = 'D:\\!!\\zeon'


class Command(BaseCommand):
    help = 'Import file data'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]

        flac_files = os.listdir(os.path.join(FILES_DIR, 'flac'))
        for f in flac_files:
            if '2017' not in f:
                continue

            f = '-'.join(f.split('-')[:3])

            if not models.Record.objects.filter(filename__contains=f).exists():
                self.process(f)


    def process(self, filename):
        print filename

        flac_files = os.listdir(os.path.join(FILES_DIR, 'flac'))
        amount = len([True for f in flac_files if f.startswith(filename)])
        print 'Found %s audio files' % amount

        text_files = os.listdir(os.path.join(FILES_DIR, 'results'))
        text_amount = len([True for f in text_files if f.startswith(filename)])
        if text_amount != amount:
            print 'Not found enough text files'
            return

        date_str = filename.split('-')[1]
        dt = date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))
        print dt

        urls = open(os.path.join(FILES_DIR, 'log')).readlines()
        url = None
        for line in urls:
            if filename in line:
                url = line.split('\t')[0]
        if not url:
            print 'Url not found'
            return

        record, _ = models.Record.objects.get_or_create(
            filename=filename,
            defaults={
                'url': url,
                'author': 'Клюхин' if 'kluhin' in filename else 'Богданов',
                'dt': dt,
            }
        )

        transcription = {}
        for i in xrange(amount):
            transcription[i] = []

            result = json.load(open(os.path.join(FILES_DIR, 'results', '%s-%02d.flac.txt' % (filename, i))))
            for block in result['response']['results']:
                transcription[i].append(block['alternatives'][0])

        record.transcription = json.dumps(transcription)
        record.save()

        record.word_set.all().delete()

        position = 0
        morph = pymorphy2.MorphAnalyzer()

        for i in xrange(amount):
            file_offset = i * 10 * 60

            for block in transcription[i]:
                start = True

                for word in block['words']:
                    offset = int(float(word['startTime'].replace('s', '')))
                    record_word = models.Word.objects.create(
                        record=record,
                        position=position,
                        offset=file_offset + offset,
                        word=word['word'],
                        block_start=start
                    )

                    for normal in set(v.normal_form for v in morph.parse(word['word'])):
                        models.WordNormal.objects.create(
                            record=record,
                            word=record_word,
                            normal=normal,
                            position=position,
                        )

                    position += 1
                    start = False













        # получить количество flac файлов
        # получить список готовых текстов. убедиться, что их столько же
        # создать или открыть файл с записью
        # удалить все слова из записи
        # перебрать операции. объединить в один json, сохранить его в запись
        # перебрать этот json. каждое слово сохранить отдельно, правильно высчитав смещение. длина записей 10 минут, 600 сек
        # для слова получить нормальные формы. сохранить в отдельную модель




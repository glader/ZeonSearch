# coding: utf-8
from __future__ import unicode_literals

import logging
from datetime import timedelta
from django.views.generic import TemplateView
from django.db import connection

from core import models
import pymorphy2

BORDERS = 40

log = logging.getLogger(__name__)


class SearchView(TemplateView):
    template_name = 'core/index.html'

    def post(self, request, *args, **kwargs):
        query = request.POST['query'].strip()
        log.info('Search for <%s>', query)

        if not query:
            return self.get(request)

        morph = pymorphy2.MorphAnalyzer()
        words = [morph.parse(word.strip())[0].normal_form for word in query.split(' ')]
        amount = len(words)

        log.info('Morphed to <%s>', ', '.join(words))

        if amount > 5:
            return self.render_to_response({'query': query, 'error': 'Слишком длинный запрос'})

        if amount == 1:
            q = 'SELECT n1.word_id FROM core_wordnormal n1 WHERE n1.normal=%s'

        else:
            select = 'SELECT ' + ', '.join('n%s.word_id' % i for i in xrange(amount))
            where = ' WHERE ' + ' AND '.join('n%s.normal=%%s' % i for i in xrange(amount))
            join = ' FROM core_wordnormal n0 '
            for i in xrange(1, amount):
                join += ' JOIN core_wordnormal n{curr} ' \
                        'ON n{prev}.record_id=n{curr}.record_id ' \
                        'AND n{prev}.position < n{curr}.position ' \
                        'AND n{curr}.position - n{prev}.position < 5 '.format(curr=i, prev=i-1)

            q = select + join + where

        q += ' LIMIT 20'

        cursor = connection.cursor()
        cursor.execute(q, words)

        results = []
        for row in cursor.fetchall():
            res_words = [models.Word.objects.get(pk=word_id) for word_id in row]
            start_position = max(res_words[0].position - BORDERS, 0)
            finish_position = res_words[-1].position + BORDERS

            words = models.Word.objects.filter(
                position__gte=start_position,
                position__lte=finish_position,
                record=res_words[0].record_id,
            )

            phrase = ''
            for word in words:
                if word.pk in row:
                    phrase += ' <span style="color:red">%s</span> ' % word.word
                else:
                    phrase += ' ' + word.word

                if word.block_start:
                    phrase = '. ' + phrase

            results.append({
                'record': res_words[0].record,
                'phrase': phrase,
                'start': timedelta(seconds=words[0].offset)
            })

        return self.render_to_response({'query': query, 'results': results})

# coding: utf-8
from __future__ import unicode_literals

import logging
from datetime import timedelta
from django.views.generic import TemplateView
from django.db import connection

from core import models
import pymorphy2

BORDERS = 50
RESULTS_PER_PAGE = 20

log = logging.getLogger(__name__)


class SearchView(TemplateView):
    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '').strip()

        if not query:
            return self.render_to_response({})

        log.info('Search for <%s>', query)

        morph = pymorphy2.MorphAnalyzer()
        words = [morph.parse(word.strip())[0].normal_form for word in query.split(' ')]
        amount = len(words)

        log.info('Morphed to <%s>', ', '.join(words))

        if amount > 5:
            return self.render_to_response({'query': query, 'error': 'Слишком длинный запрос'})

        if amount == 1:
            q = '''SELECT n0.word_id 
                   FROM core_wordnormal n0 
                   JOIN core_word w ON n0.word_id=w.id
                   JOIN core_record r ON w.record_id=r.id 
                   WHERE n0.normal=%s'''

        else:
            select = 'SELECT ' + ', '.join('n%s.word_id' % i for i in xrange(amount))
            where = ' WHERE ' + ' AND '.join('n%s.normal=%%s' % i for i in xrange(amount))
            join = ''' FROM core_wordnormal n0 JOIN core_word w ON n0.word_id=w.id
                   JOIN core_record r ON w.record_id=r.id  '''
            for i in xrange(1, amount):
                join += ' JOIN core_wordnormal n{curr} ' \
                        'ON n{prev}.record_id=n{curr}.record_id ' \
                        'AND n{prev}.position < n{curr}.position ' \
                        'AND n{curr}.position - n{prev}.position < 5 '.format(curr=i, prev=i-1)

            q = select + join + where

        q += ' ORDER BY r.dt DESC, w.position ASC'
        q += ' LIMIT %s' % (RESULTS_PER_PAGE + 1)

        page = 1
        if request.GET.get('page'):
            page = int(request.GET.get('page'))

        q += ' OFFSET %s' % (RESULTS_PER_PAGE * (page - 1))

        cursor = connection.cursor()
        cursor.execute(q, words)

        results = []
        data = cursor.fetchall()
        for row in data[:RESULTS_PER_PAGE]:
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
                'start': timedelta(seconds=words[0].offset),
            })

        return self.render_to_response({
            'query': query,
            'results': results,
            'page': page,
            'first': 1 if page > 1 else None,
            'prev': page - 1 if page > 1 else None,
            'next': page + 1 if len(data) > RESULTS_PER_PAGE else None,
        })

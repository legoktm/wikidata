#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import unicode_literals
import pywikibot
from wmflabs import db as mysql

site = pywikibot.Site('wikidata', 'wikidata')
site.login()
db = mysql.connect('wikidatawiki')


def linkify(page):
    title = page.title().split('/', 1)[1]
    return '[[{0}|{1}]]'.format(page.title(), title)


def contributors(page, db):
    with db.cursor() as cur:
        cur.execute("select count(distinct(rev_user_text)) "
                    "from revision "
                    "join page "
                    "on rev_page=page_id "
                    "where page_namespace=4 "
                    "and page_title=?", (page.title(withNamespace=False).replace(' ', '_').encode('utf-8'),))
        res = cur.fetchone()
    return res[0]


def make_report(cat, pgname):
    cat = pywikibot.Category(site, cat)
    text = """{| class="wikitable; sortable"
    |-
    ! Name !! Contributors"""

    for page in cat.articles(namespaces=[4]):
        if page.title() == 'Wikidata:Requests for comment':
            continue
        pywikibot.output(page)
        contrib = contributors(page, db)
        text += '\n|-\n| {0} || {1}'.format(linkify(page), contrib)

    text += '\n|}'

    pg = pywikibot.Page(site, pgname)
    pg.put(text, 'Bot: Updating RfC report.')

make_report('Category:Requests for comment', 'User:Legoktm/RfC report')
make_report('Category:Closed requests for comment', 'User:Legoktm/Closed RfC report')

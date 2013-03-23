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
import sys
import os
sys.path.append(os.path.expanduser('~/dumpreports'))
import pywikibot
import dumpreports

site = pywikibot.Site()
repo = site.data_repository()
wikidata = pywikibot.Site('wikidata', 'wikidata')

text = u"""<table class="wikitable sortable">
<tr><th>Burial location<th>Type<th>Location<th>Country<th>Person\n"""


def do_page(page):
    if not 'p119' in page.claims:
        return ''
    print 'Gonna fetch...'
    target = page.claims['p119'][0].getTarget()
    target.get()
    data = [target.getID()]
    data.append(target.labels.get('en', ''))
    if 'p31' in target.claims:
        tgt = target.claims['p31'][0].getTarget()
        tgt.get()
        data.append(tgt.getID())
        data.append(tgt.labels.get('en', ''))
    else:
        data.append('n/a')
        data.append('')
    if 'p131' in target.claims:
        tgt = target.claims['p131'][0].getTarget()
        tgt.get()
        data.append(tgt.getID())
        data.append(tgt.labels.get('en', ''))
    else:
        data.append('n/a')
        data.append('')
    if 'p17' in target.claims:
        tgt = target.claims['p17'][0].getTarget()
        tgt.get()
        data.append(tgt.getID())
        data.append(tgt.labels.get('en', ''))
    else:
        data.append('n/a')
        data.append('')
    data.append(page.getID())
    data.append(page.labels.get('en', ''))
    val = u"<tr><td>[[{}|{}]]<td>[[{}|{}]]<td>[[{}|{}]]<td>[[{}|{}]]<td>[[{}|{}]]\n".format(*data)
    val = val.replace('[[n/a|]]', 'n/a')
    print val.encode('utf-8')
    return val

gen = dumpreports.DumpGenerator(repo)
for page in gen:
    text += do_page(page)
text+=u'\n</table>'
pg = pywikibot.Page(wikidata, 'Wikidata:Dump reports/Burial locations')
pg.put(text, 'Bot: Updating report')

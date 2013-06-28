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
import pywikibot
from pywikibot.data import api
site = pywikibot.Site('ru', 'wikipedia')
repo = site.data_repository()

def gen():
    g = api.LogEntryListGenerator(site=site, logtype='delete', leaction='delete/delete')
    for x in g:
        yield x

for item in gen():
    #print item.title()
    pg = pywikibot.Page(item.title())
    #print pg
    item = pywikibot.ItemPage.fromPage(pg)
    try:
        item.get()
    except pywikibot.NoPage:
        continue
    if pg.exists():
        continue
    print "{} == {}".format(item.title(), item.getID())
    if len(item.sitelinks) == 1:
        print 'gonna delete'
        item = pywikibot.ItemPage(repo, item.getID())
        item.delete('Does not meet the [[Special:MyLanguage/Wikidata:Notability|notability policy]]: only linked article deleted', prompt=False)

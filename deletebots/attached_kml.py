#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from pywikibot import config
config.put_throttle = 0
en = pywikibot.Site('en')
reason = 'Category redirect'
repo = en.data_repository()


def gen():
    template = pywikibot.ItemPage(repo, 'Q6175758')
    template.get()
    for wiki in template.sitelinks:
        print 'STARTING ' + wiki
        if wiki.startswith(('en', 'es', 'fr', 'fa')):
            continue
        s = pywikibot.Site(wiki.replace('wiki', '').replace('_', '-'), 'wikipedia')
        pg = pywikibot.Category(s, template.sitelinks[wiki])
        #g = pg.getReferences(onlyTemplateInclusion=True, namespaces=14)
        g = pg.articles(namespaces=[14])
        for x in g:
            yield x

for page in gen():
    i = pywikibot.ItemPage.fromPage(page)
    if i.exists() and len(i.sitelinks) == 1:
        i = pywikibot.ItemPage(repo, i.getID())
        print i
        i.delete(reason, prompt=False)
    else:
        print 'no item/2+ sitelinks'
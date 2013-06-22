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
import re
import pywikibot as p
enwp = p.Site()
repo = enwp.data_repository()
skip = ['Mighty Ducks of Anaheim players','Anaheim Ducks players','Brooklyn Americans players','Cleveland Barons (NHL) players']
cat = p.Category(enwp, 'Category:National Hockey League players')
subcats = cat.subcategories()
for subcat in subcats:
    if not subcat.title().endswith('players'):
        continue
    if subcat.title().endswith(tuple(skip)):
        continue
    text = subcat.get()
    x = list(re.finditer('\[\[National Hockey League\]\]( \(NHL\))? for the \[\[(?P<name>.*?)\]\].', text))
    if not x:
        y = list(re.finditer('for the \[\[(?P<name>.*?)\]\] of the \[\[National Hockey League\]\].', text))
        if not y:
            continue
        else:
            title = y[0].group('name')
    else:
        title = x[0].group('name')
    team = p.Page(enwp, title)
    if team.isRedirectPage():
        continue
    item = p.ItemPage.fromPage(team)
    #print team.title()
    item.get()
    id = item.id.upper()
    #print id
    #print item.labels['en']
    print '{{{{User:Legobot/properties.js/row|en|{0}|P54|{1}|Legoktm|ignoreprefix=List|create=yes|pid2=P107|qid2=Q215627|pid3=P21|qid3=Q6581097}}}}'.format(subcat.title().encode('utf-8'), id)
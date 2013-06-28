#!/usr/bin/env python
from __future__ import unicode_literals
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
en = pywikibot.Site('en')


def gen(cat):
    return pywikibot.Category(en, 'Category:'+cat).articles(namespaces=[0])

text = ''
dontexist = list()
for year in ['Video game engines', 'Free game engines', 'Computer physics engines']:
    print year
    g = gen(year)
    text += '== [[:en:Category:{}]] ==\n'.format(year)
    for pg in g:
        d = pywikibot.ItemPage.fromPage(pg)
        if d.exists():
            label = ''
            if 'en' in d.labels:
                label = d.labels['en']
            text += '* [[{}|{}]]\n'.format(d.getID().upper(), label)
        else:
            dontexist.append(pg)
with open('hahc2.txt', 'w') as f:
    f.write(text.encode('utf-8'))
print 'written'

for item in dontexist:
    print '[[:en:{}]]'.format(item.title())

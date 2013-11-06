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

fname = 'stuff.csv'
f = open(fname, 'w')
import pywikibot
site = pywikibot.Site('wikidata', 'wikidata')
cat = pywikibot.Category(site, 'Category:Babel - Users by language')
data = {}
for subcat in cat.subcategories():
    name = subcat.title(withNamespace=False).replace('User ', '')
    data[name] = 0
    for article in subcat.articles():
        data[name] += 1
    if data[name] != 0:
        t = '{0}, {1}'.format(name, data[name])
        print t
        f.write(t + '\n')
f.close()

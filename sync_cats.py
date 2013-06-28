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
numeral_map = zip(
    (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
    ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
)
pt = pywikibot.Site('pt', 'wikipedia')
en = pywikibot.Site('en', 'wikipedia')

def int_to_roman(i):
    result = []
    for integer, numeral in numeral_map:
        count = int(i / integer)
        result.append(numeral * count)
        i -= integer * count
    return ''.join(result)

def roman_to_int(n):
    n = unicode(n).upper()

    i = result = 0
    for integer, numeral in numeral_map:
        while n[i:i + len(numeral)] == numeral:
            result += integer
            i += len(numeral)
    return result


def log(item, the_item):
    with open('film.log', 'a') as f:
        f.write('\n*[[{}]] -> [[{}]]'.format(item.getID(), the_item.getID()))


for i in range(1, 21):
    roman = int_to_roman(i)
    item = pywikibot.ItemPage.fromPage(pywikibot.Page(en, 'Category:{}th-century philosophers'.format(i)))
    p = pywikibot.Page(pt, u'Categoria:Filósofos do século {}'.format(roman))
    x = pywikibot.ItemPage.fromPage(p)
    if item.exists() and x.exists():
        if item.getID() == x.getID():
            print 'the same'
            continue
        x.removeSitelink(p.site, bot=True)
        item.setSitelink(p, bot=True)
        log(x, item)


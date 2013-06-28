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
import pywikibot as p
d = p.Site('wikidata','wikidata').data_repository()
from pywikibot import config
config.put_throttle = 0
import time
import re
rgex = re.compile('\[\[(.*?)\]\]')

regex = re.compile('\[\[Q(\d*?)\]\]')

with open('wikidata_connect_ok2.txt', 'r') as f:
    for line in f:
        sp = line.strip().split('|')
        i = p.ItemPage(d, sp[0].strip())
        print i
        if not i.exists():
            print 'Already deleted.'
            continue
        if i.sitelinks:
            print 'Still has sitelinks!!!'
            continue
        i.delete('Merged into [[' + sp[1].strip() + ']]', prompt=False)
        time.sleep(.5)



def other():
    lines = reversed(text.splitlines())

    for line in lines:
        if not regex.search(line):
            continue
        item = 'Q' + str(regex.search(line).group(1))
        i = p.Page(d, item)
        print i
        if i.exists():
            i.delete('Empty item', prompt=False)
quit()
for line in text.splitlines():
    sp = line.split('->')
    tbd = p.ItemPage(d, rgex.search(sp[0]).group(1))
    if not tbd.exists():
        continue
    if tbd.sitelinks:
        print '{} still has sitelinks'.format(tbd.getID())
        continue
    print tbd
    if len(sp) > 1:
        tbd.delete('Merged into '+sp[1].strip(), prompt=False)
    else:
        tbd.delete('Empty item', prompt=False)

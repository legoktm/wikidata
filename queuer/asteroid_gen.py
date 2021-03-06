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
import oursql
import os

repo = pywikibot.Site().data_repository()
prop = pywikibot.PropertyPage(repo, 'Property:P61')

def insert(cur, item, target, prop, lang):
    x = (None, item.getID(), target.getID(), prop.getID(), lang)
    print x
    cur.execute('INSERT INTO `baseball` VALUES (?, ?, ?, ?, ?)', x)


db = oursql.connect(raise_on_warnings=False,
                    read_default_file=os.path.expanduser("~/.my.cnf"),
                    )
cursor = db.cursor()


page = pywikibot.Page(repo, 'User:Ysogo/asteroidi-scopritori')
lines = page.get().splitlines()
for line in lines:
    print line
    line = line.strip('*').strip()
    sp = line.split('-')
    item = sp[0].strip()
    item = pywikibot.ItemPage(repo, item)
    values = sp[1].split(',')
    for value in values:
        value = value.strip()
        if value:
            target = pywikibot.ItemPage(repo, value)
            insert(cursor, item, target, prop, 'MPC')

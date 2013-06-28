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
import os
os.environ['PYWIKIBOT2_DIR'] = '/data/project/legobot/.pywikibot/'
import oursql
import pywikibot
from pywikibot import config

config.put_throttle = 0
lang = 'pt'
wp = pywikibot.Site(lang, 'wikipedia')
if not wp.logged_in():
    wp.login()
repo = pywikibot.Site().data_repository()
if not repo.logged_in():
    repo.login()


def insert(cur, item, target, prop, lang):
    x = (None, item.getID(), target.getID(), prop.getID(), lang)
    print x
    cur.execute('INSERT INTO `baseball` VALUES (?, ?, ?, ?, ?)', x)

prop = pywikibot.PropertyPage(repo, 'Property:P60')
target = pywikibot.ItemPage(repo, 'Q3863')


def main():
    cat = pywikibot.Category(wp, 'Category:Asteroides da cintura principal')
    gen = cat.articles(namespaces=0)
    db = oursql.connect(raise_on_warnings=False,
                        read_default_file=os.path.expanduser("~/.my.cnf"),
                        )
    cur = db.cursor()
    for page in gen:
        item = pywikibot.ItemPage.fromPage(page)
        if item.exists():
            ok = True
            if prop.getID() in item.claims:
                for c in item.claims[prop.getID()]:
                    if c.getTarget().getID() == target.getID():
                        ok = False
                        break
            if ok:
                insert(cur, item, target, prop, lang)

if __name__ == '__main__':
    main()
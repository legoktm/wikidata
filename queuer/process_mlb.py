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
import mwparserfromhell as mwparser
import os
#os.environ['PYWIKIBOT2_DIR'] = '/data/project/legobot/.pywikibot'
import pywikibot
from pywikibot import config
import oursql
config.put_throttle = 0
repo = pywikibot.Site().data_repository()
if not repo.logged_in():
    repo.login()
ENWP_ITEM = pywikibot.ItemPage(repo, 'Q328')
IMPORTED_FROM = pywikibot.Claim(repo ,'p143')
IMPORTED_FROM.setTarget(ENWP_ITEM)
CLAIM = pywikibot.Claim(repo, 'p301')


def go(item, target):
    CLAIM.setTarget(target)
    try:
        item.addClaim(CLAIM, bot=True)
    except pywikibot.NoPage:
        return
    print '{0} --> {1}'.format(item.getID(), target.getID())
    CLAIM.addSource(IMPORTED_FROM, bot=True)

db = oursql.connect(raise_on_warnings=False,
                    read_default_file=os.path.expanduser("~/.my.cnf"),
                    )


def gen(db):
    go = True
    while go:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM baseball LIMIT 20')
        count = 0
        for val in cursor:
            count += 1
            yield val
        if count == 0:
            go = False


def mark_done(db, number):
    cursor = db.cursor()
    cursor.execute('DELETE FROM baseball WHERE id=?', (number,))


def main():
    g = gen(db)
    for num, item, target in g:
        item = pywikibot.ItemPage(repo, item)
        target = pywikibot.ItemPage(repo, target)
        go(item, target)
        mark_done(db, num)

if __name__ == "__main__":
    main()

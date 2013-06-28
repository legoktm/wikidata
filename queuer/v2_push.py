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
os.environ['PYWIKIBOT2_DIR'] = '/data/project/legobot/.pywikibot'
import pywikibot
from pywikibot import config
import oursql
config.put_throttle = 0
repo = pywikibot.Site().data_repository()
if not repo.logged_in():
    repo.login()
IMPORTED_FROM = pywikibot.Claim(repo, 'p143')


SOURCE_VALUES = {'en': pywikibot.ItemPage(repo, 'Q328'),
                 'sv': pywikibot.ItemPage(repo, 'Q169514'),
                 'de': pywikibot.ItemPage(repo, 'Q48183'),
                 'it': pywikibot.ItemPage(repo, 'Q11920'),
                 'no': pywikibot.ItemPage(repo, 'Q191769'),
                 'ar': pywikibot.ItemPage(repo, 'Q199700'),
                 'es': pywikibot.ItemPage(repo, 'Q8449'),
                 'pl': pywikibot.ItemPage(repo, 'Q1551807'),
                 'ca': pywikibot.ItemPage(repo, 'Q199693'),
                 'fr': pywikibot.ItemPage(repo, 'Q8447'),
                 'nl': pywikibot.ItemPage(repo, 'Q10000'),
                 'pt': pywikibot.ItemPage(repo, 'Q11921'),
                 'ru': pywikibot.ItemPage(repo, 'Q206855'),
                 'vi': pywikibot.ItemPage(repo, 'Q200180'),
                 'be': pywikibot.ItemPage(repo, 'Q877583'),
                 'uk': pywikibot.ItemPage(repo, 'Q199698'),
                 'tr': pywikibot.ItemPage(repo, 'Q58255'),
                 'MPC': pywikibot.ItemPage(repo, 'Q522039'),
                 }  # TODO: read from somewhere onwiki or dynamic updates


claims = {}


def go(item, target, claim, source):
    claim.setTarget(target)
    try:
        item.addClaim(claim, bot=True)
    except pywikibot.NoPage:
        return
    print '{0} --> {1}'.format(item.getID(), target.getID())
    IMPORTED_FROM.setTarget(SOURCE_VALUES[source])
    claim.addSource(IMPORTED_FROM, bot=True)

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
    for num, item, target, prop, source, overwrite in g:
        item = pywikibot.ItemPage(repo, item)
        target = pywikibot.ItemPage(repo, target)
        if not prop in claims:
            claims[prop] = pywikibot.Claim(repo, prop)
        claim = claims[prop]
        item.get()
        g = True
        remove = list()
        if claim.getID() in item.claims:
            for c in item.claims[claim.getID()]:
                if c.getTarget():
                    if c.getTarget().getID() == target.getID():
                        g = False
                    else:
                        remove.append(c)
        if remove:
            item.removeClaims(remove, bot=True)
        if g:
            go(item, target, claim, source)
        mark_done(db, num)

if __name__ == "__main__":
    main()
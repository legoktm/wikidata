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
wp = pywikibot.Site('en', 'wikipedia')
if not wp.logged_in():
    wp.login()
repo = pywikibot.Site().data_repository()
if not repo.logged_in():
    repo.login()


def insert(cur, item, target, prop, lang):
    x = (None, item.getID(), target.getID(), prop.getID(), lang, 0)
    print x
    cur.execute('INSERT INTO `baseball` VALUES (?, ?, ?, ?, ?, ?)', x)


db = oursql.connect(raise_on_warnings=False,
                    read_default_file=os.path.expanduser("~/.my.cnf"),
                    )

instance_of = pywikibot.Claim(repo, 'p31')
part_of = pywikibot.Claim(repo, 'p361')
preceded_by = pywikibot.Claim(repo, 'p155')
followed_by = pywikibot.Claim(repo, 'p156')


def gen():
    for x in range(1, 2060):
        yield x


def get_decade(year):
    year = str(year)
    x = unicode(year[:len(year) - 1] + '0s')
    if year.endswith('00'):
        x += ' (decade)'
    return x


def do_month(cur, year):
    pg = pywikibot.Page(wp, unicode(year))
    print pg
    item = pywikibot.ItemPage.fromPage(pg)
    if item.exists():
        print item.getID()
        #instance of January
        yr_item = pywikibot.ItemPage(repo, 'Q577')
        insert(cur, item, yr_item, instance_of, 'en')
        #part of 1900
        decade = pywikibot.ItemPage.fromPage(pywikibot.Page(wp, get_decade(year)))
        insert(cur, item, decade, part_of, 'en')
        #preceded_by
        prev = pywikibot.ItemPage.fromPage(pywikibot.Page(wp, unicode(year-1)))
        if prev.exists():
            insert(cur, item, prev, preceded_by, 'en')
        #followed_by
        follow = pywikibot.ItemPage.fromPage(pywikibot.Page(wp, unicode(year+1)))
        if follow.exists():
            insert(cur, item, follow, followed_by, 'en')



def main():
    db = oursql.connect(raise_on_warnings=False,
                        read_default_file=os.path.expanduser("~/.my.cnf"),
                        )
    cursor = db.cursor()
    for year in gen():
        do_month(cursor, year)

if __name__ == "__main__":
    main()
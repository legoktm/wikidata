#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import pywikibot
import oursql
import os
import sys

query = """
/* SLOW_OK */
SELECT
 rc_title,
 rc_comment,
 rc_timestamp
FROM recentchanges
WHERE rc_namespace=0
AND rc_comment rlike "Robot: (Removing|Adding|Modifying)"
LIMIT 20;
"""

lang_links = """
/* SLOW_OK */
SELECT
 lang.ll_lang,
 lang.ll_title
FROM langlinks as lang
JOIN page as page
ON lang.ll_from = page.page_id
WHERE page.page_namespace = 0
AND page.page_title=?;
"""

db = oursql.connect(db='enwiki_p',
    host="enwiki-p.rrdb.toolserver.org",
    read_default_file=os.path.expanduser("~/.my.cnf"),
    charset=None,
    use_unicode=False
)

site = pywikibot.getSite()
repo = site.data_repository()

def fetch_links(title):
    cursor = db.cursor()
    cursor.execute(lang_links, (title,))
    data = {}
    for lang, t in cursor:
        s = lang + 'wiki'
        data[s] = {'site':s, 'title':t}
    return data

def fetch_wd(title):
    qid = repo.get_id('enwiki',title)
    return repo.get_sitelinks(qid)

def go(title, summary):
    qid = repo.get_id('enwiki',title)
    if qid == '-1':
        return
    print 'Processing {}'.format(qid)
    sitelinks = repo.get_sitelinks(qid)
    langlinks = fetch_links(title)
    modifying = 'Modifying' in summary.decode('utf-8')
    add={}
    for lang in langlinks:
        if lang not in sitelinks:
            add[lang] = langlinks[lang]
        elif modifying and (langlinks[lang] != sitelinks[lang]):
            add[lang] = langlinks[lang]
    for lang in add:
        print add[lang]
        add_link(qid, **add[lang])

def add_link(qid, site, title):
    params = {'id':qid,
        'linksite':site,
        'linktitle':title,
        'summary':u'Bot: Importing interwikis from enwiki',
        'bot':'1'
    }
    res=repo.set_sitelinks(**params)
    print res

def main():
    cursor=db.cursor()
    cursor.execute(query)
    for row in cursor:
        print row
        go(row[0], row[1])

if __name__ == "__main__":
    main()

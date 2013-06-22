#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import pywikibot
import os
import time
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
LIMIT 200;
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


site = pywikibot.getSite()
repo = site.data_repository()

def fetch_links(title,db):
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

def go(title, summary,db):
    qid = repo.get_id('enwiki',title)
    if qid == '-1':
        return
    print 'Processing {}'.format(qid)
    sitelinks = repo.get_sitelinks(qid)
    langlinks = fetch_links(title,db)
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
    time.sleep(2)

def add_link(qid, site, title,showerror=False,source='en'):
    params = {'id':qid,
        'linksite':site,
        'linktitle':title,
        'summary':u'Bot: Importing interwikis from {0}wiki'.format(source),
        'bot':'1'
    }
    if not showerror:
        try:
            res=repo.set_sitelinks(**params)
        except pywikibot.data.api.APIError, e:
            print unicode(e).encode('utf-8')
            return #TODO: Log errors
        print res
    else:
        return repo.set_sitelinks(**params)

def main():
    import oursql
    db = oursql.connect(db='dewiki_p',
        host="dewiki-p.rrdb.toolserver.org",
        read_default_file=os.path.expanduser("~/.my.cnf"),
        charset=None,
        use_unicode=False
    )

    cursor=db.cursor()
    cursor.execute(query)
    for row in cursor:
        print row
        go(row[0], row[1],db)

if __name__ == "__main__":
    main()

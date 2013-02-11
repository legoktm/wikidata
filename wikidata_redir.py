#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import sys
import os
import oursql
import pywikibot

#figure out some language shit


get_langs = """
/* SLOW_OK */
SELECT
 dbname,
 lang
FROM toolserver.wiki
WHERE family = "wikipedia"
AND is_multilang =0
"""



query = """
/* SLOW_OK */
SELECT
 wd.ips_item_id,
 wd.ips_site_page
FROM wikidatawiki_p.wb_items_per_site AS wd
JOIN {db}.page AS page
ON wd.ips_site_page = page.page_title
WHERE wd.ips_site_id="{lang}wiki"
AND page.page_namespace=0
AND page.page_is_redirect=1;
"""
query_IDK = """
/* SLOW_OK */
SELECT
 wd.ips_item_id,
 wd.ips_site_page
FROM wikidatawiki_p.wb_items_per_site AS wd
JOIN {db}.page AS page
ON wd.ips_site_page = page.page_title
JOIN {db}.page_props AS page_props
ON page.page_id = page_props.pp_page
WHERE wd.ips_site_id="{lang}wiki"
AND page.page_namespace=0
AND page.page_is_redirect=1
AND NOT EXISTS (
    SELECT
     *
    FROM {db}.page_props AS pp
    WHERE pp.pp_page=page.page_id
    AND pp.pp_propname="staticredirect"
);
""" #TODO: ELIMINATE THE SUBQUERY
##this query doesnt use {lang} because some languages have -'s

redirect_target = """
/* SLOW_OK */
SELECT
 redir.rd_title,
 redir.rd_fragment
FROM {db}.redirect as redir
JOIN {db}.page as page
ON redir.rd_from = page.page_id
WHERE redir.rd_namespace = 0
AND page.page_namespace = 0
AND page.page_title=?;
"""
lang_links = """
/* SLOW_OK */
SELECT
 lang.ll_lang,
 lang.ll_title
FROM {db}.langlinks as lang
JOIN {db}.page as page
ON lang.ll_from = page.page_id
WHERE page.page_namespace = 0
AND page.page_title=?;
"""
wd_sitelinks = """
/* SLOW_OK */
SELECT
 wd.ips_site_id,
 wd.ips_site_page
FROM wikidatawiki_p.wb_items_per_site AS wd
WHERE wd.ips_item_id=?;
"""

ignore_replag = '--ignore-replag' in sys.argv

if ignore_replag:
    print 'WARNING: WILL IGNORE HIGH REPLAG'


site = pywikibot.getSite()
repo = site.data_repository()
wikidata = pywikibot.Site('wikidata','wikidata')

class Robot:
    def __init__(self, dbname, lang):
        self.dbname = dbname
        self.lang = lang
        self.data = {'db':self.dbname,
                     'lang':self.lang,
        }
        self.db = oursql.connect(
            host="{lang}wiki-p.rrdb.toolserver.org".format(**self.data),
            read_default_file=os.path.expanduser("~/.my.cnf"),
            charset=None,
            use_unicode=False
        )

    def fetch_target(self, title, id):
        cursor = self.db.cursor()
        cursor.execute(redirect_target.format(**self.data), (title,))
        data = cursor.fetchone()
        if not data:
            return
        if data[1]:
            row = list()
            for u in data:
                row.append(u.decode('utf-8'))
            #its a section link, lets log an error
            self.log_error('[[Q{0}]] - [[{lang}wiki:{1}]] is a section redirect to: [[{lang}wiki:{2}#{3}]]'.format(
                id, title.decode('utf-8'), *row, **self.data))
            return
        else:
            return data[0]

    def update_wd(self, id, new):
        qid = 'Q'+str(id)
        print (id, new)
        #x=raw_input('continue?')
        #page.setitem(summary=u"Bypassing redirect to [[:w:en:{0}]]".format(new),
        #    items={'type': u'sitelink', 'site': 'en', 'title': new},
        #)
        #page.setsitelinkhack(id, 'enwiki', new, "Bypassing redirect to [[:w:en:{0}]]".format(new))
        try:
            verify = self.verify_langlinks(new, id)
        except ZeroDivisionError:
            verify = False
        if not verify:
            new.decode('utf-8')
            self.log_error(u'[[{0}]] does not match 75% of [[{lang}wiki:{1}]]'.format(qid, new.decode('utf-8'),
                **self.data))
            return
        try:
            params = {'id':qid,
                      'linksite':'{lang}wiki'.format(**self.data),
                      'linktitle':new,
                      'summary':u"Bypassing redirect to [[:w:{lang}:{0}]]".format(new,**self.data),
                      'bot':'1'}
            print params
            repo.set_sitelinks(**params)
            #quit()
        except pywikibot.data.api.APIError, e:
            self.log_error('[[{0}]] - {1}'.format(qid, str(e)))
        except UnicodeDecodeError:
            #lol
            return

    def log_error(self, s):
        page=pywikibot.Page(wikidata, 'User:Legobot/Conflicts/{lang}wiki'.format(**self.data))
        try:
            old = page.get(force=True)
        except pywikibot.exceptions.NoPage:
            old = 'Once you have fixed an error on this list, please remove it. Thanks!\n'
        #tweak a bit
        s = s.replace('\n',' ')
        s = s.strip()
        if not s.startswith('*'):
            s='*'+s
        if s.endswith('.'):
            s = s[:-1]
        s=s.replace('[[{lang}wiki:'.format(**self.data),'[[:w:{lang}:'.format(**self.data))
        if s.encode('utf-8') in old.encode('utf-8'):
            print 'Already logged this error, skipping.'
            return
        new = old +'\n'+s
        page.put(new, 'Bot: Logging conflict/error')

    def verify_langlinks(self, target, qid):
        #fetch langlinks
        cursor=self.db.cursor()
        cursor.execute(lang_links.format(**self.data), (target,))
        rows=cursor.fetchall()
        local = dict()
        for row in rows:
            local[row[0]+'wiki'] = row[1]
        cursor.execute(wd_sitelinks, (qid,))
        rows = cursor.fetchall()
        wd = dict()
        for row in rows:
            wd[row[0]] = row[1]
        matching = 0
        #check if only one link
        if (len(wd.keys()) == 1) and (len(local.keys()) == 0):
            return True

        for lang in local.keys():
            if lang == '{lang}wiki'.format(**self.data): #skip
                continue
            if lang in wd:
                if wd[lang] == local[lang]:
                    matching +=1
        return (float(matching) / len(local.keys())) > .75

    def replag_is_low(self):
        query="SELECT UNIX_TIMESTAMP() - UNIX_TIMESTAMP(MAX(rc_timestamp)) FROM {db}.recentchanges;"
        if self.dbname != 'simplewiki_p':
            dbs = [self.dbname,]#'wikidatawiki_p'
        else:
            dbs=[]
        cursor=self.db.cursor()
        low = True
        for db_name in dbs:
            cursor.execute(query.format(db=db_name))
            lag=cursor.fetchone()[0]
            if lag==None:
                lag=99999999
            if int(lag) > 10:
                low = False
        if not low:
            print 'REPLAG IS HIGH.'
        return ignore_replag or low

    def run(self):
        if not self.replag_is_low():
            print 'Replag is too high. Will try again later'
            quit()
        print 'Running query'
        cursor = self.db.cursor()
        cursor.execute(query.format(**self.data))
        data = cursor.fetchall()
        print 'Fetched data'
        for id, page in data:
            target = self.fetch_target(page, id)

            if not target:
                continue
            print target
            self.update_wd(id, target)
        #lets close the db
        self.db.close()


def main():
    for arg in sys.argv:
        if arg.startswith('--start'):
            start_value = arg.split('=',1)[1]
            go=False
        else:
            go=True
    db_ts = oursql.connect(
        host="sql-toolserver",
        read_default_file=os.path.expanduser("~/.my.cnf"),
        charset=None,
        use_unicode=False
    )
    cur = db_ts.cursor()
    cur.execute(get_langs)
    data = cur.fetchall()
    for dbname, lang in data:
        if not go:
            if dbname.startswith(start_value):
                go=True
            else:
                continue
        if 'nostalgia' in dbname:
            print 'Skipping nostalgiawiki_p'
            continue
        elif 'simple' in dbname:
            print 'Skipping simplewiki_p'
            continue
        elif 'tenwiki' in dbname:
            print 'Skipping tenwiki_p'
            continue
        elif 'ru_sibwiki' in dbname:
            continue
        bot = Robot(dbname, lang)
        print 'Going to run on {db}.'.format(db=dbname)
        bot.run()


if __name__ == "__main__":
    pywikibot.handleArgs()
    main()

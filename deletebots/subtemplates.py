#!/usr/bin/python

import pywikibot
import oursql
import os
import sys

d = pywikibot.Site().data_repository()


def do(i):
    if not i.exists():
        print 'already deleted'
        return

    if len(i.sitelinks) > 1:
        print 'more than 1 sitelink, lets skip'
        return
    if i.claims:
        print 'has a claim, skipping'
        return
        #print i.getID()
    i.delete('Does not meet the [[Special:MyLanguage/Wikidata:Notability|notability policy]]: subtemplate',
             prompt=False)
    print 'deleted'

db = oursql.connect(db='wikidatawiki_p',
                    host='wikidatawiki.labsdb',
                    read_default_file=os.path.expanduser('~/replica.my.cnf'),
                    )

query = """
select
ips_item_id, ips_site_page
from wb_items_per_site
where ips_site_id="{0}wiki"
and ips_site_page like "{1}:%/%"
limit 1000;""".format(sys.argv[1], pywikibot.Site(sys.argv[1]).namespaces()[10][0])

def gen(db):
    c = 0
    while c < 100:
        c += 1
        with db.cursor() as cursor:
            cursor.execute(query)
            for row in cursor:
                if row[1].endswith('/'):
                    continue
                yield row[0]


for qid in gen(db):
    i = pywikibot.ItemPage(d, 'Q' + str(qid))
    print i
    do(i)

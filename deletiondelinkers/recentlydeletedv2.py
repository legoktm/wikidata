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
import oursql
import pywikibot
site = pywikibot.Site('en', 'wikipedia')
repo = site.data_repository()
query = """
select
 w.ips_item_id,
 w.ips_site_page
from enwiki_p.logging as l
join wikidatawiki_p.wb_items_per_site as w
on w.ips_site_page=l.log_title
where l.log_type="delete"
and l.log_action="delete"
and l.log_namespace=0
and w.ips_site_id="enwiki"
order by l.log_timestamp desc
limit 10;
 """

db = oursql.connect(
    host="enwiki-p.rrdb.toolserver.org",
    read_default_file=os.path.expanduser("~/.my.cnf"),
    charset=None,
    use_unicode=False
)

reason = 'Does not meet the [[Special:MyLanguage/Wikidata:Notability|notability policy]]: only linked article deleted'
with db.cursor() as cursor:
    cursor.execute(query)
    data = cursor.fetchall()
db.close()
for z in data:
    qid = 'Q' + str(z[0])
    print qid
    i = pywikibot.ItemPage(repo, qid)
    if not i.exists():
        continue
    p = pywikibot.Page(site, z[1])
    if p.exists():
        continue
    if 'en' in i.sitelinks and len(i.sitelinks) == 1:
        i.delete(reason, prompt=False)
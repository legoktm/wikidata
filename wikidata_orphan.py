#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero
"""
#mysql> select COUNT(*) from pagelinks where pl_namespace=120 AND pl_title="P31";
import sys
import os
import oursql
import pywikibot
pid = sys.argv[1]

query = """
SELECT
 page_title
FROM pagelinks
JOIN page
ON page_id=pl_from
WHERE pl_namespace=120
AND pl_title="{0}"
AND page_namespace=0
LIMIT 100;
""".format(pid)

site=pywikibot.Site('en','wikipedia')
repo=site.data_repository()
token=repo.token(pywikibot.Page(repo,u'Main Page'), 'edit')

db = oursql.connect(db='wikidatawiki_p',
    host="sql-s1-rr.toolserver.org",
    read_default_file=os.path.expanduser("~/.my.cnf"),
    raise_on_warnings=False,
)



def remove(id):

    params = {'claim':id,
              'token':token,
              'bot':1,
              'action':'wbremoveclaims'
    }
    result = repo.raw(**params)
    print result

def gen():
    cursor=db.cursor()
    cursor.execute(query)
    for row in cursor:
        yield row[0]

def main():
    for item in gen():
        claims = repo.get_claims(item)
        if not pid.lower() in claims:
            return
        for claim in claims[pid.lower()]:
            remove(claim['id'])

if __name__ == '__main__':
    main()

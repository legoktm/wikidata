#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import pywikibot

site=pywikibot.Site()
repo=site.data_repository()

def null_edit(qid):
    #fetch the links
    sitelinks=repo.get_sitelinks(qid)
    obj=sitelinks.values()[0]
    params = {'id':qid,
        'linksite':obj['site'],
        'linktitle':"",
        'summary':u"Bot: Making null edit",
        'bot':'1'
    }

    print repo.set_sitelinks(**params)
    print 'Removed'
    params['linktitle'] = obj['title']
    print repo.set_sitelinks(**params)
    print 'Re-instated'

def main():
    with open('wd_null.txt','r') as f:
        items = f.read()
    for item in items.splitlines():
        print item
        null_edit(item)
if __name__ == "__main__":
    main()
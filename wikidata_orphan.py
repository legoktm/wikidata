#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero
"""
import sys
import pywikibot
pid = sys.argv[1]


site = pywikibot.Site('en','wikipedia')
repo = site.data_repository()
token = repo.token(pywikibot.Page(repo,u'Main Page'), 'edit')

c = pywikibot.PropertyPage(repo, pid)
gen = c.getReferences(namespaces=[0])


def remove(item):
    for claim in item.claims:
        for cl in item.claims[claim]:
            if cl.getID() == c.getID():
                item.removeClaims([cl])


for i in gen:
    item = pywikibot.ItemPage(repo, i.title())
    item.get()
    remove(item)

#!/usr/bin/env python
"""
Released into the public domain.

Authors:
    Legoktm, 2013


Script to import links from Wikivoyage into Wikidata.

First check if we can parse a link pointing to Wikipedia from Extension:RelatedSites.

If so, see if that Wikipedia page has an item. If so, add the Wikivoyage links to that item.

If it doesn't have an item, we should create a new item with both Wikipedia and Wikivoyage links.

If there is no Wikipedia link, just create a separate Wikivoyage item. We should check ALL versions of the Wikivoyage to
ensure the links add up.
"""

import pywikibot
import re
import requests
import wdapi

enwiki = pywikibot.Site('en', 'wikipedia')
repo = enwiki.data_repository()

headers = {'User-agent': 'https://www.wikidata.org/wiki/User:Legobot'}
#<li class="interwiki-wikipedia"><a href="//en.wikipedia.org/wiki/New_York_City">Wikipedia</a></li>
#<li class="interwiki-wikipedia"><a href="//en.wikipedia.org/wiki/es:Ciudad_de_Nueva_York">Wikipedia</a></li>
REGEX = re.compile('<li class="interwiki-wikipedia"><a href="//en.wikipedia.org/wiki/(.*?)">Wikipedia</a></li>')


def bot(site):
    for page in site.allpages(namespace=0):
        do_page(page)


def do_page(page):
    #page is a wikivoyage page
    wp = get_wikipedia_link(page)
    if not wp:
        wdapi.createItem(page)
        return
    item = pywikibot.ItemPage.fromPage(wp)
    if item.exists():
        data = wdapi.createItem(page, dontactuallysave=True)
        item.editEntity(data, 'Importing Wikivoyage links from [[:voy:{0}:{1}]]'.format(page.title(), page.site.code))
    else:
        wdapi.createItem(page)  # TODO: Add the Wikipedia link here...


def get_wikipedia_link(page):
    site = page.site
    #print site.siteinfo
    url = 'http:' + site.siteinfo['server'] + site.nice_get_address(page.title())
    print url
    r = requests.get(url, headers=headers)
    print r.status_code
    text = r.text
    if 'interwiki-wikipedia' in text:
        print 'yes'
        match = REGEX.search(text)
        print match.group(0)
        print match.group(1)
        paage = pywikibot.Page(enwiki, match.group(1))
        return paage

if __name__ == '__main__':
    bot(pywikibot.Site('en', 'wikivoyage'))

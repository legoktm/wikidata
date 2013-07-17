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
from __future__ import unicode_literals
import pywikibot
from pywikibot.data import api
import re
import requests
import wdapi

enwiki = pywikibot.Site('en', 'wikipedia')
envoy = pywikibot.Site('en', 'wikivoyage')
repo = enwiki.data_repository()

headers = {'User-agent': 'https://www.wikidata.org/wiki/User:Legobot'}
#<li class="interwiki-wikipedia"><a href="//en.wikipedia.org/wiki/New_York_City">Wikipedia</a></li>
#<li class="interwiki-wikipedia"><a href="//en.wikipedia.org/wiki/es:Ciudad_de_Nueva_York">Wikipedia</a></li>
REGEX = re.compile('<li class="interwiki-wikipedia"><a href="//en.wikipedia.org/wiki/(.*?)">Wikipedia</a></li>')


def reportConflict(link1, link2):
    """
    @type link1: Link
    @type link2: Link
    @return: None
    """
    pg = '-'.join(sorted([link1.source.site.lang, link2.source.site.lang]))
    pg = 'Wikidata:Wikivoyage conflicts/' + pg
    page = pywikibot.Page(repo, pg)
    try:
        old = page.get()
    except pywikibot.NoPage:
        old = ''
    nt = 'WVC|lang={0}|lang1={1}|page1={2}|target1={3}|lang2={4}|page2={5}|target2={6}'.format(
        link1.lang,
        link1.source.site.code,
        link1.source.title(),
        link1.title,
        link2.source.site.code,
        link2.source.title(),
        link2.title,
    )
    if nt in old:
        print 'already reported'
        #quit()
        return
    nt = '\n*{{' + nt + '}}'
    pywikibot.output(nt.strip())
    page.put((old + nt).strip(), 'Bot: Adding new conflict report')
    print 'uhoh, conflict!'
    #quit()


class Link:
    def __init__(self, source, lang, title):
        #source is a pywikibot.Page, and the page where the link is
        self.source = source
        #language is a string, and refers to the language code of the link
        self.lang = lang
        #title is a string, and refers to the page name
        self.title = title
        self._page = None  # lazyyyyyyyy

    def __str__(self):
        return "[[{0}:{1}]]@{2}".format(self.lang, self.title, str(self.source))

    def __repr__(self):
        return 'Link({0})'.format(str(self))

    @property
    def page(self):
        if not self._page:
            try:
                self._page = WikivoyagePage(pywikibot.Site(self.lang, 'wikivoyage'), self.title)
            except pywikibot.exceptions.NoSuchSite:
                # wtf invalid interwiki link
                pass
        return self._page


class LinkStorage:
    def __init__(self):
        self.data = {}
        #{'en':Link, 'uk': Link}
        self.checked = []
        # A list of language code's we've checked against.
        self.safe = True
        # False if any conflicts have been reported.

    def __iter__(self):
        for lang in self.data:
            yield self.data[lang]

    def addLink(self, link):
        #We should check for conflicts.
        #We should have checked for redirects by now.
        if link.lang in self.data:
            if link.title == self.data[link.lang].title:
                #We're good.
                return True
            else:
                #Uhoh. We have a conflict.
                reportConflict(link, self.data[link.lang])
                self.safe = False
                return False
        else:
            #It's a newly found link.
            self.data[link.lang] = link
            return True

    @property
    def notchecked(self):
        # We wrap everything in list() to avoid RuntimeErrors if the
        # iterative size changes
        f = []
        for lang in list(self.data):
            if not lang in list(self.checked):
                f.append(lang)
        return f


class WikipediaLinkStorage:

    def __init__(self):
        self.items = dict()
        self._item = None

    def checkLinks(self, links):
        for link in links:
            self.items[link.lang] = link.page.wikidata
        if len(set(self.items.values())) > 1:
            self.item = self.items[0]

    @property
    def item(self):
        return self._item


class WikivoyagePage(pywikibot.Page):

    @property
    def wikipedia(self):
        if hasattr(self, '_wikipedia'):
            return self._wikipedia
        self._wikipedia = None
        site = self.site
        #print site.siteinfo
        url = 'http:' + site.siteinfo['server'] + site.nice_get_address(self.title())
        #print url
        r = requests.get(url, headers=headers)
        #print r.status_code
        text = r.text
        if 'interwiki-wikipedia' in text:
            #print 'yes'
            match = REGEX.search(text)
            #print match.group(0)
            #print match.group(1)
            paage = pywikibot.Page(enwiki, match.group(1))
            self._wikipedia = paage
        return self._wikipedia

    @property
    def wikidata(self):
        if not hasattr(self, '_wikidata'):
            self._wikidata = pywikibot.ItemPage.fromPage(self.wikipedia)
        return self._wikidata


    @property
    def langlinks(self):
        #return format is like
        #{'nlwikivoyage':'title','eswikivoyage':'title'}
        #Will also include an object for the current site.
        if hasattr(self, '_data'):
            return self._data
        self._data = []
        gen = api.PropertyGenerator('langlinks', titles=self.title(), lllimit='max',
                                    site=self.site,
                                    )
        for pg in gen:
            if 'langlinks' in pg:
                for obj in pg['langlinks']:
                    self._data.append(Link(source=self, lang=obj['lang'], title=obj['*']))
        return self._data


def test(title):
    nyc = WikivoyagePage(envoy, title)
    pywikibot.output(nyc)
    collector = LinkStorage()
    for link in nyc.langlinks:
        #pywikibot.output(link)
        collector.addLink(link)
    collector.checked.append(nyc.site.code)
    while collector.notchecked:
        for link in list(collector):
            if link.lang in collector.checked:
                continue
            pg = link.page
            if not pg:
                #invalid site
                del collector.data[link.lang]
                continue
            pywikibot.output(pg)
            for l in pg.langlinks:
                collector.addLink(l)
            collector.checked.append(link.lang)
        #at this point collector has the full interwiki map
    verifier = WikipediaLinkStorage()
    verifier.checkLinks(collector.data)
    #if verifier.item:
    #   add the voy links to WD
    #else:
    #   report
    print 'done'


if __name__ == '__main__':
    for pg in envoy.allpages(namespace=0, filterredir=False):
        #pywikibot.output(pg.title())
        test(pg.title())
    #test('New York City')
    #test('New York (state)')
    #test('San Jose')
    test('Acre')

#!/usr/bin/env python
"""
Released into the public domain.

Authors:
    Legoktm, 2013

Fetches a list of the properties created in the last week for [[d:Wikidata:Status updates/Next]]
"""
import datetime
import pywikibot
from pywikibot.data import api
import re

#action=query&list=recentchanges&rctype=new&rcnamespace=120&format=jsonfm&rclimit=max

site = pywikibot.Site('wikidata', 'wikidata')
repo = site.data_repository()
page = pywikibot.Page(site, 'Wikidata:Status updates/Next')
oneweek = pywikibot.Timestamp.today() - datetime.timedelta(days=7)
params = {'action': 'query',
          'list': 'recentchanges',
          'rctype': 'new',
          'rcnamespace': '120',
          'rclimit': 'max',
          'rcend': str(oneweek),
          }

req = api.Request(site=site, **params)
data = req.submit()
l = []
for pg in data['query']['recentchanges']:
    l.append(pg['title'].split(':P')[1])

def make_link(pid):
    prop = pywikibot.PropertyPage(repo, pid)
    prop.get()
    label = prop.labels['en']
    return '[[:d:Property:{0}|{1}]]'.format(pid, label)


t = ''
for pid in l:
    t += '{0}, '.format(make_link('P'+pid))
if t:
    t = t[:-2]
else:
    t = 'none'

TOP_MARKER = '<!-- NEW PROPERTIES DO NOT REMOVE -->'
BOTTOM_MARKER = '<!-- END NEW PROPERTIES -->'
PRE_TEXT = '* Newest [[d:Special:ListProperties|properties]]: '

newtext = re.sub('%s.*?\n%s' % (TOP_MARKER, BOTTOM_MARKER), TOP_MARKER + '\n' + PRE_TEXT + t + '\n' + BOTTOM_MARKER, page.get(), flags=re.DOTALL)
pywikibot.showDiff(page.get(), newtext)
page.put(newtext, 'Bot: Updating list of new properties')

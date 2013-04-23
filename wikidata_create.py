#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import sys
import json
import time
import pywikibot
from pywikibot.data import api
from pywikibot import config

config.put_throttle = 0

enwp = pywikibot.Site('en', 'wikipedia')
repo = enwp.data_repository()
#pywikibot.handleArgs()

def create_item(site, title, token=None,check=True,labels=True):
    wiki = site.dbName()
    lang = site.language()
    item = pywikibot.ItemPage.fromPage(pywikibot.Page(site, title))
    if check and item.exists():
        print 'Has already been imported, will not create.'
        return None
    #fetch the lang links
    params = {'action': 'query',
              'titles': title,
              'prop': 'langlinks',
              'lllimit': 'max'
    }
    req = api.Request(site=site, **params)
    data = req.submit()
    try:
        links = data['query']['pages'].values()[0]['langlinks']
    except KeyError: #no langlinks
        links = []
    print 'Fetched {0} local langlinks.'.format(len(links))
    sitelinks = {wiki:{'site':wiki,'title':title}}
    labels = {lang:{'language': lang, 'value':title}}
    for link in links:
        if '#' in link['*']:
            continue
        s=link['lang'].replace('-','_')+'wiki'
        sitelinks[s]={'site':s,'title':link['*']}
        labels[link['lang']]={'language':link['lang'],'value':link['*']}
    raw_data = {'sitelinks':sitelinks}
    if labels:
        raw_data['labels'] = labels
    export = json.dumps(raw_data)
    p2 = {'action':'wbeditentity',
          'data':export,
          'summary':'Importing from [[:w:{0}:{1}]]'.format(lang, title),
          'bot':1
    }
    if token:
        p2['token'] = token
    else:
        p2['token'] = repo.token(pywikibot.Page(repo, 'Main Page'), 'edit')
    #print p2
    create = api.Request(site=repo, **p2)
    print 'Submitting creation request...'
    try:
        done = create.submit()
    except pywikibot.data.api.APIError, e:
        ec = e
        e = unicode(e)
        if 'already exists' in e or e=='':
            #whatthefuck
            return create_item(site, title, token=token, check=check, labels=labels) #fuckit
        elif 'The external client site did' in e:
            print 'external client site'
            return '-1' #yeah wtf
        elif 'already used by item' in e:
            #print 'already used by...'
            print ec.info
            return '-1'
        else:
            try:
                print repr(unicode(e))#.decode('utf-8'))
                raise pywikibot.data.api.APIError, e
            except:
                return None
    if 'success' in done:
        print 'Successful!'
    else:
        print done
#    time.sleep(3)
    return done['entity']['id']  # send back the qid

def mass_create(lang, titles, token=None):
    r=[]
    for title in titles:
        r.append(create_item(lang, title, token=token))
    return r

def allpages():
    params = {}
    if '-help' in sys.argv:
        params['namespace'] = 12
    else:
        params['namespace'] = 14
        params['start'] = 'Q'
    params['filterredir'] = False
    token = repo.token(pywikibot.Page(repo, 'Main Page'), 'edit')
    enwp = pywikibot.Site('en','wikipedia')
    ap = enwp.allpages(content=True,**params)
    for page in ap:
        for t in ['soft redirect','softredir', 'soft link']:
            if t in page.get().lower():
                print 'Skipping soft redirect'
                continue
        print create_item(enwp, page.title(), token, labels=True)
if '--allpages' in sys.argv:
    print 'running allpages'
    allpages()
    quit()

if __name__ == "__main__":
    repo.login()
    #d=['Eschatology: Death and Eternal Life', 'The Spirit of the Liturgy','Truth and Tolerance']
    #print mass_create('en',d)
    #create_item('en','Category:American chemical engineers')
    if len(sys.argv) > 1:
        category=pywikibot.Category(enwp, sys.argv[1])
    else:
        category=pywikibot.Category(enwp, 'Category:Game developer logos')
    for i in category.articles(recurse=True, namespaces=[6]):
        print i
        x=create_item(enwp,i.title(),labels=True)

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
import pywikibot
import sys
from pywikibot.data import api

site = pywikibot.Site('wikidata','wikidata')
if not site.logged_in():
    site.login()
#print site.username()
#action=query&list=recentchanges&rcuser=Dexbot&rclimit=max&rcshow=!patrolled&rctoken=patrol'


def fetch_whitelist():
        #list=allusers&augroup=sysop|autopatrolled&format=jsonfm&aulimit=max
    params = {'site': site,
              'augroup': 'sysop|autopatrolled|bot',
              }
    gen = api.ListGenerator('allusers', **params)
    for u in gen:
        yield u['name']


def fetch(user):
    params = {'rcuser':user,
              'rclimit':'max',
              'rcshow':'!patrolled',
              'rctoken':'patrol',
              }
    gen = api.ListGenerator('recentchanges', site=site, **params)
    for change in gen:
        print change
        yield change['rcid'], change['patroltoken']


def patrol(rcid, token):
    params = {'action':'patrol',
              'rcid':rcid,
              'token':token
    }
    req = api.Request(site=site, **params)
    try:
        data = req.submit()
    except pywikibot.data.api.APIError, e:
        print e.code
        print e.info
        #print 'error'
        return
    print data


def main():
    page = pywikibot.Page(site, 'User:Legobot/autopatrol.js')
    text = page.get()
    users = text.splitlines()
    for user in users:
        if user.startswith('#') or not user:
            continue
        print user
        gen = fetch(user)
        for c in gen:
            patrol(*c)
        newtext = page.get(force=True)
        newtext = newtext.replace(user+'\n','')
        page.put(newtext, 'Removing fully-patrolled user')


if __name__ == "__main__":
    if '--all' in sys.argv:
        for user in fetch_whitelist():
            print user
            for c in fetch(user):
                patrol(*c)
    elif len(sys.argv) > 1:
        print sys.argv[1]
        for c in fetch(sys.argv[1]):
            patrol(*c)
    else:
        main()

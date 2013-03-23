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
from pywikibot.data import api
site = pywikibot.Site('wikidata','wikidata')

def get_users():
    #action=query&list=allusers&augroup=confirmed&auprop=groups&aulimit=max&format=jsonfm
    params = {'action':'query',
              'list':'allusers',
              'augroup':'confirmed',
              'auprop':'groups',
              'aulimit':'max'
    }
    req = api.Request(site=site, **params)
    data = req.submit()
    for user in data['query']['allusers']:
        if 'autoconfirmed' in user['groups']:
            print user
            yield user['name']

def change_rights(user):
    #fetch token
    #action=query&list=users&ususers=Legoktm&ustoken=userrights&format=jsonfm
    t_params = {'action':'query',
                'list':'users',
                'ususers':user,
                'ustoken':'userrights'
    }
    t_req = api.Request(site=site, **t_params)
    t_data = t_req.submit()
    token = t_data['query']['users'][0]['userrightstoken']
    #really change rights
    params = {'action':'userrights',
              'user':user,
              'token':token,
              'remove':'confirmed',
              'reason':'User is autoconfirmed'
    }
    print params
    req = api.Request(site=site, **params)
    data = req.submit()
    print data

def main():
    for user in get_users():
        print user
        change_rights(user)

if __name__ == "__main__":
    pywikibot.handleArgs()
    main()
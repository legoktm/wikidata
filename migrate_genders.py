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
repo = pywikibot.Site('en','wikipedia').data_repository()
male = pywikibot.ItemPage(repo, 'Q6581097')
female = pywikibot.ItemPage(repo, 'Q6581072')
migrate = {'q44148': male,
           'q43445': female,
           }

pywikibot.handleArgs()


def gen():
    oldmale = pywikibot.ItemPage(repo, 'Q44148')
    oldfemale = pywikibot.ItemPage(repo, 'Q43445')
    for page in oldmale.getReferences(namespaces=[0]):
        yield page
    for page in oldfemale.getReferences(namespaces=[0]):
        yield page

for page in gen():
    item = pywikibot.ItemPage(repo, page.title())
    print item.getID()
    try:
        item.get()
    except KeyError:
        continue
    except KeyboardInterrupt:
        print 'quitting...'
        quit()
#    except:
#        continue
    if 'p21' in item.claims:
        for claim in item.claims['p21']:
            if not claim.getTarget():
                continue
            if claim.getTarget().getID().lower() in migrate:
                new = migrate[claim.getTarget().getID().lower()]
                try:
                    claim.changeTarget(value=new, bot=1)
                except pywikibot.data.api.APIError, e:
                    print e.code.encode('utf-8')
                    print e.info.encode('utf-8')
                    #quit()
                #    pass
                #fuckit

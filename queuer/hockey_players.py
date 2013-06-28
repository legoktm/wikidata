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
import mwparserfromhell as mwparser
import os
#os.environ['PYWIKIBOT2_DIR'] = '/data/project/legobot/.pywikibot'
import pywikibot
from pywikibot import config
#import oursql
import re
import sys
sys.path.append(os.path.expanduser('~'))
import wikidata_create
import threading
from Queue import Queue
redirects = ['Infobox Ice Hockey Player','Infobox NHL Player','Infobox ice sledge hockey player','Infobox ice hockey player']
config.put_throttle = 0
enwp = pywikibot.Site('en', 'wikipedia')
if not enwp.logged_in():
    enwp.login()
repo = enwp.data_repository()
if not repo.logged_in():
    repo.login()
ENWP_ITEM = pywikibot.ItemPage(repo, 'Q328')
IMPORTED_FROM = pywikibot.Claim(repo ,'p143')
IMPORTED_FROM.setTarget(ENWP_ITEM)
regex = re.compile('\[\[(.*?)(\|.*?|)\]\]')
CLAIM = pywikibot.Claim(repo, 'p54')

def strip(text):
    x = regex.search(text)
    if not x:
        raise ValueError
    return x.group(1)

fetched = Queue()
processed = Queue()
parsed = Queue()
insert = Queue()
check = Queue()


class ParseThread(threading.Thread):
    """
    Parse the pages using mwparser
    reads from processed queue
    """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            page, item = self.queue.get()
            self.main(page, item)
            self.queue.task_done()

    def main(self, page, item):
        print 'Parsing ' + page.title()
        code = mwparser.parse(page.get())
        found = False
        template = ''  # to make pycharm shut up
        for template in code.filter_templates():
            if template.name.strip() in redirects:
                found = True
                break
        if not found:
            print 'Could not find template on ' + page.title()
            return
        data = dictify(template)
        targets = list()
        if 'team' in data:
            try:
                team = strip(data['team'])
                targets.append(team)
            except ValueError:
                pass
        else:
            print 'No team found for ' + page.title()
            print 'Checking played_for'
            if 'played_for' in data and not ('\'\'\'' in data['played_for']):
                sp = data['played_for'].split('<br />')
                for team in sp:
                    try:
                        team = strip(team)
                        targets.append(team)
                    except ValueError:
                        continue
        if targets:
            check.put((item, targets))


class CheckThread(threading.Thread):
    """
    Checks against redirects/stuff
    reads from check queue
    """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            item, targets = self.queue.get()
            self.main(item, targets)
            self.queue.task_done()

    def main(self, item, targets):
        for team in targets:
            push = True
            t = pywikibot.Page(enwp, team)
            if not t.exists():
                continue
            if t.isRedirectPage():  # laaaaaaaaaaaame
                t = t.getRedirectTarget()
            target = pywikibot.ItemPage.fromPage(t)
            if 'p54' in item.claims:
                for c in item.claims['p54']:
                    if c.getTarget().getID() == target.getID():
                        print page.title() + ' already has it'
                        push = False
                        break
            if push:
                parsed.put((item, target))
                print 'Sent onwards!'



class InsertThread(threading.Thread):
    """
    Saves to Wikidata
    reads from parsed queue
    """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            item, target = self.queue.get()
            self.main(item, target)
            self.queue.task_done()

    def main(self, item, target):
        CLAIM.setTarget(target)
        try:
            item.addClaim(CLAIM)
        except pywikibot.NoPage:
            return
        print '{0} --> {0}'.format(item.getID(), target.getID())
        CLAIM.addSource(IMPORTED_FROM)



class GetIDThread(threading.Thread):
    """
    Gets the id or creates the item
    reads from fetched queue
    """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            page = self.queue.get()
            self.main(page)
            self.queue.task_done()

    def main(self, page):
        item = pywikibot.ItemPage.fromPage(page)
        print 'Getting ID for ' + page.title()
        if not item.exists():
            qid = wikidata_create.create_item(enwp, page.title(), token=token, check=False, labels=True)
            if not qid or str(qid) == '-1':
                print 'no id for ' + page.title()
                return
        try:
            item.get(force=True)
        except pywikibot.data.api.APIError:
            return
        print item.getID()
        processed.put((page, item))




token = repo.token(pywikibot.Page(repo, u'Main Page'), 'edit')


def dictify(template):
    data = {}
    for param in template.params:
        data[unicode(param.name).strip().lower()] = unicode(param.value).strip()
    return data

for i in range(1):
    t = ParseThread(processed)
    t.setDaemon(True)
    t.start()

for i in range(1):
    t = CheckThread(check)
    t.setDaemon(True)
    t.start()

for i in range(1):
    t = InsertThread(parsed)
    t.setDaemon(True)
    t.start()

for i in range(1):
    t = GetIDThread(fetched)
    t.setDaemon(True)
    t.start()

template = pywikibot.Page(enwp, 'Template:Infobox ice hockey player')
gen = template.getReferences(onlyTemplateInclusion=True, namespaces=[0], content=True)
count = 0
for page in gen:
    count += 1
    if count % 100 == 0:
        print count
    #print page
    fetched.put(page)

#exit in order
fetched.join()
processed.join()
parsed.join()

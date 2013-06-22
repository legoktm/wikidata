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
os.environ['PYWIKIBOT2_DIR'] = '/data/project/legobot/.pywikibot'
import pywikibot
import oursql
import sys
import time
sys.path.append(os.path.expanduser('~'))
import wikidata_create
import threading
import Queue
redirects = ['biografia','bio']

itwiki = pywikibot.Site('it', 'wikipedia')
if not itwiki.logged_in():
    itwiki.login()
repo = itwiki.data_repository()
if not repo.logged_in():
    repo.login()
fetched = Queue.Queue(maxsize=100)
processed = Queue.Queue()
parsed = Queue.Queue()
insert = Queue.Queue()


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
            page, qid = self.queue.get()
            code = mwparser.parse(page.get())
            found = False
            template = ''  # to make pycharm shut up
            for template in code.filter_templates():
                if template.name.lower().strip() in redirects:
                    found = True
                    break
            if not found:
                print 'Could not find template on '+page.title()
                return
            data = dictify(template)
            d = list()
            for nm in data:
                if not data[nm] or len(data[nm]) > 250:
                    continue
                d.append((None, page.title(), deqid(qid), nm, data[nm]))
            parsed.put(d)
            self.queue.task_done()


class InsertThread(threading.Thread):
    """
    Inserts into the db
    reads from parsed queue
    """
    def __init__(self, queue, db):
        threading.Thread.__init__(self)
        self.queue = queue
        self.db = db
        self.cursor = self.db.cursor()

    def run(self):
        while True:
            d = self.queue.get()
            store(self.cursor, d)
            self.queue.task_done()


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
            item = pywikibot.ItemPage.fromPage(page)
            if not item.exists():
                qid = wikidata_create.create_item(itwiki, page.title(), token=token, check=False, labels=True)
            else:
                qid = item.getID()
            if not qid or qid == '-1':
                return
            processed.put((page, qid))
            self.queue.task_done()




token = repo.token(pywikibot.Page(repo, 'Main Page'), 'edit')


def deqid(qid):
    return int(qid.replace('q',''))


def dictify(template):
    data = {}
    for param in template.params:
        data[unicode(param.name).strip().lower()] = unicode(param.value).strip()
    return data


def store(cursor, stuff):
    print len(stuff)
        #print (None, title, qid, param, value)
    #page VARCHAR(255), qid INT, param VARCHAR(255), value VARCHAR(255)
    cursor.executemany('INSERT INTO `persondata` VALUES (?, ?, ?, ?, ?)',
                       stuff)
    #(None, title, deqid(qid), param, value)

db = oursql.connect(raise_on_warnings=False,
                    read_default_file=os.path.expanduser("~/.my.cnf"),
                    )


for i in range(2):
    t = ParseThread(processed)
    t.setDaemon(True)
    t.start()

for i in range(2):
    t = InsertThread(parsed, db)
    t.setDaemon(True)
    t.start()

for i in range(1):
    t = GetIDThread(fetched)
    t.setDaemon(True)
    t.start()

template = pywikibot.Page(itwiki, 'Template:Bio')
gen = template.getReferences(onlyTemplateInclusion=True, namespaces=[0], content=True)
count = 0
for page in gen:
    count += 1
    if count % 100 == 0:
        print count
    put = False
    while not put:
        try:
            fetched.put(page)
            put = True
        except Queue.Full:
            time.sleep(30)

#exit in order
fetched.join()
processed.join()
parsed.join()
insert.join()
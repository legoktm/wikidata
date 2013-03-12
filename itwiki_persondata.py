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
import pywikibot
import oursql
import os
import wikidata_create

redirects = ['biografia','bio']

itwiki = pywikibot.Site('it','wikipedia')
repo = pywikibot.Site().data_repository()

mapping = {'Sesso':'sex', #either M or F
       }

token = repo.token(pywikibot.Page(repo, 'Main Page'), 'edit')

def parse_page(page, db):
    text= page.get()
    code = mwparser.parse(text)
    found = False
    for template in code.filter_templates():
        if template.name.lower().strip() in redirects:
            found = True
            break
    if not found:
        print 'Could not find template on '+page.title()
        return
    #ok lets get the wikidata item
    qid = repo.get_id('itwiki', page.title())
    if qid == '-1':
        qid = wikidata_create.create_item('it', page.title(), token=token, check=False, labels=True)
    if not qid:
        return

    cursor = db.cursor()
    data = dictify(template)
    d = list()
    for nm in data:
        if not data[nm] or len(data[nm]) > 250:
            continue
        d.append((None, page.title(), deqid(qid), nm, data[nm]))
        #d.append((None, page.title(), None, nm, data[nm]))

    store(cursor, d)


def deqid(qid):
    return int(qid.replace('q',''))

def dictify(template):
    data = {}
    for param in template.params:
        data[unicode(param.name).strip().lower()] = unicode(param.value).strip()
    return data


def store(cursor, stuff):
    print len(stuff)
    for x in stuff:
        print x
    #print (None, title, qid, param, value)
    #page VARCHAR(255), qid INT, param VARCHAR(255), value VARCHAR(255)
    cursor.executemany('INSERT INTO `persondata` VALUES (?, ?, ?, ?, ?)',
                   stuff)
    #(None, title, deqid(qid), param, value)



def main():
    db = oursql.connect(db='legoktm',
                        host='localhost',
                        raise_on_warnings=False,
                        read_default_file=os.path.expanduser("~/.my.cnf"),
    )
    template = pywikibot.Page(itwiki, 'Template:Bio')
    gen = template.getReferences(onlyTemplateInclusion=True, namespaces=[0], content=True)
    for page in gen:
        parse_page(page, db)


if __name__ == "__main__":
    main()
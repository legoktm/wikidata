#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import sys
import os
#import oursql
import time
import pywikibot
from pywikibot import textlib
import xmlreader
import mw
import settings
import datetime
import wikidata_create
from wikidata_rc import add_link #this should be moved into its own library eventually

#set up some globals

if len(sys.argv) > 1:
    wiki = sys.argv[1]
else:
    wiki = 'enwiki'

g_lang = wiki.replace('wiki','')
print 'Operating on '+wiki

#autotranslatable summaries

editsummary = {'default':'Bot: Migrating langlinks to [[WP:Wikidata]] - [[d:{0}]]',
               'he':'בוט: מעביר קישורי בינויקי ל[[ויקיפדיה:ויקינתונים|ויקינתונים]] - [[d:{0}]]'
}

PATH = '/home/legoktm/public_html/import/'
PROGRESS = PATH + '{0}_progress.txt'.format(g_lang)
DUMP = '/mnt/user-store/dumps/{0}-latest-pages-articles.xml'.format(wiki)
py_enwp = pywikibot.Site(g_lang,'wikipedia')
enwp = mw.Wiki('http://{0}.wikipedia.org/w/api.php'.format(g_lang))
enwp.login(settings.username, settings.password)


def union(a, b):
    return list(set(a) | set(b))

checktool = '//toolserver.org/~legoktm/cgi-bin/wikidata/checker.py?site={0}&id='.format(g_lang)

class Log:
    def __init__(self):
        self.enwp = py_enwp
        self.basepage = u'User:Legobot/Wikidata/'
        self.sp = None
        self.storage = None

    def done(self, page,id, notes=''):
        #self.insert(page.site.language(), page.title(), 1, notes,id)
        return True
    def error(self, object, reason,id,project=None):
        if 'no-external-page' in reason:
            return
        if project:
            suffix=project
        else:
            suffix = 'General'
        page = pywikibot.Page(self.enwp, self.basepage+suffix)
        if not self.sp:
            self.sp = page
        if self.sp != page:
            self.sp = page
            self.storage = None
        if self.storage == None:
            if page.exists():
                self.storage = page.get(force=True)
            else:
                self.storage = ''
        if id and id in self.storage:
            return
        if object['title'] in self.storage:
            return
        print 'Bot, logging error'
        reason = reason.replace('\n',' ') #should really fix the "xxwiki" syntax. Oh well
        if id:
            text = '\n*[[{0}]] ([[d:{1}]] - [{3}{1} check]) - {2}'.format(object['title'], id, reason, checktool)
        else:
            text = '\n*[[{0}]] - {2}'.format(object['title'], id, reason)
        page.text= text.decode('utf-8')
        self.enwp.editpage(page, 'Bot: Logging conflict', append=True)




class Generator:
    def __init__(self, api):
        self.api = api
        self.dump = xmlreader.XmlDump(DUMP)
    def run(self):
        storage = list()
        for page in self.inner_gen():
            storage.append(page)
            if len(storage) == 499:
                for p in self.check(storage):
                    yield p
                storage = list()


    def check(self, data):
        #data is list of "page" objects
        ids = [str(p.id) for p in data]
        params = {'action':'query',
                  'prop':'revisions|info',
                  'rvprop':'ids',
                  'pageids':'|'.join(ids)
        }
        values = {}
        for pg in data:
            values[str(pg.id)] = {'revid':pg.revisionid, 'content':pg.text,'title':pg.title}
        req = self.api.request(params)
        need_update = list()
        pages = req['query']['pages']
        for pageid in pages:
            if 'missing' in pages[pageid]:
                del values[str(pageid)] #deleted
                continue
            elif 'redirect' in pages[pageid]:
                del values[str(pageid)] #is a redirect now
                continue
            if not 'revisions' in pages[pageid]:
                del values[str(pageid)] #deleted i guess
                continue
            revision = pages[pageid]['revisions'][0]
            if revision['revid'] != values[pageid]['revid']:
                need_update.append(pageid)
        if need_update:
            params['rvprop'] = 'content'
            params['pageids'] = '|'.join(need_update)
            req = self.api.request(params)
            pages = req['query']['pages']
            for pageid in pages:
                if 'missing' in pages[pageid]:
                    del values[str(pageid)]
                    continue
                if not 'revisions' in pages[pageid]:
                    del values[str(pageid)] #deleted i guess
                    continue
                revision = pages[pageid]['revisions'][0]
                values[pageid]['content'] = revision['*']
        for page in values:
            yield values[page]

    def inner_gen(self):
        gen = self.dump.parse()
        for page in gen:
            if (page.ns != 2) and (page.ns % 2 == 0) and not page.isredirect:
                yield page

class WikidataBot:
    def __init__(self):
        self.enwp = pywikibot.Site(g_lang,'wikipedia')
        self.repo = self.enwp.data_repository()
        self.token = self.repo.token(pywikibot.Page(self.repo, 'Main Page'), 'edit')
        self.enwp_token = self.enwp.token(pywikibot.Page(self.enwp, 'User:Legoktm'), 'edit')
        self.logger = Log()
        self.override = False
        self.count = 40

    def process(self, object):
        #object = {'revid', 'content', 'title'}

        qid = self.repo.get_id(g_lang+'wiki', object['title'])
        if not self.override:
            print qid
        id = int(qid.lower().replace('q','')) #int-ify
        created = False
        if id == -1:
            #print 'Item doesn\'t exist, creating now.'
            #try:
            #    qid = wikidata_create.create_item('en', object['title'], token=self.token,check=False)
            #    created = True
                #time.sleep(2)
            #except pywikibot.data.api.APIError:
            return self.logger.error(object, 'Item does not exist.',None)
        #if we just created, that means the links are exact.
        #if created:
        #    self.remove_links(object, qid)
        if self.override:
            self.remove_links(object, qid)
            return
        locallanglinks = textlib.getLanguageLinks(object['content'], insite=self.enwp)
        #print locallanglinks
        if not locallanglinks:
            print 'no local langlinks'
            return
        #fetch foreign links
        sitelinks = self.repo.get_sitelinks(qid)
        #lets reformat sitelinks
        wd_links = {}
        for lang in sitelinks:
            wd_links[lang.replace('_','-')] = sitelinks[lang]['title']
        sitelinks = wd_links
        all_langs = union(sitelinks.keys(), locallanglinks.keys())
        #print len(sitelinks.keys())
        to_add = {}
        allgood=True
        errors=list()
        for lang in all_langs:
            ok=True
            prefix = lang.replace('wiki','')
            l = locallanglinks.get(lang, None)
            if l:
                l = l.strip()
            f = sitelinks.get(lang, None)
            if f:
                f = f.strip()
            if l == f:
                continue
            elif l and not f:
                to_add[lang] = l
            elif l and f:
                #they both exist and arent equal
                checked=False
                s = pywikibot.Site(prefix, 'wikipedia')
                print l
                print f
                l_p = pywikibot.Page(s, l)
                try:
                    if not l_p.exists():
                        #safe to remove anyways i guess.
                        continue
                except AttributeError:
                    #AttributeError: 'Page' object has no attribute '_pageid'
                    #not sure what causes this exactly
                    errors.append(lang)
                    continue
                f_p = pywikibot.Page(s, f)
                if l_p.isRedirectPage():
                    if f_p == l_p.getRedirectTarget():
                        checked=True
                elif f_p.isRedirectPage():
                    if l_p == f_p.getRedirectTarget():
                        checked=True
                if not checked:
                    allgood=False
                    ok=False
            if not ok:
                errors.append(lang)


        for langwiki in to_add:
            try:
                data = add_link(qid, langwiki.replace('-','_'), to_add[langwiki], showerror=True,source=g_lang)
            except pywikibot.data.api.APIError, e:
                return self.logger.error(object, unicode(e).encode('utf-8'), qid)
            if not 'success' in data:
                return self.logger.error(object, 'Error while adding [[:{0}:{1}]] to wikidata.'.format(langwiki.replace('wiki',''), to_add[langwiki]),qid)
            else:
                print 'Added '+langwiki
        #log some errors
        if errors:
            for error in errors:
                self.logger.error(object, '', qid, project=error)
            print 'Logged errors, won\'t continue'
            return
        if not allgood: #this shouldnt be possible logically, but lets be safe
            print 'Not safe to proceed.'
            return

        #we should be good now
        try:
            self.remove_links(object, qid)
        except pywikibot.data.api.TimeoutError:
            pass #it probably went through anyways

    def translate(self, msg):
        if g_lang in msg:
            return msg[g_lang]
        else:
            return msg['default']

    def remove_links(self, object, qid):
        if self.count > 50:
            print 'TRIAL OVER'
            sys.exit()
        newtext = textlib.removeLanguageLinks(object['content'], self.enwp)
        #need to build a page object
        page = pywikibot.Page(self.enwp, object['title'])
        page.text = newtext
        summary = self.translate(editsummary).format(qid)
        try:
            self.enwp.editpage(
                page,
                summary,
                nocreate=True,
                lastrev=int(object['revid']),
                token=self.enwp_token,
                skipec=True
            )
            self.count += 1
            print 'COUNT: '+str(self.count)
            return
        except pywikibot.exceptions.LockedPage:
            return self.logger.error(object, 'Page was protected.',qid)
        except pywikibot.exceptions.EditConflict:
            return self.logger.error(object, 'Edit conflict.',qid)
        #except:
        #    return self.logger.error(object, 'Wtf error.', qid)

    def run(self, gen=None):
        if gen:
            self.override = True
        else:
            gen_obj = Generator(enwp)
            gen = gen_obj.run()

        for object in gen:
            #print object['title']
            try:
                self.process(object)
            except UnicodeDecodeError:
                pass
            except UnicodeEncodeError:
                pass

if __name__ == "__main__":
    pywikibot.handleArgs()
    bot = WikidataBot()
    bot.run()
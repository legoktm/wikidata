#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import pywikibot
import mwparserfromhell as mwparser
import wikidata_create

#TODO: Write error logging methods

class PropBot:
    def __init__(self, lang, source, pid, target_qid, summary, **kwargs):
        self.lang = lang
        self.source = source
        self.pid = pid
        self.target_qid = target_qid
        self.target = int(self.target_qid.lower().replace('q',''))
        self.summary = summary
        self.local_site = pywikibot.Site(self.lang, 'wikipedia')
        self.repo = pywikibot.Site().data_repository()
        self.wikidata = pywikibot.Site('wikidata','wikidata')
        self.token = self.wikidata.token(pywikibot.Page(self.wikidata, 'Main Page'), 'edit')
        self.options(kwargs)


    def options(self, kwargs):
        self.create = False
        self.ignoreprefix = None
        self.ignore = None
        if 'create' in kwargs:
            self.create = kwargs['create']
        if 'ignoreprefix' in kwargs: #TODO: Allow CSV here
            self.ignoreprefix = kwargs['ignoreprefix']
        if 'ignore' in kwargs:
            self.ignore = kwargs['ignore']


    def run(self):
        if self.source.startswith(tuple(self.local_site.namespaces()[14])):
            category = pywikibot.Category(self.local_site, self.source)
            print 'Fetching {0}'.format(category.title())
            gen = category.articles(namespaces=[0])
        elif self.source.startswith(tuple(self.local_site.namespaces()[10])):
            template = pywikibot.Page(self.local_site, self.source)
            gen = template.getReferences(follow_redirects=False, onlyTemplateInclusion=True, namespaces=[0])
        else:
            #bad input
            return
        for page in gen:
            #run it against our checks first
            #TODO: These checks should be their own method for modularity
            if page.title().startswith(self.ignoreprefix):
                return
            elif self.ignore and (page.title() in self.ignore):
                return

            self.do_page(page)

    def do_page(self, page):
        #find the item
        print page
        site = self.lang + 'wiki' #haaaack
        title = page.title()
        qid = self.repo.get_id(site, title)
        print qid
        id = int(qid.lower().replace('q','')) #int-ify
        if id == -1:
            print 'Item doesn\'t exist!'
            if not self.create:
                return
            print 'Creating now...'
            qid = wikidata_create.create_item(self.lang, title, token=self.token,check=False)
            id = int(qid.lower().replace('q','')) #int-ify
        params = {'entity':qid,
                  'property':self.pid,
                  'snaktype':'value',
                  'value':'{{"entity-type":"item","numeric-id":{0}}}'.format(self.target),
                  'token':self.token,
                  'bot':1
        }
        result = self.repo.set_claim(**params)
        print result

class FeedBot:
    def __init__(self):
        self.site = pywikibot.Site('wikidata','wikidata')
        self.page = pywikibot.Page(self.site, 'User:Legobot/properties.js')
        self.archive = pywikibot.Page(self.site, 'User:Legobot/properties.js/Archive')

    def run(self):
        jobs = self.page.get().splitlines()
        for job in jobs:
            if job.startswith('#') or not job.strip():
                continue
            self.run_job(job)
            #archive it
            archive = self.archive.get(force=True)
            archive += '*'+job+'. Finished at ~~~~~\n'
            self.archive.put(archive, 'Bot: Archiving job')
            current = self.page.get(force=True)
            current = current.replace(job, '').strip()
            self.page.put(current, 'Bot: Removing archived job')

    def run_job(self, job):
        temp = mwparser.parse(job).filter_templates()[0]
        user = unicode(temp.get(5).value)
        data = {
            'lang': unicode(temp.get(1).value),
            'cat': unicode(temp.get(2).value),
            'pid': unicode(temp.get(3).value),
            'target_qid': unicode(temp.get(4).value),
            #'user': temp.get(5).value,
        }
        #build the summary
        summary = 'Bot: Setting [[Property:{pid}|{pid}]] to [[{target_qid}]]; using [[:{lang}:{cat}]]; \
requested by [[User talk:{user}|{user}]]'.format(user=user, **data)
        data['summary'] = summary
        bot = PropBot(**data)
        bot.run()



if __name__ == "__main__":
    robot = FeedBot()
    robot.run()
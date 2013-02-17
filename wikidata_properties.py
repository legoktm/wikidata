#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import time
import datetime
import pywikibot
import mwparserfromhell as mwparser
import wikidata_create

wikidata = pywikibot.Site('wikidata','wikidata')
recursion_users = []

class Log:
    def __init__(self, row, source, lang):
        self.row = row
        self.source = source
        self.lang = lang
        self.storage = list()
        #Storage is a list of tuples:
        #(lang, Article, Successful?, comment, id)
        #Note that successful can have 3 values, True, False, None
        #True = Done
        #False = Not done/Error
        #None = Already done (no action taken)
        #QID or None

    def blacklist(self, page, reason):
        """
        Was blacklisted for whatever reason.
        """
        self.storage.append((page.site.language(), page.title(), False, reason, None))
        return False
    def done(self, page,id):
        self.storage.append((page.site.language(), page.title(), True, '',id))
        return True
    def error(self, page, reason,id):
        self.storage.append((page.site.language(), page.title(), False, reason,id))
        return False
    def already(self, page,id):
        self.storage.append((page.site.language(), page.title(), None, '',id))
        return True

    def save(self):
        basepage = 'User:Legobot/properties.js/Archive/'
        suffix = datetime.datetime.utcnow().strftime('%Y/%m/%d')
        page = pywikibot.Page(wikidata, basepage+suffix)
        header = '[[:{0}:{1}]]'.format(self.lang, self.source)
        text = self.row +'\n{{User:Legobot/Table/top}}\n'
        for row in self.storage:
            if row[4]:
                text+='{{{{User:Legobot/Table/row|wikilink={0}:{1}|done={2!s}|{3}|id={4}}}}}\n'.format(*row)
            else:
                text+='{{{{User:Legobot/Table/row|wikilink={0}:{1}|done={2!s}|{3}}}}}\n'.format(*row)
        text+='|} --~~~~'
        page.put(text, header, newsection=True)


class PropBot:
    def __init__(self, lang, source, pid, target_qid, summary, row, **kwargs):
        self.lang = lang
        self.source = source
        self.pid = pid
        self.target_qid = target_qid
        self.target = int(self.target_qid.lower().replace('q',''))
        self.summary = summary
        self.local_site = pywikibot.Site(self.lang, 'wikipedia')
        self.repo = pywikibot.Site().data_repository()
        self.wikidata = wikidata
        self.token = self.wikidata.token(pywikibot.Page(self.wikidata, 'Main Page'), 'edit')
        self.options = kwargs
        #this just needs to be global
        self.create = 'create' in self.options
        #recursion for rschen
        if 'recursion' in self.options and self.options['user'].lower() in recursion_users:
            self.recursion = int(self.options['recursion'])
        else:
            self.recursion = 0

        #set up logging
        self.logger = Log(row, source, lang)


    def run_checks(self, page):
        ##IGNORE PREFIX.
        if 'ignoreprefix' in self.options:
            if ',' in self.options['ignoreprefix']:
                ignoreprefix = self.options['ignoreprefix'].split(',')
            else:
                ignoreprefix = [self.options['ignoreprefix']]
            for prefix in ignoreprefix:
                if page.title().startswith(prefix):
                    reason = 'Blacklisted: {0}'.format(prefix)
                    return self.logger.blacklist(page, reason)
        #IGNORE.
        if 'ignore' in self.options:
            if ',' in self.options['ignore']:
                ignore = self.options['ignore'].split(',')
            else:
                ignore = [self.options['ignore']]
            for i in ignore:
                if page.title() == i.strip():
                    reason = 'Ignored: {0}'.format(i)
                    return self.logger.blacklist(page, reason)
        #redirect check
        if page.isRedirectPage():
            return self.logger.blacklist(page, 'Is a redirect page.')
        #success!
        return True


    def run(self):
        if self.source.startswith(tuple(self.local_site.namespaces()[14])):
            category = pywikibot.Category(self.local_site, self.source)
            print 'Fetching {0}'.format(category.title())
            gen = category.articles(namespaces=[0], recurse=self.recursion)
        elif self.source.startswith(tuple(self.local_site.namespaces()[10])):
            template = pywikibot.Page(self.local_site, self.source)
            gen = template.getReferences(follow_redirects=False, onlyTemplateInclusion=True, namespaces=[0])
        else:
            #bad input
            return
        for page in gen:
            #run it against our checks first
            checks = self.run_checks(page)
            if checks:
                self.do_page(page)
            else:
                print 'Skipping {0}'.format(page.title())
        self.logger.save()

    def do_page(self, page):
        #find the item
        print page
        site = self.lang + 'wiki' #haaaack
        title = page.title()
        qid = self.repo.get_id(site, title)
        print qid
        id = int(qid.lower().replace('q','')) #int-ify
        created = False
        if id == -1:
            print 'Item doesn\'t exist!'
            if not self.create:
                return self.logger.error(page, 'Page does not have a Wikidata item.',None)
            print 'Creating now...'
            try:
                qid = wikidata_create.create_item(self.lang, title, token=self.token,check=False)
                created = True
                time.sleep(2)
            except pywikibot.data.api.APIError:
                return self.logger.error(page, 'Item could not be created.',None)
        #at this point, lets make sure we're not adding a duplicate claim.
        if not created and self.check_claims(qid, page):
            #means it was already done
            return
        params = {'entity':qid,
                  'property':self.pid,
                  'snaktype':'value',
                  'value':'{{"entity-type":"item","numeric-id":{0}}}'.format(self.target),
                  'token':self.token,
                  'bot':1
        }
        try:
            result = self.repo.set_claim(**params)
        except pywikibot.data.api.APIError, e:
            self.logger.error(page, unicode(e).encode('utf-8'), qid)
            return
        print result
        time.sleep(2)
        return self.logger.done(page,qid)

    def check_claims(self, qid, page):
        claims = self.repo.get_claims(qid)
        if not self.pid.lower() in claims:
            return
        prop = claims[self.pid.lower()]
        #lets check if our specific value is there
        for claim in prop:
            if int(claim['mainsnak']['datavalue']['value']['numeric-id']) == self.target:
                return self.logger.already(page,qid)
        return


class FeedBot:
    def __init__(self):
        self.site = wikidata
        self.page = pywikibot.Page(self.site, 'User:Legobot/properties.js')

    def run(self):
        jobs = self.page.get().splitlines()
        for job in jobs:
            if job.startswith('#') or not job.strip():
                continue
            self.run_job(job)
            #remove it
            current = self.page.get(force=True)
            current = current.replace(job+'\n', '').strip()
            self.page.put(current, 'Bot: Removing archived job')

    def run_job(self, job):
        temp = mwparser.parse(job).filter_templates()[0]
        data = {
            'lang': unicode(temp.get(1).value),
            'source': unicode(temp.get(2).value),
            'pid': unicode(temp.get(3).value),
            'target_qid': unicode(temp.get(4).value),
            'row':job,
            'user':unicode(temp.get(5).value),
        }
        #build the summary
        summary = 'Bot: Setting [[Property:{pid}|{pid}]] to [[{target_qid}]]; using [[:{lang}:{source}]]; \
requested by [[User talk:{user}|{user}]]'.format(**data)
        data['summary'] = summary
        #lets build some options
        whitelist = ['ignoreprefix','create','ignore','recursion']
        for param in temp.params:
            if unicode(param.name) in whitelist:
                data[unicode(param.name)] = unicode(param.value)
        print data
        bot = PropBot(**data)
        bot.run()



if __name__ == "__main__":
    robot = FeedBot()
    robot.run()

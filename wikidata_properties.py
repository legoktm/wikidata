#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import time
import datetime
import oursql
import os
import pywikibot
import mwparserfromhell as mwparser
import wikidata_create

wikidata = pywikibot.Site('wikidata','wikidata')
recursion_users = []

pywikibot.handleArgs()

db = oursql.connect(db='u_legoktm_wikidata_properties_p',
    host="sql-s1-user.toolserver.org",
    read_default_file=os.path.expanduser("~/.my.cnf"),
    raise_on_warnings=False,
)

SOURCE_VALUES = {'en':328,
                 'sv':169514,
                 'de':48183,
                 'it':11920,
                 'no':191769,
                 'ar':199700,
                 'es':8449,
                 'pl':1551807,
                 'ca':199693,
                 'fr':8447,
                 'nl':10000,
                 'pt':11921,
                 'ru':206855,
                 'vi':200180,

           } #TODO: read from somewhere onwiki or dynamic updates

class Log:
    def __init__(self, row, source, lang, db, job_id, nolog):
        self.source = source
        self.lang = lang
        self.storage = list()
        self.row = row
        #Storage is a list of tuples:
        #(lang, Article, Successful?, comment, id)
        #Note that successful can have 3 values, True, False, None
        #True = Done
        #False = Not done/Error
        #None = Already done (no action taken)
        #QID or None
        self.conn = db
        self.cursor = self.conn.cursor()
        self.job_id = job_id
        self.nolog = nolog

    def blacklist(self, page, reason):
        """
        Was blacklisted for whatever reason.
        """
        self.insert(page.site.language(), page.title(), 0, reason, None)
        return False
    def done(self, page,id, notes=''):
        self.insert(page.site.language(), page.title(), 1, notes,id)
        return True
    def error(self, page, reason,id):
        self.insert(page.site.language(), page.title(), 0, reason,id)
        return False
    def already(self, page,id, notes=''):
        self.insert(page.site.language(), page.title(), 2, notes,id)
        return True

    def save(self):
        basepage = 'User:Legobot/properties.js/Archive/'
        suffix = datetime.datetime.utcnow().strftime('%Y/%m/%d')
        page = pywikibot.Page(wikidata, basepage+suffix)
        code = mwparser.parse(self.row)
        if not self.nolog:
            code.filter_templates()[0].add('id',str(self.job_id))
        page.text = '\n' + unicode(code)
        wikidata.editpage(page, 'Bot: Archiving request', append=True)

    def deqify(self, id):
        #de-q-ify
        if id:
            return int(id.lower().replace('q',''))

    def insert(self, lang, page, success, notes, id):
        if self.nolog:
            return
        data = (None, lang, success, page, notes, None, self.deqify(id), self.job_id)
        try:
            self.cursor.execute('INSERT INTO `edits` VALUES (?,?,?,?,?,?,?,?)', data)
        except UnicodeDecodeError:
            pass #TODO FIXME
            #data = (None, lang, success, page.decode('utf-8'), notes, None, self.deqify(id), self.job_id)
            #self.cursor.execute('INSERT INTO `edits` VALUES (?,?,?,?,?,?,?,?)', data)



class PropBot:
    def __init__(self, lang, source, pid, target_qid, summary, row, job_id, db, **kwargs):
        self.lang = lang
        self.source = source
        self.pid = pid
        self.target_qid = target_qid
        #self.target =
        self.summary = summary
        self.local_site = pywikibot.Site(self.lang, 'wikipedia')
        self.repo = pywikibot.Site('en','wikipedia').data_repository()
        self.wikidata = wikidata
        self.token = self.wikidata.token(pywikibot.Page(self.wikidata, 'Main Page'), 'edit')
        self.db = db
        self.job_id = job_id
        self.options = kwargs
        self.nolog = 'nolog' in kwargs
        #this just needs to be global
        self.create = 'create' in self.options
        #recursion for rschen
        if 'recursion' in self.options and self.options['user'].lower() in recursion_users:
            self.recursion = int(self.options['recursion'])
        else:
            self.recursion = 0
        #build a dict of props to add
        self.add = dict()
        self.add[pid.lower()] = target_qid
        for key in kwargs:
            if key.startswith(('pid')):
                self.add[kwargs[key].lower()] = kwargs['qid'+key[-1:]] #super haxor
        print 'here'
        for x in self.add:
            print "{}: {}".format(x, self.add[x])


        #set up logging
        self.logger = Log(row, source, lang, db, job_id, self.nolog)


    def deqify(self, i):
        return int(i.lower().replace('q',''))

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
            try:
                print 'Fetching {0}'.format(category.title().encode('utf-8'))
            except UnicodeDecodeError:
                pass
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
                pass
                #print 'Skipping {0}'.format(page.title())
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
                #time.sleep(20)
            except pywikibot.data.api.APIError:
                return self.logger.error(page, 'Item could not be created.',None)
        #at this point, lets make sure we're not adding a duplicate claim.
        if not created:
            already_done, add_these = self.check_claims(qid, page)
            if already_done:
                return
        else:
            add_these = self.add.keys()
        if created:
            notes = 'created by bot'
        else:
            notes = ''
        for pid in add_these:
            params = {'entity':qid,
                      'property':pid,
                      'snaktype':'value',
                      'value':'{{"entity-type":"item","numeric-id":{0}}}'.format(self.deqify(self.add[pid])),
                      'token':self.token,
                      'bot':1,
                      'summary':self.summary,
            }
            try:
                result = self.repo.set_claim(**params)
                if self.lang in SOURCE_VALUES:
                    value = SOURCE_VALUES[self.lang]
                    s_params = {'statement':result['claim']['id'],
                                'token':self.token,
                                'bot':1,
                                'snaks':'{"p143":[{"snaktype":"value","property":"p143","datavalue":{"type":"wikibase-entityid","value":{"entity-type":"item","numeric-id":'+str(value)+'}}}]}'
                    }
                    res2 = self.repo.set_reference(**s_params)
                    print res2
                print result
            except pywikibot.data.api.APIError, e:
                self.logger.error(page, unicode(e).encode('utf-8'), qid)
                continue

        #time.sleep(20)
        return self.logger.done(page,qid,notes=notes)


    def check_claims(self, qid, page):
        claims = self.repo.get_claims(qid)
        add_these = list()
        for key in self.add:
            if not key in claims:
                add_these.append(key)
                continue
            prop = claims[key]
            added=False
            for claim in prop:
                if int(claim['mainsnak']['datavalue']['value']['numeric-id']) == self.deqify(self.add[key]):
                    added=True
                    break
            if not added:
                add_these.append(key)

        if not add_these:
            return True,self.logger.already(page,qid)
        return False,add_these


class FeedBot:
    def __init__(self, db):
        self.site = wikidata
        self.page = pywikibot.Page(self.site, 'User:Legobot/properties.js')
        self.db = db

    def run(self):
        jobs = self.page.get().splitlines()
        for job in jobs:
            if job.startswith('#') or not job.strip():
                continue
            done = self.run_job(job)
            #remove it
            if done:
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
        whitelist = ('ignoreprefix','create','ignore','recursion','pid','qid','nolog')
        for param in temp.params:
            if unicode(param.name).startswith(whitelist):
                data[unicode(param.name)] = unicode(param.value)
        print data
        #check to make sure this job shouldnt be done on labs.
        if 'db' in data:
            return False
        job_id = self.insert(data) #load into the db
        data['job_id'] = job_id
        data['db'] = self.db
        bot = PropBot(**data)
        bot.run()
        self.mark_done(job_id)
        return True

    def insert(self, data):
        # lang  source  pid  target_qid  row  user None done None, pid2, qid2, pid3, qid3, pid4, qid4, pid5, qid5
        d = (None, #None aka id
             data['lang'], #lang
             data['source'], #source
             data['pid'], #pid
             data['target_qid'], #target_qid
             data['row'], #row
             data['user'], #user
             None, #None aka timestamp
             0, #done
             data.get('pid2',None),
             data.get('qid2',None),
             data.get('pid3',None),
             data.get('qid3',None),
             data.get('pid4',None),
             data.get('qid4',None),
             data.get('pid5',None),
             data.get('qid5',None),
        )
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO `jobs` VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', d)
        #get the id
        cursor.execute('SELECT MAX(id) FROM jobs')
        return cursor.fetchone()[0]

    def mark_done(self, job_id):
        cursor = self.db.cursor()
        cursor.execute('UPDATE jobs SET done=1 WHERE id=?', (job_id,))




if __name__ == "__main__":
    robot = FeedBot(db)
    robot.run()

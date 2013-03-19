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

#autotranslatable summaries

editsummary = {
    "el":"[[User:Addbot|Ρομπότ:]] Μεταφέρω $counter σύνδεσμους interwiki, που τώρα παρέχονται από τα [[Wikipedia:Wikidata|Wikidata]] στο [[d:$id]]",
    "eo":"[[Uzanto:Addbot|Roboto:]] Forigo de $counter interlingvaj ligiloj, kiuj nun disponeblas per [[d:|Vikidatumoj]] ([[d:$id]])",
    "en":"Bot: Migrating $counter langlinks, now provided by [[Wikipedia:Wikidata|Wikidata]] on [[d:$id]]",
    "zh":"机器人：移除",
    "szl":"[[Używacz:Addbot|Addbot]] przećepoł $counter linkůw interwiki, terozki bydům ůune na [[d:|Wikidata]]",
    "af":"Verplasing van $counter interwikiskakels wat op [[d:|Wikidata]] beskikbaar is op [[d:$id]]",
    "bat_smg":"Perkeliamas $counter tarpkalbėnės nūruodas, daba esontės [[d:|Wikidata]] poslapī [[d:$id]].",
    "vi":"Bot: Di chuyển $counter liên kết ngôn ngữ đến [[d:|Wikidata]] tại [[d:$id]] [[M:User:Addbot/WDS|Addbot]]",
    "ca":"Bot: Traient $counter enllaços interwiki, ara proporcionats per [[d:|Wikidata]] a [[d:$id]]",
    "am":"[[User:Addbot|ሎሌ፦]] መያያዣዎች ወደ $counter ልሳናት አሁን በ[[Wikipedia:Wikidata|Wikidata]] ገጽ [[d:$id]] ስላሉ ተዛውረዋል።",
    "it":"migrazione automatica di $counter collegamenti interwiki a [[d:Wikidata:Pagina_principale|Wikidata]], [[d:$id]]",
    "eu":"[[User:Addbot|Robota:]] hizkuntza arteko $counter lotura lekualdatzen; aurrerantzean [[Wikipedia:Wikidata|Wikidata]] webgunean izango dira, [[d:$id]] orrian",
    "ar":"[[مستخدم:Addbot|بوت:]] ترحيل $counter وصلة إنترويكي, موجودة الآن في [[d:|ويكي بيانات]] على [[d:$id]]",
    "cs":"[[Wikipedista:Addbot|Bot:]] Odstranění $counter [[Wikipedie:Wikidata#Mezijazykové odkazy|odkazů interwiki]], které jsou nyní dostupné na [[d:|Wikidatech]] ([[d:$id]])",
    "et":"[[User:Addbot|Robot]]: muudetud $counter intervikilinki, mis on nüüd andmekogus [[d:$id|Wikidata]]",
    "gl":"[[Usuario:Addbot|Bot:]] Retiro $counter ligazóns interlingüísticas, proporcionadas agora polo [[d:|Wikidata]] en [[d:$id]]",
    "tet":"Bot: Hasai $counter ligasaun interwiki, ne'ebé agora mai husi [[d:$id]] iha [[d:|Wikidata]] ",
    "id":"[[Pengguna:Addbot|Bot:]] Migrasi $counter pranala interwiki, karena telah disediakan oleh [[Wikipedia:Wikidata|Wikidata]] pada item [[d:$id]]",
    "es":"Moviendo $counter enlaces interlingúisticos, ahora proporcionado(s) por [[d:|Wikidata]] en la página [[d:$id]].",
    "ru":"Перемещение $counter интервики на [[Wikipedia:Wikidata|Викиданные]], [[d:$id]]",
    "sr":"[[User:Addbot|Бот:]] Селим $counter међујезичких веза, које су сад на [[Википедија:Википодаци|Википодацима]] на [[d:$id]]",
    "lb":"Bot: Huet $counter Interwikilinke geréckelt, déi elo op [[d:|Wikidata]] op [[d:$id]] zur Verfügung gestallt ginn",
    "pt":"A migrar $counter interwikis, agora providenciados por [[Wikipedia:Wikidata|Wikidata]] em [[d:$id]]",
    "la":"[[Usor:Addbot|Addbot]] $counter nexus intervici removet, quod nunc apud [[d:|Vicidata]] cum tessera [[d:$id]] sunt",
    "tt":"[[User:Addbot|Бот:]] бу мәкаләнең [[Википедия:Интервики|интервики]] сылтамалары ($counter) хәзер [[d:$id|Wikidata-да]]",
    "frr":"[[User:Addbot|Bot:]] Fersküüw $counter interwiki-links, diar nü uun [[d:|Wikidata]] üüb det sidj [[d:$id]] paroot stun",
    "lt":"Perkeliamos $counter tarpkalbinės nuorodos, dabar pasiekiamos [[d:|Wikidata]] puslapyje [[d:$id]].",
    "sh":"[[Korisnik:Addbot|Bot:]] migracija $counter međuwiki veza sada dostupnih na stranici [[d:$id]] na [[d:|Wikidati]]",
    "vec":"[[Utente:Addbot|Bot]]: Migrasion de $counter interwiki links so [[d:Wikidata:Pagina_principale|Wikidata]] - [[d:$id]]",
    "_default":"[[M:User:Addbot|Bot:]] Migrating $counter interwiki links, now provided by [[d:|Wikidata]] on [[d:$id]] [[M:User:Addbot/WDS|(translate me)]]",
    "ro":"Migrare a $counter legături interwiki, furnizate acum de [[Wikipedia:Wikidata|Wikidata]] la [[d:$id]]",
    "ia":"[[Usator:Addbot|Robot:]] Migration de $counter ligamines interwiki, fornite ora per [[Wikipedia:Wikidata|Wikidatos]] in [[d:$id]]",
    "is":"Bot: Flyt $counter tungumálatengla, sem eru núna sóttir frá [[d:|Wikidata]] á [[d:$id]]",
    "nv":"wikidata bitsʼą́ą́dę́ę́ʼígíí chodaoʼį́ kʼad ([[d:$id]]; $counter wikidata bitsʼą́ą́dę́ę́ʼ)",
    "ta":"[[User:Addbot|தானியங்கி:]] $counter விக்கியிடை இணைப்புகள் நகர்த்தப்படுகின்றன, தற்போது [[Wikipedia:Wikidata|விக்கிதரவில்]] இங்கு [[d:$id]]",
    "be":"[[User:Addbot|Робат]] перанёс $counter міжмоўных спасылак да аб'екта [[d:$id]] на [[:en:Wikipedia:Wikidata|Wikidata]]",
    "fr":"Suis retirer $counter liens entre les wikis, actuellement fournis par [[d:|Wikidata]] sur la page [[d:$id]]",
    "bg":"[[Потребител:Addbot|Робот]]: Преместване на $counter междуезикови препратки към [[:en:Wikipedia:Wikidata|Уикиданни]], в [[d:$id]].",
    "ms":"[[Pengguna:Addbot|Bot:]] Memindahkan $counter pautan interwiki, kini disediakan oleh [[Wikipedia:Wikidata|Wikidata]] di [[d:$id]]",
    "sl":"Bot: Migracija $counter interwikija/-ev, od zdaj gostuje(-jo) na [[d:|Wikipodatkih]], na [[d:$id]]",
    "mr":"[[सदस्य:Addbot|सांगकाम्या:]] $counter इतर भाषातील दुव्यांचे विलिनीकरण, आता [[d:WD:I|विकिडेटा]]वर उपलब्ध [[d:$id]]",
    "bn":"[[ব্যবহারকারী:Addbot|বট]]: $counter টি আন্তঃউইকি সংযোগ সরিয়ে নেওয়া হয়েছে, যা এখন [[d:|উইকিউপাত্তের]] - [[d:$id]] এ রয়েছে",
    "de":"$counter [[Hilfe:Internationalisierung|Interwiki-Link(s)]] nach [[WP:Wikidata|Wikidata]] ([[d:$id]]) migriert",
    "mg":"Nanala rohy interwiki $counter izay efa omen'i [[:mg:w:Wikipedia:Wikidata|Wikidata]] eo amin'i [[d:$id]]",
    "da":"Bot: Migrerer $counter interwikilinks, som nu leveres af [[d:|Wikidata]] på [[d:$id]]",
    "fa":"[[کاربر:Addbot|ربات:]] انتقال $counter پیوند میانویکی به [[d:$id]] در [[ویکیپدیا:ویکیداده|ویکیداده]]",
    "uz":"[[Foydalanuvchi:Addbot|Bot:]] endilikda [[d:Wikidata:Ana_Sayfa|Wikidata]] [[d:$id]] sahifasida saqlanadigan $counter intervikini koʻchirdi",
    "no":"bot: Fjerner $counter interwikilenker som nå hentes fra [[d:$id]] på [[d:|Wikidata]]",
    "bs":"[[Korisnik:Addbot|Bot:]] premještanje $counter međuwiki linkova koji su sada dostupni na stranici [[d:$id]] na [[d:|Wikidati]]",
    "fi":"[[Käyttäjä:Addbot|Botti]] poisti $counter [[Wikipedia:Wikidata|Wikidatan]] sivulle [[d:$id]] siirrettyä kielilinkkiä",
    "hu":"Bot: $counter interwiki link áthelyezve a [[d:|Wikidata]] [[d:$id]] adatába",
    "ja":"[[User:Addbot|ボット]]: 言語間リンク $counter 件を[[Wikipedia:ウィキデータ|ウィキデータ]]上の [[d:$id]] に転記",
    "he":"בוט: מעביר קישורי בינויקי ל[[ויקיפדיה:ויקינתונים|ויקינתונים]] - [[d:$id]]",
    "ka":"[[User:Addbot|Bot:]] $counter [[ვპ:ებ|ენათაშორისი ბმული]] გადატანილია [[Wikipedia:Wikidata|Wikidata]]-ზე, [[d:$id]]",
    "be_x_old":"[[User:Addbot|Робат]]: перанос $counter міжмоўных спасылак у [[Вікіпэдыя:Вікізьвесткі|Вікізьвесткі]] да аб’екта [[d:$id]]",
    "ckb":"[[بەکارھێنەر:Addbot|بۆت:]] گواستنەوەی $counter بەستەری نێوانویکی، ئێستا دابین کراوە لەسەر [[d:| ویکیدراوە]] لە [[d:$id]]",
    "ilo":"[[Agar-aramat:Addbot|Bot:]] Agiyal-alis kadagiti $counter nga interwiki, a nait-iteden idiay [[Wikipedia:Wikidata|Wikidata]] iti [[d:$id]]",
    "be_tarask":"[[User:Addbot|Робат]]: перанос $counter міжмоўных спасылак у [[Вікіпэдыя:Вікізьвесткі|Вікізьвесткі]] да аб’екта [[d:$id]]",
    "ko":"[[User:Addbot|봇:]] 인터위키 링크 $counter 개가 [[백:위키데이터|위키데이터]]의 [[d:$id]] 항목으로 옮겨짐",
    "sv":"Bot överför $counter interwikilänk(ar), som nu återfinns på sidan [[d:$id]] på [[d:|Wikidata]]",
    "ur":"[[صارف:Addbot|روبالہ:]] منتقلی $counter بین الویکی روابط، اب [[d:|ویکی ڈیٹا]] میں [[d:$id]] پر موجود ہیں",
    "sk":"[[Redaktor:Addbot|Bot:]] Odstránenie $counter odkazov interwiki, ktoré sú teraz dostupné na [[d:|Wikiúdajoch]] ([[d:$id]])",
    "pl":"[[User:Addbot|Bot:]] Przenoszę linki interwiki ($counter) do [[d:|Wikidata]], są teraz dostępne do edycji na [[d:$id]]",
    "min":"[[Pengguna:Addbot|Bot:]] Migrasi $counter pautan interwiki, dek lah disadioan jo [[Wikipedia:Wikidata|Wikidata]] pado [[d:$id]]",
    "ku":"Bot: $counter girêdanên înterwîkiyê ên ku niha li ser [[:d|Wikidata]]yê ne, jê bibe",
    "ml":"$counter ഇന്റര്വിക്കി കണ്ണികളെ [[Wikipedia:Wikidata|വിക്കിഡാറ്റയിലെ]] [[d:$id]] എന്ന താളിലേക്ക്  മാറ്റിപ്പാര്പ്പിച്ചിരിക്കുന്നു. ",
    "nl":"[[Gebruiker:Addbot|Robot:]] Verplaatsing van $counter interwikilinks. Deze staan nu op [[d:|Wikidata]] onder [[d:$id]]",
    "os":"Бот схафта $counter æвзагы æрвитæны, кæцытæ [[Википеди:Викирардтæ|Викирардты]] нырид сты ацы фарсы: [[d:$id]]",
}
if '--labs' in sys.argv:
    DUMP = '/public/datasets/public/{0}/'.format(wiki)
    dates = [int(x) for x in os.listdir(DUMP)]
    date = str(max(dates))
    DUMP += '{0}/{1}-{0}-pages-articles.xml.bz2'.format(date, wiki)
else:
    PATH = '/home/legoktm/public_html/import/'
    PROGRESS = PATH + '{0}_progress.txt'.format(g_lang)
    DUMP = '/mnt/user-store/dumps/{0}-latest-pages-articles.xml'.format(wiki)

py_enwp = pywikibot.Site(g_lang.replace('_','-'),'wikipedia')
enwp = mw.Wiki('http://{0}.wikipedia.org/w/api.php'.format(g_lang.replace('_','-')))
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
        print object['title']
        reason = reason.replace('\n',' ') #should really fix the "xxwiki" syntax. Oh well
        if id:
            text = u'\n*[[:{0}]] ([[d:{1}]] - [{3}{1} check]) - {2}'.format(object['title'], id, reason, checktool)
        else:
            text = u'\n*[[:{0}]] - {2}'.format(object['title'], id, reason)
        page.text= text
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
        if len(storage) != 0:
            for p in self.check(storage):
                yield p


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
            values[str(pg.id)] = {'revid':pg.revisionid, 'content':pg.text,'title':pg.title,'id':pg.id}
        req = self.api.request(params)
        need_update = list()
        pages = req['query']['pages']
        for pageid in pages:
            if 'missing' in pages[pageid]:
                del values[str(pageid)]  # deleted
                continue
            elif 'redirect' in pages[pageid]:
                del values[str(pageid)]  # is a redirect now
                continue
            if not 'revisions' in pages[pageid]:
                del values[str(pageid)]  # deleted i guess
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
            if (not page.ns in (2, 6, 8)) and (page.ns % 2 == 0) and not page.isredirect:
                yield page

class WikidataBot:
    def __init__(self):
        self.enwp = py_enwp
        self.repo = self.enwp.data_repository()
        self.token = self.repo.token(pywikibot.Page(self.repo, 'Main Page'), 'edit')
        self.enwp_token = self.enwp.token(pywikibot.Page(self.enwp, 'User:Legoktm'), 'edit')
        self.logger = Log()
        self.override = False
        self.trial = 0
        self.trial_on = '--trial' in sys.argv
        self.showerrors = '--errors' in sys.argv

    def process(self, object):
        #object = {'revid', 'content', 'title','id'}
        if 'noexternallanglinks' in object['content'].lower():
            print 'noextlanglinks'
            return
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
            return #self.logger.error(object, 'Item does not exist.',None)
        #if we just created, that means the links are exact.
        #if created:
        #    self.remove_links(object, qid)
        if self.override:
            self.remove_links(object, qid,'??')
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
                print 'dont match'
                errors.append(lang)


        for langwiki in to_add:
            try:
                data = add_link(qid, langwiki.replace('-','_'), to_add[langwiki], showerror=True,source=g_lang)
            except pywikibot.data.api.APIError, e:
                return self.logger.error(object, unicode(e).encode('utf-8'), qid)
            except TypeError:
                #weird pywikibot error
                return self.logger.error(object, 'Error while adding [[:{0}:{1}]] to wikidata.'.format(langwiki.replace('wiki',''), to_add[langwiki]),qid)
            if not 'success' in data:
                return self.logger.error(object, 'Error while adding [[:{0}:{1}]] to wikidata.'.format(langwiki.replace('wiki',''), to_add[langwiki]),qid)
            else:
                print 'Added '+ langwiki
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
            self.remove_links(object, qid, len(locallanglinks))
        except pywikibot.data.api.TimeoutError:
            print 'timeout error'
            pass  # it probably went through anyways
        self.trial += 1
        if self.trial_on:
            time.sleep(3)
            if self.trial >= 50:
                print 'trial over.'
                quit()


    def translate(self, msg):
        if g_lang in msg:
            return msg[g_lang].decode('utf-8')
        else:
            return msg['_default'].decode('utf-8')

    def remove_links(self, object, qid, count):
        newtext = textlib.removeLanguageLinks(object['content'], self.enwp)
        #need to build a page object
        page = pywikibot.Page(self.enwp, object['title'])
        page.text = newtext
        summary = self.translate(editsummary).replace('$id', qid).replace('$counter', str(count))
        try:
            self.enwp.editpage(
                page,
                summary,
                nocreate=True,
                lastrev=int(object['revid']),
                token=self.enwp_token,
                skipec=True,
                useid=object['id']
            )
            return
        except pywikibot.exceptions.LockedPage:
            print 'protected'
            return self.logger.error(object, 'Page was protected.',qid)
        except pywikibot.exceptions.EditConflict:
            print 'edit conflict'
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
            if self.showerrors:
                self.process(object)
            else:
                try:
                    self.process(object)
                #except UnicodeDecodeError:
                #    print 'decode error'
                #    pass
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    #just suppress errors for now, we can fix them later
                    print 'uhohs error'
                    pass


if __name__ == "__main__":
    print 'Operating on '+wiki
    pywikibot.handleArgs()
    bot = WikidataBot()
    bot.run()
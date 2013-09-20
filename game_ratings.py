#!/usr/bin/python
from __future__ import unicode_literals

import mwparserfromhell
import pywikibot
from pywikibot import pagegenerators
import wdapi

dewiki = pywikibot.Site('de', 'wikipedia')
repo = dewiki.data_repository()

USK = {
    0: 'Q14920387',
    6: 'Q14920391',
    12: 'Q14920392',
    16: 'Q14920393',
    18: 'Q14920394',
}
USK_PROP = pywikibot.PropertyPage(repo, 'P914')

PEGI = {
    3: 'Q14915512',
    7: 'Q14915514',
    12: 'Q14915515',
    16: 'Q14915516',
    18: 'Q14915517',
}
PEGI_PROP = pywikibot.PropertyPage(repo, 'P908')

REF = pywikibot.Claim(repo, 'P143')
REF.setTarget(pywikibot.ItemPage(repo, 'Q48183'))

temp = pywikibot.Page(dewiki, 'Vorlage:Infobox Computer- und Videospiel')
gen = pagegenerators.ReferringPageGenerator(temp, onlyTemplateInclusion=True, content=True)


def normalize_pegi(thingy):
    # BECAUSE PEOPLE DO WEIRD THINGS!
    thingy = pywikibot.removeDisabledParts(thingy)
    thingy = thingy.replace('+', '')
    thingy = thingy.strip()
    if thingy.isdigit():
        if int(thingy) in PEGI:
            item = pywikibot.ItemPage(repo, PEGI[int(thingy)])
            return item


def normalize_usk(thingy):
    thingy = pywikibot.removeDisabledParts(thingy)
    thingy = thingy.strip()
    if thingy.isdigit():
        if int(thingy) in USK:
            item = pywikibot.ItemPage(repo, USK[int(thingy)])
            return item


def do_page(page):
    pywikibot.output(page)
    text = page.get()
    claims = []
    code = mwparserfromhell.parse(text)
    found = 0
    for t in code.filter_templates():
        if t.name.matches('Infobox Computer- und Videospiel'):
            found += 1
            for pname in ['PEGI', 'PEGI1', 'PEGI2', 'PEGI3']:
                if t.has_param(pname):
                    val = unicode(t.get(pname).value)
                    item = normalize_pegi(val)
                    if not item:
                        continue
                    claim = pywikibot.Claim(repo, PEGI_PROP.getID())
                    claim.setTarget(item)
                    claims.append(claim)
                else:
                    print 'no ' + pname
            for pname in ['USK']:
                if t.has_param(pname):
                    val = unicode(t.get(pname).value)
                    item = normalize_usk(val)
                    if not item:
                        continue
                    claim = pywikibot.Claim(repo, USK_PROP.getID())
                    claim.setTarget(item)
                    claims.append(claim)
                else:
                    print 'no ' + pname

    if found > 1:
        pywikibot.output('COMPLAINT: {0}'.format(page.title(asLink=True, forceInterwiki=True)))
        return
    item = pywikibot.ItemPage.fromPage(page)
    for claim in claims:
        print claim
        can, reason = wdapi.canClaimBeAdded(item, claim)
        if can:
            pywikibot.output('Adding claim: {0} --> {1}'.format(claim.getID(), claim.getTarget().getID()))
            item.addClaim(claim)
            claim.addSource(REF)
        else:
            print 'couldnt be added'
            print reason

if __name__ == '__main__':
    for page in gen:
        do_page(page)

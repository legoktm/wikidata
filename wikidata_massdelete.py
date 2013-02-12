#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import time
try:
    import wikipedia as pywikibot
except ImportError:
    import pywikibot
import mwparserfromhell as mwparser



def main():
    wikidata = pywikibot.getSite('wikidata','wikidata')
    page = pywikibot.Page(wikidata, 'User:Legobot/Dupes')
    text = page.get()
    code = mwparser.parse(text)
    templates = code.filter_templates()
    for template in templates:
        if template.name != 'rfd links':
            continue
        qid = str(template.get(1).value)
        reason = str(template.get(2).value)
        print 'Will delete {0} because: {1}'.format(qid, reason)
        page = pywikibot.Page(wikidata, qid)
        if not page.exists():
            print 'Uhoh, someone already deleted it!'
            continue
        page.delete(reason, prompt=False)
        print 'Destroyed. Will sleep a bit.'
        time.sleep(10)

if __name__ == "__main__":
    main()

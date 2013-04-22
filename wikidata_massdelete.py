#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
import sys
import re
link = re.compile('\[\[(.*?)\]\]')
import pywikibot
from pywikibot import config
config.put_throttle = 0
import mwparserfromhell as mwparser





def main():
    skip=None
    skipped=False
    for arg in pywikibot.handleArgs():
        if arg.startswith('--skip'):
            skip = arg.split('=',1)[1]
    wikidata = pywikibot.getSite('wikidata','wikidata')
    page = pywikibot.Page(wikidata, 'User:Legobot/Dupes')
    text = page.get()
    code = mwparser.parse(text)
    templates = code.filter_templates()
    for template in templates:
        if template.name != 'rfd links':
            continue
        qid = str(template.get(1).value)
        if skip and not skipped:
            if qid==skip:
                skipped=True
            else:
                continue
        reason = str(template.get(2).value)
        if not ('exact' in reason.lower() or 'duplicate' in reason.lower()):
            print 'Not an exact dupe, skipping'
            continue
        dupe = link.search(reason)
        if not dupe:
            print 'Error: Cannot parse the deletion reason, skipping.'
            continue
        other = pywikibot.Page(wikidata, dupe.group(1))
        if not other.exists():
            print 'Uhoh, the other copy doesn\'t exist. Won\'t delete.'
            continue
        print 'Will delete {0} because: {1}'.format(qid, reason)
        page = pywikibot.Page(wikidata, qid)
        if not page.exists():
            print 'Uhoh, someone already deleted it!'
            continue
        page.delete(reason, prompt=False)
        print 'Destroyed. Will sleep a bit.'
        #time.sleep(10) - let pywikibot throttle handle it

if __name__ == "__main__":
    main()

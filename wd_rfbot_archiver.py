#!/usr/bin/env python
from __future__ import unicode_literals
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
import datetime
import pywikibot
import mwparserfromhell

site = pywikibot.Site('wikidata', 'wikidata')

#figure out the current archive
today = datetime.datetime.today()
archive = pywikibot.Page(site, today.strftime('Wikidata:Requests for permissions/RfBot/%B %Y'))
if not archive.exists():
    text = today.strftime("""{{DEFAULTSORT:*Bot %Y %m}}
{{archive|category=Archived requests for permissions}}
= Successful requests =

= Unsuccessful requests =""")
    archive.put(text, 'Bot: Creating new monthly archive.')


pg = pywikibot.Page(site, 'Wikidata:Requests for permissions/Bot')
text = pg.get()
rm_these = list()
code = mwparserfromhell.parse(text)
for temp in code.filter_templates():
    if temp.name.startswith('Wikidata:Requests for permissions/Bot/') and not '/Header/' in temp.name:
        subpage = pywikibot.Page(site, str(temp.name))
        if '{{approved}}' in subpage.get().lower():
            rm_these.append(subpage.title())
print(rm_these)

#ok lets now add them to the archive list
old = archive.get()
nt = ''
for ap in rm_these:
    nt += '* [[{0}]]\n'.format(ap)

newtext = old.replace('\n= Unsuccessful requests =', nt + '\n= Unsuccessful requests =')
archive.put(newtext, 'Bot: Archiving approved requests from [[Wikidata:Requests for permissions/Bot]]')

#ok lets remove them...

oldold = pg.get() + '\n'  # the trailing newline will get chopped by mediawiki anyways

for ap in rm_these:
    oldold = oldold.replace('{{'+ap+'}}\n', '')
pg.put(oldold, 'Bot: Removing approved requests archived to [[{0}]]'.format(archive.title()))

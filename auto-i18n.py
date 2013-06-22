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
import json
import re
import pywikibot

regex = re.compile('case \"(?P<lang>.*?)\":\s*?\$summary =\s*?"(?P<summary>.*?)"')

meta = pywikibot.Site('meta','meta')
page = pywikibot.Page(meta, 'User:Addbot/Wikidata Summary')
text = page.get()

data = {
    'en':'Bot: Migrating $counter langlinks, now provided by [[Wikipedia:Wikidata|Wikidata]] on [[d:$id]]',
    'fr':'Suis retirer $counter liens entre les wikis, actuellement fournis par [[d:|Wikidata]] sur la page [[d:$id]]',
    '_default':'[[M:User:Addbot|Bot:]] Migrating $counter interwiki links, now provided by [[d:|Wikidata]] on [[d:$id]] [[M:User:Addbot/WDS|(translate me)]]',
}
start = False
lines = text.splitlines()
for line in lines:
    if line.strip() == '<pre>':
        start = True
        continue
    if not start:
        continue
    if not 'summary' in line or not 'case' in line:
        continue
    match = regex.match(line)
    if not match:
        print line
        quit()
    lang = match.group('lang')
    sum = match.group('summary')
    if not sum.strip():
        continue
    data[lang] = sum
#    print (lang, sum)
for key in data:
    print '\t"{0}":"{1}",'.format(key, data[key].encode('utf-8'))

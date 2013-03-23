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
import pywikibot
import re
pywikibot.handleArgs()
site = pywikibot.Site('wikidata','wikidata')
regex = re.compile('== \[\[(?P<qid>Q\d*?)\]\] ==(?P<text>.*?)(?===)', flags=re.DOTALL)
page = pywikibot.Page(site, 'Wikidata:Requests for deletions')
text = oldtext = page.get()
x = list(regex.finditer(text))
for m in x:
    q = pywikibot.Page(site, m.group('qid'))
    print q
    if (not 'done}}' in m.group('text').lower()) and (not q.exists()):
        print 'should be marked as done'
        t = m.group()
        t+=':{{done}} ~~~~\n'
        text = text.replace(m.group(), t)
pywikibot.showDiff(oldtext, text)
page.put(text, 'marking requests as done')
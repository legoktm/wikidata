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

Script to parse RfD into a machine readable format.
"""

import mwparserfromhell
import pywikibot
import simplejson

repo = pywikibot.Site('wikidata', 'wikidata').data_repository()

rfd = pywikibot.Page(repo, u'Wikidata:Requests for deletions')


def parse():
    text = rfd.get()
    code = mwparserfromhell.parse(text)
    requests = []
    section = code.get_sections()[2]
    for section in code.get_sections()[1:]:

    #print section
    #print type(section)
        data = {'section': section}
        header = unicode(section.filter_headings()[0])
        data['header'] = header
        text = mwparserfromhell.parse(unicode(section).replace(header +'\n', ''))
        data['text'] = text
        print text
        item = None
        for template in text.filter_templates():
            if unicode(template.name).startswith('Rfd group'):
                data['type'] = 'bulk'
                break
            elif template.name == 'rfd links':
                data['type'] = 'single'
                item = template.get(1).value
                break
        if item:
            item = pywikibot.ItemPage(repo, item)
        data['item'] = item
        requests.append(data)
    return requests


if __name__ == '__main__':
    print parse()

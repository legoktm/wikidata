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

Script to comment on RfD requests.
"""

import parser
import pywikibot
ORIGINAL_TEXT = parser.rfd.get()

stuff = parser.parse()


def comment(cmts, data):
    if not cmts:
        return
    if not hasattr(cmts, '__iter__'):
        cmts = [cmts]
    t = '\n'
    if len(cmts) == 1:
        t += ':{0} ~~~~\n'.format(cmts[0])
    else:
        for cmt in cmts:
            t += ':* {0}\n'.format(cmt)
        t += ':~~~~\n'
    section = unicode(data['section']).strip()
    section += t
    text = parser.rfd.text
    newtext = text.replace(unicode(data['section']), section)
    parser.rfd.text = newtext
    if hasattr(parser.rfd, 'counter'):
        parser.rfd.counter += 1
    else:
        parser.rfd.counter = 1
    if parser.rfd.counter >= 5:
        finish()
        parser.rfd.get()



def main():
    for req in stuff:
        cmts = []
        checked = []
        safe = True
        if '[[User:Legobot|Legobot]]' in unicode(req['text']):
            #we already commented!
            continue
        if req['type'] == 'bulk':
            continue
        if req['item']:
            item = req['item']
            if not item.exists():
                continue
            if item.sitelinks:
                safe = False
                cmts.append('Warning: item still has {0} sitelinks.'.format(len(item.sitelinks)))
            else:
                checked.append('sitelinks')
                cmts.append('Bot comment: Item has no remaining sitelinks.')
            incoming = list(item.getReferences(namespaces=[0], total=1))
            link = '{{{{il|{0}}}}}'.format(item.getID())
            if incoming:
                safe = False
                cmts.append('Warning: item still has ' + link)
            else:
                checked.append(link)
                cmts.append('Bot comment: item has no ' + link)
        if safe:
            comment('Bot comment: Looks good to me. (Checked {0}).'.format(', '.join(checked)), req)
        else:
            comment(cmts, req)


def finish():
    if not hasattr(parser.rfd, 'counter'):
        #We never touched anything, oh well.
        return
    pywikibot.showDiff(ORIGINAL_TEXT, parser.rfd.text)
    try:
        parser.rfd.save(u'Bot: Commenting on {0} request(s).'.format(parser.rfd.counter))
    except pywikibot.exceptions.PageNotSaved:
        pass
    parser.rfd.counter = 0


if __name__ == "__main__":
    main()
    finish()

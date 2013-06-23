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
print "Content-type: text/html\n\n"
import cgitb; cgitb.enable()
import cgi
import sys
import os
os.environ['PYWIKIBOT2_DIR'] = '/home/legoktm/rewrite/'
import pywikibot
from pywikibot import textlib
import bootstrap
sys.path.append('/home/legoktm/wikidata')
import enwiki_removal




#the form page
form = """
      <form class="form-signin" action="/~legoktm/cgi-bin/wikidata/checker.py" method="get">
        <h2 class="form-signin-heading">Please enter an id.</h2>
        <input type="text" class="input-block-level" name="id" placeholder="Q##">
        <input type="text" class="input-block-level" name="site" placeholder="en">
        <button class="btn btn-large btn-primary" type="submit">Check</button>
      </form>
"""


def union(a, b):
    return list(set(a) | set(b))

def main():
    stuff = cgi.FieldStorage()
    try:
        qid = stuff['id'].value.lower()
    except KeyError:
        print bootstrap.main(tool='checker.py', stuff=form, title='checker.py')
        return
    try:
        site_lang = stuff['site'].value.lower()
    except KeyError:
        site_lang = 'en'
    site_lang = site_lang.replace('_','-')
    site=pywikibot.Site(site_lang,'wikipedia')
    repo=site.data_repository()
    #qid = 'Q1'
    sitelinks = repo.get_sitelinks(qid)
    for lang in sitelinks:
        if '_' in lang:
            newlang = lang.replace('_','-')
            sitelinks[newlang] = {'title':sitelinks[lang]['title']}
            del sitelinks[lang]
    #print sitelinks.keys()
    #pull the enwiki link
    enwiki = sitelinks['{0}wiki'.format(site_lang)]['title']
    pg = pywikibot.Page(site, enwiki)
    enwiki_text = pg.get()
    local = textlib.getLanguageLinks(enwiki_text, insite=site)
    if not local and pg.namespace() == 10:
        try:
            enwiki_text = pywikibot.Page(site, pg.title()+'/doc').get()
            local = textlib.getLanguageLinks(enwiki_text, insite=site, template_subpage=True)
        except pywikibot.NoPage:
            pass
    all_langs = union(sitelinks.keys(), local.keys())
    header = """
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th>Language</th>
                    <th>Local</th>
                    <th>Wikidata</th>
                  </tr>
                </thead>
                <tbody>
    """
    footer = """
                </tbody>
              </table>
    """
    text = ''
    allgood=True
    for lang in all_langs:
        row = ''
        prefix = lang.replace('wiki','').replace('_','-')
        row+='<td><a href="//{1}.wikipedia.org/wiki/{0}:">{0}wiki</a></td>'.format(prefix, site_lang)
        l = None
        d = None
        if lang in local:
            row+='<td><a href="//{2}.wikipedia.org/wiki/{0}:{1}">{0}:{1}</a></td>'.format(prefix, local[lang], site_lang)
            l = local[lang]
        else:
            row+='<td class=muted>----</td>'
        if lang in sitelinks:
            row+='<td><a href="//{2}.wikipedia.org/wiki/{0}:{1}">{0}:{1}</a></td>'.format(prefix, sitelinks[lang]['title'], site_lang)
            d=sitelinks[lang]['title']
        else:
            row+='<td class=muted>----</td>'

        if (l and d) and (l == d):
            row = '<tr class="done">'+row
        elif d and not l:
            row = '<tr class="done">'+row
        else:
            #lets see if its a redirect.
            checked=False
            if l and d:
                s = pywikibot.Site(prefix, 'wikipedia')
                l_p = pywikibot.Page(s, l)
                d_p = pywikibot.Page(s, d)
                if l_p.isRedirectPage():
                    if d_p == l_p.getRedirectTarget():
                        row = '<tr class="already">'+row
                        checked=True
                elif d_p.isRedirectPage():
                    if l_p == d_p.getRedirectTarget():
                        row = '<tr class="already">'+row
                        checked=True
            if not checked:
                row = '<tr class="not">'+row
                allgood=False
        row +='</td>\n'
        text+=row
    msg=''
    if allgood and local:
        msg='<p><center><a href="//{1}.wikipedia.org/wiki/{0}">{0}</a> can be removed of interwiki links.</center></p>'.format(enwiki, site_lang)
    elif allgood and not local:
        msg='<p><center><a href="//{2}.wikipedia.org/wiki/{0}">{0}</a> (<a href="//www.wikidata.org/wiki/{1}">{1}</a>) has successfully been migrated to Wikidata.</center></p>'.format(enwiki, qid.upper(), site_lang)
    else:
        msg='<p><center>Status of <a href="//{2}.wikipedia.org/wiki/{0}">{0}</a> (<a href="//www.wikidata.org/wiki/{1}">{1}</a>):</center></p>'.format(enwiki, qid.upper(), site_lang)
    text = msg+ header + text + footer
    print bootstrap.main(tool='checker.py', stuff=text, title='checker.py')



if __name__ == "__main__":
    main()
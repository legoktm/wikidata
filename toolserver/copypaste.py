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




#the form page
form = """
      <form class="form-signin" action="/~legoktm/cgi-bin/wikidata/copypaste.py" method="get">
        <h2 class="form-signin-heading">Please enter an id.</h2>
        <input type="text" class="input-block-level" name="id" placeholder="Q##">
        <!--<input type="text" class="input-block-level" name="site" placeholder="en">-->
        <button class="btn btn-large btn-primary" type="submit">Check</button>
      </form>
"""

def main():
    stuff = cgi.FieldStorage()
    try:
        qid = stuff['id'].value.lower()
    except KeyError:
        print bootstrap.main(tool='copypaste.py', stuff=form, title='copypaste.py')
        return
    site=pywikibot.Site('en','wikipedia')
    repo=site.data_repository()
    #qid = 'Q1'
    sitelinks = repo.get_sitelinks(qid)
    links = list()
    keys = sorted(sitelinks.keys())
    for site in keys:
        lang = site.replace('wiki','').replace('_','-')
        link = sitelinks[site]['title']
        links.append('[[{0}:{1}]]'.format(lang, link))
    text = '\n'.join(links)
    text = '<textarea rows="30" cols="100">'+text+'</textarea>'

    print bootstrap.main(tool='copypaste.py', stuff=text, title='copypaste.py')



if __name__ == "__main__":
    main()
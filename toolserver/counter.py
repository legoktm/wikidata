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
print "Content-Type: text/html\n"
import cgitb
cgitb.enable()
import cgi
import pywikibot
stuff = cgi.FieldStorage()
#lang = stuff['lang'].value
lang = 'en'
site = pywikibot.Site(lang, 'wikipedia')
import oursql

t_query = """
/* SLOW_OK */
SELECT
 COUNT(*)
FROM templatelinks
JOIN page
ON page_id = tl_from
WHERE tl_namespace=10
AND tl_title=?
AND page_namespace=0
"""
c_query = """
/* SLOW_OK */
SELECT
 COUNT(*)
FROM categorylinks
JOIN page
ON page_id = cl_from
WHERE cl_to=?
AND page_namespace=0
"""


def getdb(lang):
    wiki = lang + '.wikipedia.org'
    db = oursql.connect(db='toolserver', host="sql", read_default_file="/home/legoktm/.my.cnf")
    cur = db.cursor()
    cur.execute("SELECT dbname, server FROM `wiki` WHERE domain = '%s' LIMIT 1" %wiki)
    res = cur.fetchall()[0]
    return [res[0], 's' + str(res[1])]


def count(query, data, dbname, database):
    db = oursql.connect(db=dbname, host="sql-%s" %(database), read_default_file="/home/legoktm/.my.cnf")
    cur = db.cursor()
    cur.execute(query, (data,))
    query = cur.fetchall()
    res = query[0][0]
    cur.close()
    return res

#source = stuff['source'].value
source = 'Category:Ice hockey teams in Ontario'
if source.startswith(tuple(site.namespaces()[14])):
    s_p = pywikibot.Category(site, source)
    query = c_query
elif source.startswith(tuple(site.namespaces()[10])):
    s_p = pywikibot.Page(site, source)
    query = t_query
else:
    raise ValueError
name = s_p.title(withNamespace=False).replace(' ', '_')

print count(query, name, *getdb(lang))
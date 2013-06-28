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
import oursql
import sys
import os
import cgitb; cgitb.enable()
import cgi
import logs

db = oursql.connect(db='u_legoktm_wikidata_properties_p',
    host="sql-s1-user.toolserver.org",
    read_default_file=os.path.expanduser("~/.my.cnf"),
)

path = '/home/legoktm/public_html/static/{0}.html'

cursor = db.cursor()
cursor.execute("SELECT id FROM `jobs` WHERE done=1")
for row in cursor:
    id = row[0]
    filename = path.format(str(id))
    if os.path.exists(filename):
        continue
    dump = logs.main(id)
    with open(filename, 'w') as f:
        f.write(dump)
        print 'generated {0}'.format(str(id))


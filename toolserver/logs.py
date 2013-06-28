#!/usr/bin/env python
from __future__ import unicode_literals
"""
Copyright (C) 2013 Legoktm

Licensed as CC-Zero. See https://creativecommons.org/publicdomain/zero/1.0 for more details.
"""
print "Content-type: text/html\n\n"
import oursql
import sys
import os
import cgitb; cgitb.enable()
import cgi
import datetime
import bootstrap
import redirect

def noparam():
    print 'Please add the job parameter.'

def convert_status(value,css=False):
    if css:
        return ['not','done','already'][value]
    else:
        return ['Not done','Done','Already done'][value]

def plink(pid):
    return '<a href="//www.wikidata.org/wiki/Property:{pid}">Property:{pid}</a>'.format(pid=pid)

def qlink(qid):
    return '<a href="//www.wikidata.org/wiki/{qid}">{qid}</a>'.format(qid=str(qid))

def main(job_id):
    db = oursql.connect(db='u_legoktm_wikidata_properties_p',
            host="sql-s1-user.toolserver.org",
            read_default_file=os.path.expanduser("~/.my.cnf"),
    )


    cursor = db.cursor()


    query = """
    SELECT
     lang,
     source,
     pid,
     target_qid,
     user,
     timestamp,
     done,
     pid2,
     qid2,
     pid3,
     qid3,
     pid4,
     qid4,
     pid5,
     qid5
    FROM jobs
    WHERE id=?
    """
    cursor.execute(query, (job_id,))
    data = cursor.fetchone()
    info = """<p>Data was imported from <a href="//www.wikidata.org/wiki/{lang}:{source}">{lang}:{source}</a>.
    {pid} was linked with {targetqid}.
    It was requested by <a href="//www.wikidata.org/wiki/User:{user}">{user}</a>. """
    if data[6]:
        info+='The task finished at {ts}.'
    else:
        info+='The task started at {ts}, and is currently running.'
    if data[7]:
        info+= '\n<br />The following properties were also added:\n<ul>'
        info+= '<li>{pid} --> {qid}</li>\n'.format(pid=plink(data[7]), qid=qlink(data[8]))
        if data[9]:
            info+= '<li>{pid} --> {qid}</li>\n'.format(pid=plink(data[9]), qid=qlink(data[10]))
            if data[11]:
                info+= '<li>{pid} --> {qid}</li>\n'.format(pid=plink(data[11]), qid=qlink(data[12]))
                if data[13]:
                    info+= '<li>{pid} --> {qid}</li>\n'.format(pid=plink(data[13]), qid=qlink(data[14]))
        info+='</ul>\n'
    info += '</p>'

    info = info.format(
        lang=data[0],
        source=unicode(data[1]),
        pid=plink(data[2]),
        targetqid=plink(data[3]),
        user=unicode(data[4]),
        ts=data[5].strftime('%Y-%m-%dT%H:%M:%SZ'),
    )


    query = """
    SELECT
     lang,
     page,
     success,
     comment,
     item,
     timestamp
    FROM edits
    WHERE job_id=?
    """
    cursor = db.cursor()
    cursor.execute(query, (job_id,))

    header = """
              <table class="table table-bordered">
                <thead>
                  <tr>
                    <th>Page</th>
                    <th>Status</th>
                    <th>Item</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
    """
    footer = """
                </tbody>
              </table>
    """
    text =''
    for lang,page,success,comment,item,timestamp in cursor:
        if not comment:
            comment = ''
        else:
            comment = ': '+comment
        link = '<a href="//www.wikidata.org/wiki/{lang}:{page}">{lang}:{page}</a>'.format(lang=lang, page=unicode(page))
        if item:
            item_link = '<td><a href="//www.wikidata.org/wiki/Q{item}">Q{item}</a></td>'.format(item=item)
        else:
            item_link = '<td class=muted>--</td>'
       # print unicode(ts)
       # print type(ts)
        row = '<tr class="{css}"><td>{link}</td><td>{status}{comment}</td>{itemlink}<td>{ts}</td></tr>\n'.format(
            link=unicode(link),
            status=convert_status(success),
            comment=comment,
            itemlink=item_link.decode('utf-8'),
            ts=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            css=convert_status(success,css=True)
        )
        text += row
    all = info+header+text+footer
    return bootstrap.main(tool='properties.js log', title='Job archive', stuff=unicode(all))

path = '/home/legoktm/public_html/static/{0}.html'


if __name__ == "__main__":
    stuff = cgi.FieldStorage()
    try:
        job_id = int(stuff['job'].value)
    except:
        noparam()
        sys.exit()
    if os.path.exists(path.format(str(job_id))):
        print redirect.main(job_id)
    else:
        print main(job_id)

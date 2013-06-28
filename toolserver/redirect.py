#!/usr/bin/env python
"""
Released into the public domain by Legoktm
"""
def main(job_id):
    return """
     <html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Redirecting</title>
    <meta http-equiv="refresh" content="0;URL='//toolserver.org/~legoktm/static/{0}.html'" />
  </head>
  <body>
    <p>Redirecting</p>
  </body>
</html>""".format(str(job_id))
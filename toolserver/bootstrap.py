from __future__ import unicode_literals
def main(tool, **kwargs):
    path = '//toolserver.org/~legoktm/bootstrap'
    if tool=='checker.py':
        nav = """<li><a href="//www.wikidata.org/wiki/User:Legobot/properties.js/Archive">properties.js log</a></li>
        <li class="active"><a href="//www.wikidata.org/wiki/User:Legoktm/checker.py">checker.py</a></li>
        <li><a href="//www.wikidata.org/wiki/User_talk:Legobot/properties.js">Requests</a></li>
        <li><a href="//toolserver.org/~legoktm/cgi-bin/wikidata/copypaste.py">copypaste.py</a></li>
    """
    elif tool=='copypaste.py':
        nav = """<li><a href="//www.wikidata.org/wiki/User:Legobot/properties.js/Archive">properties.js log</a></li>
        <li ><a href="//www.wikidata.org/wiki/User:Legoktm/checker.py">checker.py</a></li>
        <li><a href="//www.wikidata.org/wiki/User_talk:Legobot/properties.js">Requests</a></li>
        <li class="active"><a href="//toolserver.org/~legoktm/cgi-bin/wikidata/copypaste.py">copypaste.py</a></li>
    """

    else:
        nav = """<li class="active"><a href="#">properties.js log</a></li>
        <li><a href="//www.wikidata.org/wiki/User:Legoktm/checker.py">checker.py</a></li>
        <li><a href="//www.wikidata.org/wiki/User_talk:Legobot/properties.js">Requests</a></li>
        <li><a href="//toolserver.org/~legoktm/cgi-bin/wikidata/copypaste.py">copypaste.py</a></li>
    """


    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <title>{title}</title>

    <!-- Le styles -->
    <link href="{path}/css/bootstrap.min.css" rel="stylesheet">
    <style>
    body {{
             padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
    }}
    </style>
    <link href="{path}/css/bootstrap-responsive.min.css" rel="stylesheet">
    <link href="//toolserver.org/~legoktm/local.css" rel="stylesheet">

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
    <script src="{path}/js/html5shiv.js"></script>
    <![endif]-->
    </head>

    <body>

    <div class="navbar navbar-inverse navbar-fixed-top">
    <div class="navbar-inner">
    <div class="container">
    <button type="button" class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    </button>
    <a class="brand" href="#">Wikidata</a>
    <div class="nav-collapse collapse">
    <ul class="nav">
    {nav}
    </ul>
    </div><!--/.nav-collapse -->
    </div>
    </div>
    </div>

    <div class="container">

    {stuff}

    </div> <!-- /container -->

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="{path}/js/jquery.js"></script>

    </body>
    </html>
    """.format(path=path, nav=nav, **kwargs).encode('utf-8')

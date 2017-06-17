#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# see benchsimple.py
# configuration for pystpl

def escape_text(s):
    s = s.replace(u"&", u"&amp;") # must be done first!
    s = s.replace(u"<", u"&lt;")
    s = s.replace(u">", u"&gt;")
    s = s.replace(u'"', u"&quot;")
    s = s.replace(u"'", u"&#39;")
    return s

config = {

"template" : """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
          "http://www.w3.org/TR/html4/loose.dtd">
<html>

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <style type="text/css">
	tr.row1 { background-color: #00ffff; }
	tr.row2 { background-color: #ffff00; }
	td.red  { background-color: #ff0000; }
    </style>

    <title>Benchsimple | [[title]]</title>
</head>

<body>
    <h1>Benchsimple | [[title]]</h1>
    <ul id="nav">
[[FOR i,item IN navigation]]
        <li><a href="[[item.href]]" id="btn-[[i]]">[[item.caption]]</a></li>
[[ENDFOR]]
    </ul>

    <table>
[[FOR i,row IN table]]
        <tr class="[[IF i == 1]]row1[[ENDIF]][[IF i == 2]]row2[[ENDIF]][[IF i == 3]]row1[[ENDIF]][[IF i == 4]]row2[[ENDIF]][[IF i == 5]]row1[[ENDIF]]">
[[FOR col IN row]]
            <td[[IF col == 33]] class="red"[[ENDIF]]>[[col]]</td>
[[ENDFOR]]
        </tr>
[[ENDFOR]]
    </table>

</body>
</html>
""",

"module"   : "pystpl",
"import"   : "import sys;sys.path.append('../../');import pystpl; from config_pystpl import escape_text",
"complete" : "t = pystpl.Tpl(template, '[[', ']]'); r = t.substitute(context_dict, escape_text)",
"parse"    : "t = pystpl.Tpl(template, '[[', ']]')",
"render"   : "r = t.substitute(context_dict, escape_text)"
}

#-----------------------------------------


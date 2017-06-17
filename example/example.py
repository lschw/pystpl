# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
import pystpl

# simulate a global gettext method "_()"
if sys.version_info > (3,0):
    import builtins
    __builtins__._ = lambda x : "TRANSLATED TEXT"
else:
    import __builtin__
    __builtin__._ = lambda x : "TRANSLATED TEXT"

print(pystpl.__version__)

# example template text
text = """
Lorem ipsum dolor sit [[var1]] amet, consectetur adipisicing [[foo.bar]] elit.

[[FOR i,item1 IN list1]][[FOR j,item2 IN list2]]
    [[i]],[[j]]: [[item1]], [[item2]]
[[ENDFOR]][[ENDFOR]]

[[FOR item IN list1]]
    [[item]]
[[ENDFOR]]

[[IF var2 == "lalilu"]]
    var2 is lalilu
[[ELSE]]
    var2 is not lalilu
[[ENDIF]]

[[IF var3 > 103]]
    var3 > 103
[[ENDIF]]

[[IF var3 < 103]]
    var3 < 103
[[ENDIF]]

[[IF var3 <= 103]]
    var3 <= 103
[[ENDIF]]

[[IF var3 <= 103]]
    var3 <= 103
[[ENDIF]]

[[IF var3 != 103]]
    var3 != 103
[[ENDIF]]

[[IF var1 == var2]]
    var1 == var2
[[ENDIF]]

escape tag characters via repetition of tag: [[[[ok]]]]

Lorem ipsum dolor sit [[{some translateable text}]] amet.
"""

# example data
data = {
    "var1" : "this is a test",
    "var2" : "lalilu",
    "var3" : 10,
    "foo" : {"bar" : 123},
    "list1" : [44,56,11],
    "list2" : ["blub", "haha"]
}

# example quote method
def quote(text):
    return text.replace("a", "AA")

try:
    # parse template
    tpl = pystpl.Tpl(text)
    
    # evaluate template and fill placeholders with data
    print(tpl.substitute(data, quote))
except pystpl.TplError as e:
    print(e)

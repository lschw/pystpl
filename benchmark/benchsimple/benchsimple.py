#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple template-engine benchmark.

This benchmark is derived from a benchmark proposed in a german Python-forum.
("Das deutsche Python-Forum": "Templating gesucht..." from "jens", 2006-02-16)

It was then modified, modularized, enhanced and adapted to several
template-engines by Roland Koebler.

For details, see http://www.simple-is-better.org/template/

:Requires:  Python 2.x / 3.x
:Version:   benchsimple2 / 2013-04-02
:Author:    Roland Koebler <rk at simple-is-better dot org>

:RCS:       $Id: benchsimple.py,v 1.6 2013/04/02 14:52:04 rk Exp $
"""
__version__ = "2013-04-02"
__author__   = "Roland Koebler <rk at simple-is-better dot org>"

import timeit, sys

#-----------------------------------------
#configuration
result = open("bench.simple.html", 'r').read()

context_dict = ({
    'title': 'Some <test>',
    'navigation': [
        {'href': '#"\'', 'caption': '''escaping &<>'''},
        {'href': '#', 'caption': 'foobar'},
        {'href': '#', 'caption': 'baz'}
    ],
    'table': [
        [1,2,3,4,5,6,7,8,9,0],
        [11,12,13,14,15,16,17,18,19,10],
        [21,22,23,24,25,26,27,28,29,20],
        [31,32,33,34,35,36,37,38,39,30],
        [41,42,43,44,45,46,47,48,49,40]
    ],
    'highlight' : 33
})

N = 1000

#----------------------
# result-checking
def test_results(*args):
    """Test if the template-results are correct.

    :Example:
        r1 = template.render()
        r2 = template.render()
        test_result(r1, r2)
    """
    if len(args) == 0:
        raise ValueError("missing parameters.")
    ok = 0
    for r in args:
        if r == result:
            ok += 1
        elif r == result.replace("#&quot;", "#&#34;"):
            ok += 1
    if ok == 0:
        print("****wrong result:")
        print(args[0])
        print(args[0] == result)
        print(len(result), len(args[0]), args[0][:2100] == result[:2100])
        print("****")
    print("  -> %d results ok, %d wrong." % (ok, len(args)-ok))

#-----------------------------------------
# benchmark

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("""USAGE: benchsimple.py <TEMPLATEENGINEs>""")
        sys.exit(1)

    print("""benchsimple %s:
    iterations: %d (except for import)
    notes:
        import:   time for import
        complete: complete parsing+rendering
        parse:    may include compilation, depending on template-engine.
        render:   render template with custom data.
        "render only" benefits from caches, "complete" does not""" % (__version__, N))
    print("-----------------------")

    for engine_name in sys.argv[1:]:

        # import template-configuration
        if 'config' in dir():
            del config
        exec("from config_%s import config" % engine_name)

        # import template-engine + benchmark "import"
        t_import = timeit.Timer(config["import"]).timeit(1)
        exec(config["import"])
        exec("import %s" % config["module"])
        # print name/version of template
        try:
            v = eval(config["module"]).__version__
        except AttributeError:
            v = "?.?"
        print(eval(config["module"]).__name__ + " " + v)

        # benchmark "complete"
        t_complete = timeit.Timer(setup=config["import"]+"""\ntemplate=%s; context_dict=%s\n""" % (repr(config["template"]), context_dict),
                                   stmt=config["complete"]).timeit(N)/N
        template = config["template"]
        exec(config["complete"])
        r_complete = r

        # benchmark "parse only"
        if config["parse"]:
            t_parse = timeit.Timer(setup=config["import"]+"""\ntemplate=%s; context_dict=%s\n""" % (repr(config["template"]), context_dict),
                                    stmt=config["parse"]).timeit(N)/N

        # benchmark "render only"
        if config["render"]:
            t_render = timeit.Timer(setup=config["import"]+"""\ntemplate=%s; context_dict=%s\n""" % (repr(config["template"]), context_dict)+config["parse"],
                                     stmt=config["render"]).timeit(N)/N
            exec(config["parse"])
            exec(config["render"])
            r_render1 = r
            exec(config["render"])
            r_render2 = r

        # check + print result
        if config["render"]:
            test_results(r_complete, r_render1, r_render2)
            print("  import:      %8.4f ms" % (t_import  *1000))
            print("  complete:    %8.4f ms" % (t_complete*1000))
            print("  parse only:  %8.4f ms" % (t_parse   *1000))
            print("  render only: %8.4f ms" % (t_render  *1000))
        else:
            test_results(r_complete)
            print("  import:      %8.4f ms" % (t_import  *1000))
            print("  complete:    %8.4f ms" % (t_complete*1000))

        print("-----------------------")

#-----------------------------------------


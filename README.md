# pystpl
a small and simple template parser

## Installation
Download the latest release from [/releases/latest](https://github.com/lschw/pystpl/releases/latest).

Either copy the *pystpl/* directory to your desired location or install via

    cd /path/to/extracted/files
    pip install .

## Usage

### Example
    
    import pystpl
    
    data = {
        "var1" : "this is a test",
        "foo" : {"bar" : 123},
        "list" : [44,56,11]
    }
    
    text = """
        Lorem ipsum dolor sit [[var1]] amet, consectetur adipisicing [[foo.bar]] elit.
        
        [[FOR i,item IN list1]]
            [[i]]: [[item]]
        [[ENDFOR]]
        
        [[IF var1 == "abc"]]
            var1 is abc
        [[ELSE]]
            var1 is not abc
        [[ENDIF]]
    """
    
    tpl = pystpl.Tpl(text)
    print(tpl.substitute(data))

For a more detailed example see [example/example.py](example/example.py)

### Tags
Tags are statements in the template which mark variables, loops or conditions. By default, tags are marked with '[[' and ']]', however, these opening and closing characters can be changed.

    tpl = pystpl.Tpl(text, tag_open="[[", tag_close="]]")

### Variables
Variables are marked as [[var]]. This tag is replaced with the content of the variable named *var* in the data dict given in the substitute method. If the variables itself are dicts or objects, properties or members can be accessed via dot separated names, e.g. [[foo.bar]]. This would correspond to

    data = {
        "foo": {"bar" : 123}
    }

### Translateable strings
Translateable strings can be marked via curly brakets inside a tag

    [[{text to translate}]]

All these strings are passed to a *_()* method as defined by gettext.

### Loops
Lists can be loop through via

    [[FOR item in mylist]]
        Bla [[item]] blub
    [[ENDFOR]]

This construct loops through all items in the list *mylist*, e.g. with
    
    data = {
        "mylist" : ["value1", "value2", "value3"]
    }

this would result in
    
    Bla value1 blub
    Bla value2 blub
    Bla value3 blub

If the current loop index is required it can be accessed via a variable separated by a comma before the loop variable

    [[FOR i,item in mylist]]
        Index [[i]], bla [[item]] blub
    [[ENDFOR]]

### Conditions
Conditions can be evaluated via

    [[IF item1 OP item2]]
        text if condition is true
    [[ELSE]]
        text if condition is false
    [[ENDIF]]

item1 and item2 can be
 * variable names
 * strings quoted with " "
 * integers, floats
 * TRUE, FALSE
 * NONE

the operation OP can be
 * ==
 * !=
 * &lt;
 * &gt;
 * &lt;=
 * &gt;=

### Escaping characters
Text in variables can be escaped through an optional method given to the substitute method, e.g.

    def escape(var):
        var = var.replace("<", "&lt;")
        var = var.replace(">", "&gt;")
        return var
    
    tpl.substitute(data, escape)

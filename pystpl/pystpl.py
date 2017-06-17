# pystpl - a small and simple template parser
# Copyright (C) 2017 Lukas Schwarz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import copy
import re

class TplError(Exception):
    """
    Exception raised if parse or substitution error occurs
    """
    def __init__(self, msg, line, pos, tpl=None):
        """
        msg  : error message
        line : line in template where error occured
        pos  : position in error line
        tpl  : template text
        """
        Exception.__init__(self, msg)
        self.msg = msg
        self.line = line
        self.pos = pos
        self.tpl = tpl
    
    def __str__(self):
        return "{} in template in line {} at position {}".format(
            self.msg, self.line, self.pos
        )


class Tag:
    """
    Represents a single template tag
    """
    def __init__(self, name, start, end, line, pos):
        """
        name  : name of tag = characters inside open and close characters
        start : global position of open character
        end   : global position after close character
        line  : line where tag occurs
        pos   : position in line where tag occurs
        """
        self.name = name
        self.start = start
        self.end = end
        self.line = line
        self.pos = pos


def var_exists(var, data):
    """
    Checks if a variable `var` in the format "abc[.foo[.bar[...]]]" in the
    dict or object `data` exists
    
    var  : name of variable
    data : variable lookup dict or object
    """
    if var == "":
        return False
    parts = var.split(".")
    value = data
    for part in parts:
        if hasattr(value, part):
            value = getattr(value, part)
        elif part in value:
            value = value[part]
        else:
            return False
    return True


def get_var(var, data):
    """
    Returns value of variable `var` in the format "abc[.foo[.bar[...]]]" in the
    dict or object `data`
    
    var  : name of variable
    data : variable lookup dict or object
    """
    if var == "":
        raise KeyError("Unknown variable '{}'".format(var))
    parts = var.split(".")
    value = data
    for part in parts:
        if hasattr(value, part):
            value = getattr(value, part)
        elif part in value:
            value = value[part]
        else:
            raise KeyError("Unknown variable '{}'".format(var))
    return value


class Condition:
    """
    Class handles and checks a symbolic condition of two items which can be
    either strings, numbers, boolean, None or variables
    """
    def __init__(self, item1, item2, op):
        """
        item1 : either string, number, boolean, None, variable name
        item2 : either string, number, boolean, None, variable name
        op    : symbolic operation, e.g. "==", "<=", ...
        """
        self.item1 = item1
        self.item2 = item2
        if op not in ["==", "<=", ">=", "!=", "<", ">"]:
            raise ValueError("Invalid operator '{}'".format(op))
        self.op = op
    
    
    def check(self, data):
        """
        Check whether condition is True or False
        data : storage for variables
        """
        
        # fetch actual values of items
        item1 = self._parse_item(self.item1, data)
        item2 = self._parse_item(self.item2, data)
        
        # evaluate condition
        if self.op == "==":
            return item1 == item2
        if self.op == "<=":
            return item1 <= item2
        if self.op == "<":
            return item1 < item2
        if self.op == ">=":
            return item1 >= item2
        if self.op == ">":
            return item1 > item2
        if self.op == "!=":
            return item1 != item2
    
    
    def _parse_item(self, item, data):
        """
        Return actual content of item
        
        item : item to fetch content
        data : storage for variables
        """
        
        # item is string
        if item.startswith('"') and item.endswith('"'):
            return item[1:-1]
        
        # item is number
        if re.match(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$", item):
            return float(item)
        
        # item is boolean or None
        if re.match("^(true)$", item,  re.IGNORECASE):
            return True
        if re.match("^(false)$", item,  re.IGNORECASE):
            return False
        if re.match("^(none)$", item,  re.IGNORECASE):
            return None
        
        # item is a variable
        return get_var(item, data)


class TplItem:
    """
    Base class for template items
    """
    def __init__(self, parent, line, pos):
        """
        parent : parent item
        line   : line where item occurs
        pos    : position in line whre item occurs
        """
        self.parent = parent
        self.line = line
        self.pos = pos
        pass
    
    
    def render(self, data, escape_var=None):
        """
        Render item
        data       : storage for variables
        escape_var : text escape function
        """
        pass


class TplItemText(TplItem):
    """
    Template item for text
    """
    def __init__(self, parent, line, pos, text, tag_open, tag_close):
        """
        text      : text
        tag_open  : tag open characters
        tag_close : tag close characters
        """
        TplItem.__init__(self, parent, line, pos)
        self.text = text
        self.tag_open = tag_open
        self.tag_close = tag_close
    
    
    def render(self, data, escape_var=None):
        """
        Render item
        """
        text = str(self.text)
        
        # replace escaped open/close characters (double occurrence)
        text = text.replace(self.tag_open+self.tag_open, self.tag_open)
        text = text.replace(self.tag_close+self.tag_close, self.tag_close)
        return text


class TplItemVar(TplItem):
    """
    Template item which is a single variable
    """
    def __init__(self, parent, line, pos, var):
        """
        var : variable name
        """
        TplItem.__init__(self, parent, line, pos)
        self.var = var
    
    
    def render(self, data, escape_var=None):
        """
        Render item
        """
        try:
            text = str(get_var(self.var, data))
            if escape_var != None:
                text = escape_var(text)
            return text
        except Exception as e:
            raise TplError(e, self.line, self.pos)


class TplItemTranslate(TplItem):
    """
    Template item which is a single string to translate (with gettext)
    """
    def __init__(self, parent, line, pos, text):
        """
        text : text to translate
        """
        TplItem.__init__(self, parent, line, pos)
        self.text = text
    
    
    def render(self, data, escape_var=None):
        """
        Render item
        """
        return _(str(self.text))


class TplItemLoop(TplItem):
    """
    Template item which represents a for loop
    """
    def __init__(self, parent, line, pos, var_tmp, var_loop, var_index):
        """
        var_tmp   : name of variable which holds a single list item
        var_loop  : name of variable which holds the list
        var_index : name of variable which will hold loop index
        """
        TplItem.__init__(self, parent, line, pos)
        self.var_tmp = var_tmp
        self.var_loop = var_loop
        self.var_index = var_index
        self.childs = [] # child items for rendering inside loop
    
    
    def render(self, data, escape_var=None):
        """
        Render item
        """
        # check if item variable hides global variable
        if var_exists(self.var_tmp, data):
            raise TplError(
                "Loop variable '{}' ".format(self.var_tmp) + 
                "hides global variable", self.line, self.pos
            )
        
        # check if index variable hides global variable
        if self.var_index and ( var_exists(self.var_index, data) or \
                self.var_index == self.var_tmp):
            raise TplError(
                "Index variable '{}' ".format(self.var_index) + 
                "hides global variable", self.line, self.pos
            )
        
        ret = ""
        
        # get list
        try:
            var_loop = get_var(self.var_loop, data)
        except Exception as e:
            raise TplError(e, self.line, self.pos)
        
        # temporary variable storage
        data2 = copy.deepcopy(data)
        
        for i,var in enumerate(var_loop):
            
            # make item variable available
            data2[self.var_tmp] = var
            
            # make loop cnt variable available
            if self.var_index:
                data2[self.var_index] = i+1 
            for child in self.childs:
                ret += child.render(data2, escape_var)
        return ret


class TplItemIf(TplItem):
    """
    Template item which represents an if-else condition
    """
    def __init__(self, parent, line, pos, condition):
        """
        condition : condition object
        """
        TplItem.__init__(self, parent, line, pos)
        self.condition = condition
        self.childs_true = [] # child items if condition is True
        self.childs_false = [] # child items if condition is False
    
    
    def render(self, data, escape_var=None):
        """
        Render item
        """
        ret = ""
        try:
            if self.condition.check(data):
                for child in self.childs_true:
                    ret += child.render(data, escape_var)
            else:
                for child in self.childs_false:
                    ret += child.render(data, escape_var)
        except Exception as e:
            raise TplError(e, self.line, self.pos)
        return ret


class Tpl:
    """
    Class representing a template
    """
    
    def __init__(self, tpl, tag_open="[[", tag_close="]]"):
        """
        tpl       : template text
        tag_open  : open tag characters
        tag_close : close tag characters
        """
        self.tpl = tpl
        self.tpl_items = []
        self.tag_open = re.escape(tag_open)
        self.tag_close = re.escape(tag_close)
        
        # regular expressions for finding tags
        self.re_tag = re.compile(self.tag_open+"(.*?)"+self.tag_close)
        self.re_loop_start = re.compile(r"^(FOR) ((([a-zA-Z0-9_]*),)*)([a-zA-Z_]([a-zA-Z0-9_]*)*) (IN) ([a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*)$")
        self.re_loop_end = re.compile(r"^(ENDFOR)$")
        self.re_if_start = re.compile(r"^(IF) (.*) (==|<=|>=|!=|<|>) (.*)$")
        self.re_if_end = re.compile(r"^(ENDIF)$")
        self.re_else = re.compile(r"^(ELSE)$")
        self.re_var = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*)$")
        self.re_translate = re.compile(r"^\{(.*)\}$")
        
        try:
            self._parse(tpl, tag_open, tag_close)
        except TplError as e:
            e.tpl = self.tpl
            raise
    
    
    def _parse(self, tpl, tag_open, tag_close):
        """
        Parse template and create items
        tpl       : template text
        tag_open  : open tag characters
        tag_close : close tag characters
        """
        
        tag_last = Tag(None, 0, 0, 0, 0) # last found tag
        search_start = 0 # current search position
        cur_childs = [] # current childs
        cur_parent = None # current parent
        cur_parent_type = ["global"] # type of current parent item
                                     # (global, loop, cond_true, cond_false)
        
        # replace escaped (by double occurrence) tag characters with arbitrary
        # other characters (here '@') to prevent a matching
        tpl = tpl.replace(tag_open+tag_open, "@"*2*len(tag_open))
        tpl = tpl.replace(tag_close+tag_close, "@"*2*len(tag_close))
        
        # loop until end of template is reached
        while True:
            
            # fetch next tag
            m = self.re_tag.search(tpl, search_start)
            if not m:
                # no more tag found -> we are at the end of the template
                
                if cur_parent_type[-1] != "global":
                    raise TplError("End is reached without closing all tags",
                        tag.line, tag.pos)
                
                # create text item from text between last tag and end
                line, pos = self._get_line_pos(tag_last.end)
                cur_childs.append(
                    TplItemText(
                        cur_parent, line, pos, self.tpl[tag_last.end:],
                        tag_open, tag_close
                    )
                )
                self.tpl_items += cur_childs
                break
            
            # create tag object
            tag = Tag(
                m.group(1), m.start(), m.end(), *self._get_line_pos(m.start())
            )
            
            # create text item from text between last tag and current tag
            cur_childs.append(
                TplItemText(
                    cur_parent, tag.line, tag.pos,
                    self.tpl[tag_last.end:tag.start], tag_open, tag_close
                )
            )
            search_start = tag.end
            tag_last = tag
            
            # check for FOR tag
            m = self.re_loop_start.match(tag.name)
            if m:
                # remove one newline character from the end of last (text) child
                if cur_childs and isinstance(cur_childs[-1], TplItemText):
                    if cur_childs[-1].text.endswith("\n"):
                        cur_childs[-1].text = cur_childs[-1].text[:-1]
                
                # create loop item
                new_parent = TplItemLoop(
                    cur_parent, tag.line, tag.pos, m.group(5), m.group(8),
                    m.group(4)
                )
                
                # add childs dependent of parent type
                cur_childs.append(new_parent)
                if cur_parent_type[-1] == "global":
                    self.tpl_items += cur_childs
                if cur_parent_type[-1] == "loop":
                    cur_parent.childs += cur_childs
                if cur_parent_type[-1] == "cond_true":
                    cur_parent.childs_true += cur_childs
                if cur_parent_type[-1] == "cond_false":
                    cur_parent.childs_false += cur_childs
                
                cur_parent = new_parent
                cur_parent_type.append("loop")
                cur_childs = []
                continue
            
            # check for ENDFOR tag
            m = self.re_loop_end.match(tag.name)
            if m:
                if cur_parent_type[-1] != "loop":
                    raise TplError(
                        "End loop tag without opening loop tag " +
                        "or missmatching nesting", tag.line, tag.pos
                    )
                
                # remove one newline character from the end of last (text) child
                if cur_childs and isinstance(cur_childs[-1], TplItemText):
                    if cur_childs[-1].text.endswith("\n"):
                        cur_childs[-1].text = cur_childs[-1].text[:-1]
                
                cur_parent.childs += cur_childs
                cur_parent = cur_parent.parent
                cur_parent_type.pop()
                cur_childs = []
                continue
            
            # check for start IF tag
            m = self.re_if_start.match(tag.name)
            if m:
                # remove one newline character from the end of last (text) child
                if cur_childs and isinstance(cur_childs[-1], TplItemText):
                    if cur_childs[-1].text.endswith("\n"):
                        cur_childs[-1].text = cur_childs[-1].text[:-1]
                
                # create IF item
                new_parent = TplItemIf(
                    cur_parent, tag.line, tag.pos,
                    Condition(m.group(2), m.group(4), m.group(3))
                )
                
                # add childs dependent of parent type
                cur_childs.append(new_parent)
                if cur_parent_type[-1] == "global":
                    self.tpl_items += cur_childs
                if cur_parent_type[-1] == "loop":
                    cur_parent.childs += cur_childs
                if cur_parent_type[-1] == "cond_true":
                    cur_parent.childs_true += cur_childs
                if cur_parent_type[-1] == "cond_false":
                    cur_parent.childs_false += cur_childs
                
                cur_parent = new_parent
                cur_parent_type.append("cond_true")
                cur_childs = []
                continue
            
            # check for ELSE tag
            m = self.re_else.match(tag.name)
            if m:
                # remove one newline character from the end of last (text) child
                if cur_childs and isinstance(cur_childs[-1], TplItemText):
                    if cur_childs[-1].text.endswith("\n"):
                        cur_childs[-1].text = cur_childs[-1].text[:-1]
                
                if cur_parent_type[-1] != "cond_true":
                    raise TplError(
                        "Else tag without opening if tag " +
                        "or missmatching nesting", tag.line, tag.pos
                    )
                
                cur_parent.childs_true += cur_childs
                cur_parent_type[-1] = "cond_false"
                cur_childs = []
                continue
            
            # check for ENDIF tag
            m = self.re_if_end.match(tag.name)
            if m:
                if cur_parent_type[-1] not in ["cond_true", "cond_false"]:
                    raise TplError("End if tag without opening if tag " +
                        "or missmatching nesting", tag.line, tag.pos)
                
                # remove one newline character from the end of last (text) child
                if cur_childs and isinstance(cur_childs[-1], TplItemText):
                    if cur_childs[-1].text.endswith("\n"):
                        cur_childs[-1].text = cur_childs[-1].text[:-1]
                
                # add childs dependent of parent type
                if cur_parent_type[-1] == "cond_true":
                    cur_parent.childs_true += cur_childs
                elif cur_parent_type[-1] == "cond_false":
                    cur_parent.childs_false += cur_childs
                cur_parent = cur_parent.parent
                cur_parent_type.pop()
                cur_childs = []
                continue
            
            # check for translateable string
            m = self.re_translate.match(tag.name)
            if m:
                cur_childs.append(
                    TplItemTranslate(cur_parent, tag.line, tag.pos, m.group(1))
                )
                continue
            
            # check for variable tag
            m = self.re_var.match(tag.name)
            if m:
                cur_childs.append(
                    TplItemVar(cur_parent, tag.line, tag.pos, tag.name)
                )
                continue
            
            raise TplError("Invalid tag '{}'".format(tag.name),
                tag.line, tag.pos)
        
    
    def substitute(self, data, escape_var=None):
        """
        Evaluate template by substitution of variables
        data       : storage for variables
        escape_var : text escape function
        """
        ret = ""
        for item in self.tpl_items:
            ret += item.render(data, escape_var)
        return ret
    
    
    def _get_line_pos(self, pos):
        """
        Get line number inside template of character at position `pos`
        pos : character position
        """
        line = self.tpl.count("\n", 0, pos)
        if line == 0:
            return (line, pos)
        
        line_begin = self.tpl[:pos].rfind("\n")
        return (line, pos-line_begin)



def load_from_file(filename, tag_open="[[", tag_close="]]"):
    """
    Create template object from file
    
    filename  : use text inside this file as template
    tag_open  : open tag characters
    tag_close : close tag characters
    """
    with open(filename) as fh:
        return Tpl(fh.read(), tag_open, tag_close)

#!/usr/bin/env python
###############################################################################
##
## MODULE      : tm-pygments.py
## DESCRIPTION : Syntax highlighting in TeXmacs using pygments,
##                  based on minimal.py by Darcy Shen and the OldHtmlFormatter
##                  of the Pygments documentation.
## COPYRIGHT   : (C) 2021 Jeroen Wouters, Darcy Shen
##
## This software falls under the GNU general public license version 3 or later.
## It comes WITHOUT ANY WARRANTY WHATSOEVER. For details, see the file LICENSE
## in the root directory or <http://www.gnu.org/licenses/gpl-3.0.html>.

import os
import sys
from os.path import exists
tmpy_home_path = os.environ.get("TEXMACS_HOME_PATH") + "/plugins/tmpy"
if (exists (tmpy_home_path)):
    sys.path.append(os.environ.get("TEXMACS_HOME_PATH") + "/plugins/")
else:
    sys.path.append(os.environ.get("TEXMACS_PATH") + "/plugins/")

from tmpy.protocol        import *
from tmpy.compat          import *

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound

from TeXmacsFormatter import TeXmacsFormatter

flush_verbatim("Pygments highlighting plugin")

while True:
    line = tm_input()
    if not line:
        continue
    
    if line.strip().startswith("%"):
         # flush_verbatim("The first line needs to start with %, \
         #    followed by the language and style to be used for highlighting, \
         #    separated by ;. \nE.g. \"% cpp; default\"")
         # while line != "<EOF>":
         #     line = tm_input ()
         # continue
         
        # drop initial "%"
        line = line.strip()[1:]
        if ';' in line:
            lang, style = map(lambda x: x.strip(), line.split(";",2))
        else:
            lang = line.strip()
            style = "default"
        lines = []
    else:
        lang = ""
        style = "default"
        lines = [line]
    
    if not(style in get_all_styles()):
        flush_verbatim("The style \'" + style + "\' is not supported")
        while line != "<EOF>":
            line = tm_input ()
        continue

    # Get the code to highlight
    while line != "<EOF>":
        line = tm_input ()
        #if line == '':
        #    continue
        lines.append(line)
    code = '\n'.join(lines[:-1])
    
    try:
        if lang == "":
            lexer = guess_lexer(code)
        else:
            lexer = get_lexer_by_name(lang)
        texmacs = highlight(code, lexer, \
            TeXmacsFormatter(style=style))
        flush_any ("texmacs:" + texmacs)
    except ClassNotFound:
        flush_verbatim("The language \'" + lang + "\' is not supported.")

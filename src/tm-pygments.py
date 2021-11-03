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

from pygments import highlight

from pygments.lexers import get_lexer_by_name
from pygments.styles import get_all_styles

from tmpy.protocol        import *
from tmpy.compat          import *

from pygments.formatter import Formatter

class TexmacsFormatter(Formatter):

    def __init__(self, **options):
        Formatter.__init__(self, **options)

        # create a dict of (start, end) tuples that wrap the
        # value of a token so that we can use it in the format
        # method later
        self.styles = {}

        # we iterate over the `_styles` attribute of a style item
        # that contains the parsed style values.
        for token, style in self.style:
            start = end = ''
            # a style item is a tuple in the following form:
            # colors are readily specified in hex: 'RRGGBB'
            if style['color']:
                start += '<with|color|#%s|' % style['color']
                end = '>' + end
            if style['bold']:
                start += '<with|font-series|bold|'
                end = '>' + end
            if style['italic']:
                start += '<with|font-shape|italic|'
                end = '>' + end
            if style['underline']:
                start += '<underline|'
                end = '>' + end
            self.styles[token] = (start, end)

    def serialize(self, value):
        serialization = ""
        for c in value:
            if c == '<':
                serialization += "\<less\>"
            elif c == '>':
                serialization += "\<gtr\>"
            elif c == '\\':
                serialization += "\\\\"
            elif c == '|':
                serialization += "\\|"
            else:
                serialization += c
        return serialization


    def format(self, tokensource, outfile):
        # lastval is a string we use for caching
        # because it's possible that a lexer yields a number
        # of consecutive tokens with the same token type.
        # to minimize the size of the generated texmacs markup we
        # try to join the values of same-type tokens here
        lastval = ''
        lasttype = None

        # wrap the whole output with <verbatim|...>
        outfile.write('<verbatim|')

        for ttype, value in tokensource:
            # if the token type doesn't exist in the stylemap
            # we try it with the parent of the token type
            # eg: parent of Token.Literal.String.Double is
            # Token.Literal.String
            while ttype not in self.styles:
                ttype = ttype.parent
            if ttype == lasttype:
                # the current token type is the same of the last
                # iteration. cache it
                lastval += value
            else:
                # not the same token as last iteration, but we
                # have some data in the buffer. wrap it with the
                # defined style and write it to the output file
                if lastval:
                    stylebegin, styleend = self.styles[lasttype]
                    outfile.write(stylebegin + self.serialize(lastval) + styleend)
                # set lastval/lasttype to current values
                lastval = value
                lasttype = ttype

        # if something is left in the buffer, write it to the
        # output file, then close the opened <verbatim|...> tag
        if lastval:
            stylebegin, styleend = self.styles[lasttype]
            outfile.write(stylebegin + self.serialize(lastval) + styleend)
        outfile.write('>\n')

flush_verbatim("Pygments highlighting plugin")

while True:
    line = tm_input()
    if not line:
        continue
    elif not line.strip().startswith("%"):
         flush_verbatim("The first line needs to start with %, \
            followed by the language and style to be used for highlighting, \
            separated by ;. \nE.g. \"% cpp; default\"")
         while line != "<EOF>":
             line = tm_input ()
         continue

    lang, style = map(lambda x: x.strip(),line.strip()[1:].split(";",2))
    if not(style in get_all_styles()):
        flush_verbatim("Selected style is not supported")
        while line != "<EOF>":
            line = tm_input ()
        continue

    lines = []
    while line != "<EOF>":
        line = tm_input ()
        if line == '':
            continue
        lines.append(line)
    code = '\n'.join(lines[:-1])
    texmacs = highlight(code, get_lexer_by_name(lang), \
        TexmacsFormatter(style=style)).replace("\n","\n\n").replace(" ","\ ")

    flush_any ("texmacs:" + texmacs)

from pygments.formatter import Formatter

# debug = False

class TeXmacsFormatter(Formatter):

    def __init__(self, **options):
        Formatter.__init__(self, **options)

        # create a dict of (start, end) tuples that wrap the
        # value of a token so that we can use it in the format
        # method later
        self.styles = {}
        self.styles_multiline = {}
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

        #If newlines are inside tags it seems the format
        # <\with|color|...> ... </with> should be used

        for token, style in self.style:
            start = end = ''
            # a style item is a tuple in the following form:
            # colors are readily specified in hex: 'RRGGBB'
            if style['color']:
                start += '<\\with|color|#%s>' % style['color']
                end = '</with>' + end
            if style['bold']:
                start += '<\\with|font-series|bold>'
                end = '</with>' + end
            if style['italic']:
                start += '<\\with|font-shape|italic>'
                end = '</with>' + end
            if style['underline']:
                start += '<\\underline>'
                end = '</underline>' + end
            self.styles_multiline[token] = (start, end)

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
            elif c == '\n':
                serialization += "\n\n"
            elif c == " ":
                serialization += "\ "
            else:
                serialization += c
        return serialization

    def output(self, value, type, outfile):
        stylebegin, styleend = self.styles[type]
#        if value.strip() == '':
            # outstring = self.serialize(value)
            # if debug: print("writing: \"" + outstring + "\"")
#            outfile.write(outstring)
        # else:
        # \n is not necessarily the last token!
        if '\n' in value:
            lines = value.split('\n')
            outstring = stylebegin + self.serialize(lines[0]) + styleend + "\n\n"
            # if debug: print("writing [0]: \"" + outstring + "\"")
            outfile.write(outstring)
            for line in lines[1:-1]:
                if line == '':
                    outfile.write("\;\n\n")
                else:
                    outstring = stylebegin + self.serialize(line) + styleend + "\n\n"
                    # if debug: print("writing [:-1]: \"" + outstring + "\"")
                    outfile.write(outstring)
            outstring = stylebegin + self.serialize(lines[-1]) + styleend
            # if debug: print("writing [-1]: \"" + outstring + "\"")
            outfile.write(outstring)
        else:
            outstring = stylebegin + self.serialize(value) + styleend
            # if debug: print("writing3: \"" + outstring + "\"")
            outfile.write(outstring)
        

    def format(self, tokensource, outfile):
        # lastval is a string we use for caching
        # because it's possible that a lexer yields a number
        # of consecutive tokens with the same token type.
        # to minimize the size of the generated texmacs markup we
        # try to join the values of same-type tokens here
        lastval = ''
        lasttype = None

        # It does not seem possible to have a newline ending a <\with> </with> tag.
        # E.g.
        # <\with|color|#408080>//test
        #
        #</with>test
        # does not result in a newline. Move the newline outside of the tag.

        # wrap the whole output with <verbatim-code|...>
        outfile.write('<\\verbatim-code>\n')

        for ttype, value in tokensource:
            # if debug: print("ttype: \"" + str(ttype) + "\"")
            # if debug: print("value: \"" + value + "\"")
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
                    self.output(lastval, lasttype, outfile)
                # set lastval/lasttype to current values
                lastval = value
                lasttype = ttype

        # if something is left in the buffer, write it to the
        # output file, then close the opened <verbatim|...> tag
        if lastval:
            self.output(lastval, lasttype, outfile)
        outfile.write('</verbatim-code>')

"""Asciitable: an extensible ASCII table reader and writer.

latex.py:
  Classes to read and write LaTeX tables

:Copyright: Smithsonian Astrophysical Observatory (2011)
:Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)
"""

## 
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Smithsonian Astrophysical Observatory nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
## 
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS  
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import asciitable.core as core

latexdicts ={'AA':  {'tabletype': 'table',
                 'header_start': r'\hline \hline', 'header_end': r'\hline',
                 'data_end': r'\hline'},
             'doublelines': {'tabletype': 'table', 
                 'header_start': r'\hline \hline', 'header_end': r'\hline\hline',
                 'data_end': r'\hline\hline'},
             'template': {'tabletype': 'tabletype', 'caption': 'caption',
                 'col_align': 'col_align', 'preamble': 'preamble', 'header_start': 'header_start',
                 'header_end': 'header_end', 'data_start': 'data_start',
                 'data_end': 'data_end', 'tablefoot': 'tablefoot'}
            }

def add_dictval_to_list(adict, key, alist):
    '''add a value from a dictionary to a list
   
    :param adict: dictionary
    :param key: key of value
    :param list: list where value should be added
    '''
    if key in adict.keys():
        if type(adict[key]) == str:
            alist.append(adict[key])
        else:
            alist.extend(adict[key])

def find_latex_line(lines, latex):
    '''Find the first line which matches a patters
    
    :param lines: list of strings
    :param latex: search pattern
    :returns: line number or None, if no match was found
    '''
    re_string = re.compile(latex.replace('\\', '\\\\'))
    for i,line in enumerate(lines):
        if re_string.match(line):
            return i
    else:
        return None


class LatexHeader(core.BaseHeader):
    header_start = r'\begin{tabular}'
    
    def start_line(self, lines):
        line = find_latex_line(lines, self.header_start)
        if line:
            return line + 1
        else:
            return None
    
    def write(self, lines):
        if not 'col_align' in self.latex.keys():
            self.latex['col_align'] = len(self.cols) * 'c'

        lines.append(r'\begin{' + self.latex['tabletype'] + r'}')
        add_dictval_to_list(self.latex, 'preamble', lines)
        if 'caption' in self.latex.keys():
            lines.append(r'\caption{' + self.latex['caption'] +'}')
        lines.append(self.header_start + r'{' + self.latex['col_align'] + r'}')
        add_dictval_to_list(self.latex, 'header_start', lines)
        lines.append(self.splitter.join([x.name for x in self.cols]))
        add_dictval_to_list(self.latex, 'header_end', lines)
                

    
class LatexData(core.BaseData):
    data_start = None
    data_end = r'\end{tabular}'
    
    def start_line(self, lines):
        if self.data_start:
            return find_latex_line(lines, self.data_start)
        else:
            return self.header.start_line(lines) + 1
    
    def end_line(self, lines):
        if self.data_end:
            return find_latex_line(lines, self.data_end)
        else:
            return None

    def write(self, lines):
        add_dictval_to_list(self.latex, 'data_start', lines)
        core.BaseData.write(self, lines)
        add_dictval_to_list(self.latex, 'data_end', lines)
        lines.append(self.data_end)
        add_dictval_to_list(self.latex, 'tablefoot', lines)
        lines.append(r'\end{' + self.latex['tabletype'] + '}')



class LatexSplitter(core.BaseSplitter):

    delimiter = '&'

    def process_line(self, line):
        """Remove whitespace at the beginning or end of line. Also remove
        \\ at end of line"""
        line = line.split('%')[0]
        line = line.strip()
        if line[-2:] ==r'\\':
            line = line.strip(r'\\')
        else:
            raise core.InconsistentTableError(r'Lines in LaTeX table have to end with \\')
        return line
    
    def process_val(self, val):
        """Remove whitespace and {} at the beginning or end of value."""
        val = val.strip()
        if (val[0] == '{') and (val[-1] == '}'):
            val = val[1:-1]
        return val
    
    def join(self, vals):
        '''Join values together and add a few extra spaces for readability'''
        delimiter = ' ' + self.delimiter + ' '
        return delimiter.join(str(x) for x in vals) + r' \\'

extra_latex_pars = ('latexdict', 'caption', 'col_align', 'ignore_latex_commands')

class Latex(core.BaseReader):
    '''Writes (and reads) LaTeX tables
    
    This class implements some LaTeX specific commands.
    Its main purpose is to write out a table in a form that LaTeX
    can compile. It is beyond the scope to implement every possible 
    LaTeX command, instead the focus is to generate a simple, yet 
    syntactically valid LaTeX tables.
    This class can also read simple LaTeX tables (one line per table row,
    no \multicolumn or similar constructs), spcifically, it can read the 
    tables it writes.
    '''
    # some latex commands should be treated as comments (i.e. ignored)
    # when reading a table 
    ignore_latex_commands = ['hline', 'vspace', 'tableline']
    
    def __init__(self, **kwargs):
        core.BaseReader.__init__(self)
        self.header = LatexHeader()
        self.data = LatexData()
        self.header.comment = '%|' + '|'.join([r'\\' + command for command in self.ignore_latex_commands])
        self.header.splitter = LatexSplitter()        
        self.data.splitter = LatexSplitter()
        self.data.header = self.header
        self.header.data = self.data
        self.latex = {}
        self.latex['tabletype'] = 'table'
        # The latex dict drives the format of the table and needs to be shared
        # with data and header
        self.header.latex = self.latex
        self.data.latex = self.latex

        if 'latexdict' in kwargs:
            self.latex.update(kwargs['latexdict'])
        if 'caption' in kwargs:
            self.latex['caption'] = kwargs['caption']
        if 'col_align' in kwargs:
            self.latex['col_align'] = kwargs['col_align']
        if 'ignore_latex_commands' in kwargs:
            self.ignore_latex_commands = kwargs['ignore_latex_commands']

        self.header.comment = '%|' + '|'.join([r'\\' + command for command in self.ignore_latex_commands])
        self.data.comment = self.header.comment

        for arg in kwargs:
            if arg not in extra_latex_pars:
                raise ValueError(arg + 'is not a keyword for asciitable.Latex')

    def write(self, table=None):
        self.header.start_line = None
        self.data.start_line = None
        return core.BaseReader.write(self, table=table)


LatexReader = Latex



class AASTexHeader(core.BaseHeader):
    header_start = r'\tablehead'

    def start_line(self, lines):
        return find_latex_line(lines, r'\tablehead')

    def write(self, lines):
        if not 'col_align' in self.latex.keys():
            self.latex['col_align'] = len(self.cols) * 'c'

        lines.append(r'\begin{' + self.latex['tabletype'] + r'}{' + self.latex['col_align'] + r'}')
        add_dictval_to_list(self.latex, 'preamble', lines)
        if 'caption' in self.latex.keys():
            lines.append(r'\tablecaption{' + self.latex['caption'] +'}')
        tablehead = ' & '.join([r'\colhead{' + x.name + '}' for x in self.cols])
        lines.append(r'\tablehead{' + tablehead + '}')


class AASTexData(LatexData):
    data_start = r'\startdata'
    data_end = r'\enddata'

    def start_line(self, lines):
        return find_latex_line(lines, self.data_start) + 1

    def write(self, lines):
        lines.append(self.data_start)
        core.BaseData.write(self, lines)
        lines.append(self.data_end)
        add_dictval_to_list(self.latex, 'tablefoot', lines)
        lines.append(r'\end{' + self.latex['tabletype'] + r'}')

class AASTexHeaderSplitter(LatexSplitter):

    def process_line(self, line):
        """extract column names from tablehead
        """
        line = line.split('%')[0]
        line = line.replace(r'\tablehead','')
        line = line.strip()
        if (line[0] =='{') and (line[-1] == '}'):
            line = line[1:-1]
        else:
            raise core.InconsistentTableError(r'\tablehead is missing {}')
        return line.replace(r'\colhead','')

    def join(self, vals):
        return ' & '.join([r'\colhead{' + str(x) + '}' for x in vals])



class AASTex(Latex):
    '''Writes (and reads) AASTeX tables
    
    This class implements some AASTeX specific commands.
    AASTeX is used for the AAS (American Astronomical Society)
    publications like ApJ, ApJL and AJ.
    Writes (and reads) LaTeX tables
    
    This class implents some LaTeX specific commands.
    Its main purpose is to write out a table in a form that LaTeX
    can compile. It is beyond the scope to implement every possible 
    LaTeX command, instead the focus is to generate a simple, yet 
    syntactically valid LaTeX tables.
    This class can also read simple LaTeX tables (one line per table row,
    no \multicolumn or similar constructs), spcifically, it can read the 
    tables it writes.
    '''
    # some latex commands should be treated as comments (i.e. ignored)
    # when reading a table 
    ignore_latex_commands = ['hline', 'vspace', 'tableline']

    def __init__(self, **kwargs):
        Latex.__init__(self)
        self.header = AASTexHeader()
        self.data = AASTexData()
        self.header.comment = '%|' + '|'.join([r'\\' + command for command in self.ignore_latex_commands])
        self.header.splitter = AASTexHeaderSplitter()
        self.data.splitter = LatexSplitter()
        self.data.comment = self.header.comment
        self.data.header = self.header
        self.header.data = self.data
        self.latex['tabletype'] = 'deluxetable'
        # The latex dict drives the format of the table and needs to be shared
        # with data and header
        self.header.latex = self.latex
        self.data.latex = self.latex

AASTexReader = AASTex


# make these lines in test caes and in documentation

#dat = {'cola':[1,2], 'colb':[3,4]}
#asciitable.write(dat, sys.stdout, Writer = asciitable.Latex, tabletype = 'AA', caption = 'Mag values \\label{tab1}', latexdict = {'preamble':'\\begin{center}', 'tablefoot':'\\end{center}', 'data_end':['\\hline','\\hline']}, col_align='|ll|')
#\begin{table}
#\begin{center}
#\caption{Mag values \label{tab1}}
#\begin{tabular}{|ll|}
#\hline \hline
#cola & colb \\
#\hline
#1 & 3 \\
#2 & 4 \\
#\hline
#\hline
#\end{tabular}
#\end{center}
#\end{table}


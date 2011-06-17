import re
import asciitable.core as core

class LatexHeader(core.BaseHeader):
    header_begin = r'\begin{tabular}'
    caption = None
    col_align = None
    
    def start_line(self, lines):
        re_string = re.compile(self.header_begin.replace('\\', '\\\\'))
        for i, line in enumerate(lines):
            if re_string.match(line):
                # This construct breaks at the \begin{tabular} line, i.e. we
                # need to add 1 to i after the loop
                return i+1
        else:
            #No begin_table found, so let's try if we are reading the bare inner bit
            return None
    
    def write(self, lines, table):
        lines.append(r'\begin{' + self.tabletype + r'}')
        if self.caption:
            lines.append(self.caption)
        if not self.col_align:
            self.col_align = len(table.cols) * 'c'
        lines.append(self.header_begin + r'{' + self.col_align + r'}')
        lines.append(r'\hline')
        lines.append(r'\hline')
        lines.append(self.splitter.join([x.name for x in table.cols]))
        lines.append(r'\hline')
    
class LatexData(core.BaseData):
    data_end = r'\end{tabular}'
    
    def start_line(self, lines):
        return self.header.start_line(lines) + 1
    
    def end_line(self, lines):
        re_string = re.compile(self.data_end.replace('\\', '\\\\'))
        for i,line in enumerate(lines):
            if re_string.match(line):
                # This construct breaks at the \begin{tabular} line, i.e. we
                # need to add 1 to i after the loop
                return i
        else:
            #No begin_table found, so let's try if we are reading the bare inner bit
            return None
    
    def write(self, lines, table):
        lines.append(r'\hline')
        core.BaseData.write(self, lines, table)
        lines.append(r'\hline')
        lines.append(self.data_end)
        lines.append(r'\end{' + self.header.tabletype + '}')

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
            raise InconsistentTableError(r'Lines in LaTeX table have to end with \\')
        return line
        
    def join(self, vals):
        if self.delimiter is '&':
            # '&' is standard for Latex
            # add some white spaces here to improve readability
            delimiter = ' & '
        else:
            delimiter = self.delimiter
        return delimiter.join(str(x) for x in vals) + r' \\'


class Latex(core.BaseReader):
    '''Writes (and reads) LaTeX tables
    
    This class implents some LaTeX specific commands.
    Its main purpose is to write out a table in a form that LaTeX
    can compile. It is beyond the scope to implenent every possible 
    LaTeX command, instead the focus is to generate a simple, yet 
    syntactically valid LaTeX table.
    This class can read LaTeX the tables it writes and others of similar format,
    i.e. exactly one row of data per line, no multicolumns, no footnotes. 
    '''
    # some latex commands should be treated as comments (i.e. ignored)
    # when reading a table 
    ignore_latex_commands = ['hline', 'vspace', 'caption']
    special_writer_pars = ('caption', 'tabletype', 'col_align')
    
    def __init__(self, **kwargs):
        core.BaseReader.__init__(self)
        self.header = LatexHeader()
        self.data = LatexData()
        self.header.comment = '%|' + '|'.join([r'\\' + command for command in self.ignore_latex_commands])
        self.header.splitter = LatexSplitter()        
        self.data.splitter = LatexSplitter()
        self.data.comment = self.header.comment
        self.data.header = self.header
        self.header.data = self.data
        if 'tabletype' in kwargs:
            self.header.tabletype = kwargs['delimiter']
        else:
            self.header.tabletype = 'table'
        if 'caption' in kwargs:
            self.header.caption = kwargs['caption']
        if 'col_align' in kwargs:
            self.header.col_align = kwargs['col_align']
    def write(self, table=None):
        self.header.start_line = None
        self.data.start_line = None

        return core.BaseReader.write(self, table=table)

LatexReader = Latex

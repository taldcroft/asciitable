from asciitable import *

class LatexHeader(BaseHeader):
    
    header_begin = r'\begin{tabular}'
    caption = None
    col_align = None
    
    def start_line(self, lines):
        re_string = re.compile(self.header_begin.replace('\\', '\\\\'))
        for i, line in enumerate(lines):
            if re_string.match(line):
                # This construct breaks at the \begin{tabular} line, i.e. we need to add 1 to i after the loop 
                return i + 1
        else:
            #No begin_table found, so let's try if we are reading the bare inner bit
            return None
    
    def write(self, lines, table):
        lines.append(r'\begin{' + self.tabletype + r'}')
        if self.caption:
            lines.append(self.caption)
        if not self.col_align:
            self.col_align = r'{' + len(table.cols) * 'c' + r'}'
        lines.append(self.header_begin + self.col_align)
        lines.append(r'\hline')
        lines.append(r'\hline')
        lines.append(self.splitter.join([x.name for x in table.cols]))
        lines.append(r'\hline')
    
class LatexData(BaseData):
    data_end = r'\end{tabular}'
    
    def start_line(self, lines):
        return self.header.start_line(lines) + 1
    
    def end_line(self, lines):
        re_string = re.compile(self.data_end.replace('\\', '\\\\'))
        for i,line in enumerate(lines):
            if re_string.match(line):
                # This construct breaks at the \begin{tabular} line, i.e. we need to add 1 to i after the loop 
                return i
        else:
            #No begin_table found, so let's try if we are reading the bare inner bit
            return None
    
    def write(self, lines, table):
        lines.append(r'\hline')
        BaseData.write(self, lines, table)
        lines.append(r'\hline')
        lines.append(self.data_end)
        lines.append(r'\end{' + self.header.tabletype + '}')

class LatexSplitter(BaseSplitter):

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


class LaTeX(BaseReader):
    
    # some latex commands should be treated as comments (i.e. ignored)
    # when reading a table 
    ignore_latex_commands = ['hline', 'vspace']
    
    def __init__(self):
        BaseReader.__init__(self)
        self.header = LatexHeader()
        self.data = LatexData()
        self.header.comment = '%|' + '|'.join([r'\\' + command for command in self.ignore_latex_commands])
        self.header.splitter = LatexSplitter()
        self.header.tabletype = 'table'
        self.data.splitter = LatexSplitter()
        self.data.comment = self.header.comment
        self.data.header = self.header
        self.header.data = self.data

    
    def write(self, table=None):
        self.header.start_line = None
        self.data.start_line = None
        return BaseReader.write(self, table = table)


import re
import asciitable.core as core

def add_dictval_to_list(adict, key, alist):
    if key in adict.keys():
        if type(adict[key]) == str:
            alist.append(adict[key])
        else:
            alist.extend(adict[key])

def find_latex_line(lines, latex):
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

        if self.latex['tabletype'] == 'deluxetable':
            lines.append(r'\begin{' + self.latex['tabletype'] + r'}{' + self.latex['col_align'] + r'}')
            add_dictval_to_list(self.latex, 'preamble', lines)
            if 'caption' in self.latex.keys():
                lines.append(r'\tablecaption{' + self.latex['caption'] +'}')
            tablehead = ' & '.join([r'\colhead{' + x.name + '}' for x in self.cols])
            lines.append(r'\tablehead{' + tablehead + '}')
        else:
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
        if self.latex['tabletype'] == 'deluxetable':
            lines.append(self.data_start)
            core.BaseData.write(self, lines)
            lines.append(self.data_end)
            add_dictval_to_list(self.latex, 'tablefoot', lines)
            lines.append(r'\begin{' + self.latex['tabletype'] + r'}')
        else:
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
        if self.delimiter is '&':
            # '&' is standard for Latex
            # add some white spaces here to improve readability
            delimiter = ' & '
        else:
            delimiter = self.delimiter
        return delimiter.join(str(x) for x in vals) + r' \\'

class AASTexHeaderSplitter(LatexSplitter):
    
    def process_line(self, line):
        """
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



class Latex(core.BaseReader):
    '''Writes (and reads) LaTeX tables
    
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
        core.BaseReader.__init__(self)
        self.header = LatexHeader()
        self.data = LatexData()
        self.header.comment = '%|' + '|'.join([r'\\' + command for command in self.ignore_latex_commands])
        self.header.splitter = LatexSplitter()        
        self.data.splitter = LatexSplitter()
        self.data.comment = self.header.comment
        self.data.header = self.header
        self.header.data = self.data
        self.latex = {}
        self.latex['tabletype'] = 'table'
        # The latex dict drives the format of the table and needs to be shared
        # with data and header
        self.header.latex = self.latex
        self.data.latex = self.latex
        if 'tabletype' in kwargs:
            self.latex['tabletype'] = kwargs['tabletype']
            if kwargs['tabletype'] == 'deluxetable':
                self.header.start_line = lambda lines: find_latex_line(lines, r'\tablehead')
                self.header.splitter = AASTexHeaderSplitter()
                self.data.data_start = r'\startdata'
                self.data.start_line = lambda lines: find_latex_line(lines, self.data.data_start) + 1
                self.data.data_end = r'\enddata'
            if kwargs['tabletype'] == 'AA':
                self.latex.update({'tabletype': 'table', 'header_start': r'\hline \hline', 'header_end': r'\hline', 'data_end': r'\hline'})
            
        if 'latexdict' in kwargs:
            self.latex.update(kwargs['latexdict'])
        if 'caption' in kwargs:
            self.latex['caption'] = kwargs['caption']
        if 'col_align' in kwargs:
            self.latex['col_align'] = kwargs['col_align']

    def write(self, table=None):
        header_start_line_old = self.header.start_line
        data_start_line_old = self.data.start_line
        self.header.start_line = None
        self.data.start_line = None
        written = core.BaseReader.write(self, table=table)
        self.header.start_line = header_start_line_old
        self.data.start_line = data_start_line_old
        return written
        

LatexReader = Latex

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


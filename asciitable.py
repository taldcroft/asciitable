import os
import sys
import re
import numpy

class Column(object):
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.str_vals = []

class Splitter(object):
    delimiter = None
    autostrip = True

    def __call__(self, line):
        vals = line.split(self.delimiter)
        if self.autostrip:
            vals = [x.strip() for x in vals]
        return vals

class TableData(object):
    skip_header = 1
    skip_footer = 0
    comments = '#'
    splitter = Splitter()
    
    def get_str_vals(self, lines, cols):
        re_comment = re.compile(r'\s*' + self.comments)
        data_lines = [x for x in lines if not re_comment.match(x)]
        for line in data_lines[slice(self.skip_header, -self.skip_footer or None)]:
            str_vals = self.splitter(line)
            try:
                for col in cols:
                    col.str_vals.append(str_vals[col.index])
            except IndexError:
                raise ValueError('Line %d has too few columns of data' % (i+1))

class TableHeader(object):
    skip_header = 0
    comments = '#'
    splitter = Splitter()
    include_names = None
    exclude_names = None
    names = None

    def get_cols(self, lines):
        if self.names is None:
            n_match = 0
            re_comment = re.compile(r'\s*' + self.comments)
            for line in lines:
                if not re_comment.match(line):
                    if n_match == self.skip_header:
                        break
                    else:
                        n_match += 1
            else: # No header line matching
                raise ValueError('No header line found')
            self.names = self.splitter(line)
        
        names = set(self.names)
        if self.include_names is not None:
            names.intesection_update(self.include_names)
        if self.exclude_names is not None:
            names.difference_update(self.exclude_names)
            
        return [Column(name=x, index=i) for i, x in enumerate(self.names) if x in names]

class Inputter(object):
    def get_lines(self, table):
        """Get the lines from the ``table`` input which can be:
        * A string: either a filename or a full data table (os.linesep separated)
        * A list of lines
        """
        try:
            table + ''
            if os.linesep not in table:
                with open(table, 'r') as f:
                    table = f.read()
            return table.splitlines()
        except TypeError:
            try:
                # See if table supports indexing, slicing, and iteration
                table[0]
                table[0:1]
                iter(table)
                return table
            except TypeError:
                raise TypeError('Input "table" must be a string (filename or data) or an iterable')

    def process_lines(self, lines):
        """Override this method if something has to be done to convert raw input lines to the
        table rows.  E.g. account for continuation characters if a row is split into lines."""
        return lines

    def __call__(self, table):
        lines = self.get_lines(table)
        return self.process_lines(lines)

class Outputter(object):
    converters = dict()
    default_converter = [lambda vals: [int(x) for x in vals],
                         lambda vals: [float(x) for x in vals],
                         lambda vals: vals]

    def __call__(self, cols):
        self.convert_vals(cols)
        return dict((x.name, x) for x in cols)

    def convert_vals(self, cols):
        for col in cols:
            col.converters = self.converters.get(col.name, self.default_converter)[:]
            while not hasattr(col, 'data'):
                try:
                    col.data = col.converters[0](col.str_vals)
                except (TypeError, ValueError):
                    if col.converters:
                        col.converters.pop(0)
                    else:
                        raise ValueError('Column failed to convert')

class NumpyArrayOutputter(Outputter):
    default_converter = [lambda vals: numpy.array(vals, numpy.int),
                         lambda vals: numpy.array(vals, numpy.float),
                         lambda vals: numpy.array(vals, numpy.str)]

    def __call__(self, cols):
        self.convert_vals(cols)
        return numpy.rec.fromarrays([x.data for x in cols], names=[x.name for x in cols])

class AsciiTable(object):
    header_class = TableHeader
    data_class = TableData
    inputter_class = Inputter
    outputter_class = NumpyArrayOutputter

    def __init__(self, table):
        self.table = table
        self.header = self.__class__.header_class()
        self.data = self.__class__.data_class()
        self.inputter = self.__class__.inputter_class()
        self.outputter = self.__class__.outputter_class()

    def read(self):
        self.lines = self.inputter(self.table)
        self.cols = self.header.get_cols(self.lines)
        self.data.get_str_vals(self.lines, self.cols)
        return self.outputter(self.cols)

testlines = ['col1 col2 col3',
             '1   2 3.4',
             '2.3 4 hi']

testtable = """#
col1 col2 col3
1   2 3.4
2.3 4 hi
"""
        
a = """
fname : file or str [Inputter]

 File or filename to read. If the filename extension is gz or bz2, the file is
 first decompressed.

dtype : dtype, optional [Outputter]

 Data type of the resulting array. If None, the dtypes will be determined by
 the contents of each column, individually.

comments : str, optional [Header, Data]

 The character used to indicate the start of a comment. All the characters
 occurring on a line after a comment are discarded

delimiter : str, int, or sequence, optional [Splitter]

 The string used to separate values. By default, any consecutive whitespaces
 act as delimiter. An integer or sequence of integers can also be provided as
 width(s) of each field.

skip_header : int, optional [Header, Data]

 The numbers of lines to skip at the beginning of the file.

skip_footer : int, optional [Data]

 The numbers of lines to skip at the end of the file

converters : variable or None, optional [Outputter]

 The set of functions that convert the data of a column to a value. The
 converters can also be used to provide a default value for missing data:
 converters = {3: lambda s: float(s or 0)}.

missing_values : variable or None, optional [?]

 The set of strings corresponding to missing data.

filling_values : variable or None, optional [?]

 The set of values to be used as default when the data are missing.

usecols : sequence or None, optional [Header]

 Which columns to read, with 0 being the first. For example, usecols = (1, 4,
 5) will extract the 2nd, 5th and 6th columns.

names : {None, True, str, sequence}, optional [Header]

 If names is True, the field names are read from the first valid line after the
 first skiprows lines. If names is a sequence or a single-string of
 comma-separated names, the names will be used to define the field names in a
 structured dtype. If names is None, the names of the dtype fields will be
 used, if any.

excludelist : sequence, optional [Header]

 A list of names to exclude. 

deletechars : str, optional [not needed]

 A string combining invalid characters that must be deleted from the names.

defaultfmt : str, optional [Header]

 A format used to define default field names, such as f%i or f_%02i.

autostrip : bool, optional [Splitter]

 Whether to automatically strip white spaces from the variables.

case_sensitive : {True, False, upper, lower}, optional [Header]

 If True, field names are case sensitive. If False or upper, field names are
 converted to upper case. If lower, field names are converted to lower case.

unpack : bool, optional [Outputter]

 If True, the returned array is transposed, so that arguments may be unpacked
 using x, y, z = loadtxt(...)

usemask : bool, optional [Outputter]

 If True, return a masked array. If False, return a regular array.

invalid_raise : bool, optional [skip]

 If True, an exception is raised if an inconsistency is detected in the number
 of columns. If False, a warning is emitted and the offending lines are
 skipped.
"""

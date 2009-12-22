import os
import sys
import re
import csv

try:
    import numpy
except ImportError:
    pass

class Column(object):
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.str_vals = []

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
            lines = table.splitlines()
        except TypeError:
            try:
                # See if table supports indexing, slicing, and iteration
                table[0]
                table[0:1]
                iter(table)
                lines = table
            except TypeError:
                raise TypeError('Input "table" must be a string (filename or data) or an iterable')

        return self.process_lines(lines)

    def process_lines(self, lines):
        """Override this method if something has to be done to convert raw input lines to the
        table rows.  E.g. account for continuation characters if a row is split into lines or
        remove blank lines."""
        return lines

class Splitter(object):
    """Use python csv to do the splitting"""
    autostrip = True
    delimiter = ' '
    quotechar = '"'
    doublequote = True
    escapechar = None
    quoting = csv.QUOTE_MINIMAL

    def __call__(self, lines):
        if self.autostrip:
            lines = (x.strip() for x in lines)
        return csv.reader(lines,
                          delimiter =self.delimiter,
                            doublequote = self.doublequote,
                            escapechar =self.escapechar,
                            quotechar = self.quotechar,
                            quoting = self.quoting,
                            skipinitialspace = self.autostrip
                            )
    
class SplitterWhiteSpace(object):
    """Example of a simple custom splitter"""
    delimiter = None
    autostrip = True

    def __call__(self, lines):
        vals = line.split(self.delimiter)
        if self.autostrip:
            vals = [x.strip() for x in vals]
        yield vals

class TableData(object):
    """Table data reader

    :param start_line: None, int, or a function of ``lines`` that returns None or int
    :param end_line: None, int, or a function of ``lines`` that returns None or int

    """
    start_line = 1
    end_line = None
    comment = r'\s*#'
    splitter = Splitter()
    
    def get_str_vals(self, lines):
        if not hasattr(self, 'data_lines'):
            re_comment = re.compile(self.comment)
            data_lines = [x for x in lines if not re_comment.match(x)]

            if hasattr(self.start_line, '__call__'):
                start_line = self.start_line(lines)
            else:
                start_line = self.start_line

            if hasattr(self.end_line, '__call__'):
                end_line = self.end_line(lines)
            else:
                end_line = self.end_line

            self.data_lines = data_lines[slice(start_line, self.end_line)]
        return self.splitter(self.data_lines)

    def set_cols(self, cols, str_vals, n_data_cols):
        if len(cols) != n_data_cols:
            raise ValueError('Table columns inconsistent with first data line')
        for col in cols:
            col.str_vals.append(str_vals[col.index])

class TableHeader(object):
    auto_format = '%d'
    start_line = 0
    comment = '#'
    splitter = Splitter()
    include_names = None
    exclude_names = None
    names = None

    def get_cols(self, lines, n_data_cols):
        if hasattr(self.start_line, '__call__'):
            start_line = self.start_line(lines)
        else:
            start_line = self.start_line

        if start_line is None:
            # No header line so auto-generate names from n_data_cols
            self.names = [self.auto_format.format(i) for i in range(n_data_cols)]

        elif self.names is None:
            # No column names supplied so read them from header line in table.
            n_match = 0
            re_comment = re.compile(r'\s*' + self.comment)
            for line in lines:
                if not re_comment.match(line):
                    if n_match == start_line:
                        break
                    else:
                        n_match += 1
            else: # No header line matching
                raise ValueError('No header line found in table')
            self.names = self.splitter([line]).next()
        
        names = set(self.names)
        if self.include_names is not None:
            names.intesection_update(self.include_names)
        if self.exclude_names is not None:
            names.difference_update(self.exclude_names)
            
        return [Column(name=x, index=i) for i, x in enumerate(self.names) if x in names]

class Outputter(object):
    converters = dict()
    default_converter = [lambda vals: [int(x) for x in vals],
                         lambda vals: [float(x) for x in vals],
                         lambda vals: vals]

    def convert_vals(self, cols):
        print self.converters
        for col in cols:
            converters = self.converters.get(col.name, self.default_converter)
            # Make a copy of converters and make sure converters it is a list
            try:
                col.converters = converters[:]
            except TypeError:
                col.converters = [converters]

            while not hasattr(col, 'data'):
                try:
                    col.data = col.converters[0](col.str_vals)
                except (TypeError, ValueError):
                    if col.converters:
                        col.converters.pop(0)
                    else:
                        raise ValueError('Column failed to convert')

    def __call__(self, cols):
        self.convert_vals(cols)
        return dict((x.name, x) for x in cols)

def convert_numpy(numpy_type):
    return lambda vals: numpy.array(vals, getattr(numpy, numpy_type))

class NumpyOutputter(Outputter):
    default_converter = [convert_numpy('int'),
                         convert_numpy('float'),
                         convert_numpy('str')]

    def __call__(self, cols):
        self.convert_vals(cols)
        return numpy.rec.fromarrays([x.data for x in cols], names=[x.name for x in cols])

class Table(object):
    header_class = TableHeader
    data_class = TableData
    inputter_class = Inputter
    outputter_class = Outputter

    def __init__(self):
        self.header = self.__class__.header_class()
        self.data = self.__class__.data_class()
        self.inputter = self.__class__.inputter_class()
        self.outputter = self.__class__.outputter_class()

    def read(self, table):
        lines = self.inputter.get_lines(table)
        n_data_cols = len(self.data.get_str_vals(lines).next())
        cols = self.header.get_cols(lines, n_data_cols)

        set_cols = self.data.set_cols   # reduce object lookup within inner loop
        for str_vals in self.data.get_str_vals(lines):
            set_cols(cols, str_vals, n_data_cols)
        return self.outputter(cols)


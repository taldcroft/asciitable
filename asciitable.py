""" An extensible ASCII table reader.

:Copyright: Smithsonian Astrophysical Observatory (2010)
:Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)
"""
## Copyright (c) 2010, Smithsonian Astrophysical Observatory
## All rights reserved.
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

__version__ = '0.6.0'

import os
import sys
import re
import csv
import itertools

try:
    import numpy
    has_numpy = True
except ImportError:
    has_numpy = False

class InconsistentTableError(ValueError):
    pass

# Python 3 compatibility tweaks.  Should work back through 2.4.
try:
    import cStringIO as io
except ImportError:
    import io

try:
    next
except NameError:
    next = lambda x: x.next()

try:
    izip = itertools.izip
except AttributeError:
    izip = zip

# Python 2.4 comptability: any() function is built-in only for 2.5 onward
try:
    any
except NameError:
    def any(vals):
        for val in vals:
            if val:
                return True
        return False

# Default setting for guess parameter in read()
GUESS = True

class Keyword(object):
    """Table keyword"""
    def __init__(self, name, value, units=None, comment=None, format=None):
        self.name = name
        self.value = value
        self.units = units
        self.comment = comment
        self.format = format

class Column(object):
    """Table column.

    The key attributes of a Column object are:

    * **name** : column name
    * **index** : column index (first column has index=0, second has index=1, etc)
    * **str_vals** : list of column values as strings
    * **data** : list of converted column values
    """
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.str_vals = []
        self.fill_values = {}

class BaseInputter(object):
    """Get the lines from the table input and return a list of lines.  The input table can be one of:

    * File name
    * String (newline separated) with all header and data lines (must have at least 2 lines)
    * File-like object with read() method
    * List of strings
    """
    def get_lines(self, table):
        """Get the lines from the ``table`` input.
        
        :param table: table input
        :returns: list of lines
        """
        try:
            if hasattr(table, 'read'):
                table = table.read()
            elif '\n' not in table and '\r' not in table + '':
                table = open(table, 'r').read()
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
        """Process lines for subsequent use.  In the default case do nothing.
        This routine is not generally intended for removing comment lines or
        stripping whitespace.  These are done (if needed) in the header and
        data line processing.

        Override this method if something more has to be done to convert raw
        input lines to the table rows.  For example the
        ContinuationLinesInputter derived class accounts for continuation
        characters if a row is split into lines."""
        return lines

class BaseSplitter(object):
    """Base splitter that uses python's split method to do the work.

    This does not handle quoted values.  A key feature is the formulation of
    __call__ as a generator that returns a list of the split line values at
    each iteration.

    There are two methods that are intended to be overridden, first
    ``process_line()`` to do pre-processing on each input line before splitting
    and ``process_val()`` to do post-processing on each split string value.  By
    default these apply the string ``strip()`` function.  These can be set to
    another function via the instance attribute or be disabled entirely, for
    example::

      reader.header.splitter.process_val = lambda x: x.lstrip()
      reader.data.splitter.process_val = None
      
    :param delimiter: one-character string used to separate fields 
    """
    delimiter = None
    
    def process_line(self, line):
        """Remove whitespace at the beginning or end of line.  This is especially useful for
        whitespace-delimited files to prevent spurious columns at the beginning or end."""
        return line.strip()

    def process_val(self, val):
        """Remove whitespace at the beginning or end of value."""
        return val.strip()

    def __call__(self, lines):
        if self.process_line:
            lines = (self.process_line(x) for x in lines)
        for line in lines:
            vals = line.split(self.delimiter)
            if self.process_val:
                yield [self.process_val(x) for x in vals]
            else:
                yield vals

    def join(self, vals):
        if self.delimiter is None:
            delimiter = ' '
        else:
            delimiter = self.delimiter
        return delimiter.join(str(x) for x in vals)
    

class DefaultSplitter(BaseSplitter):
    """Default class to split strings into columns using python csv.  The class
    attributes are taken from the csv Dialect class.

    Typical usage::

      # lines = ..
      splitter = asciitable.DefaultSplitter()
      for col_vals in splitter(lines):
          for col_val in col_vals:
               ...

    :param delimiter: one-character string used to separate fields.
    :param doublequote:  control how instances of *quotechar* in a field are quoted
    :param escapechar: character to remove special meaning from following character
    :param quotechar: one-character stringto quote fields containing special characters
    :param quoting: control when quotes are recognised by the reader
    :param skipinitialspace: ignore whitespace immediately following the delimiter
    """
    delimiter = ' '
    quotechar = '"'
    doublequote = True
    escapechar = None
    quoting = csv.QUOTE_MINIMAL
    skipinitialspace = True
    
    def process_line(self, line):
        """Remove whitespace at the beginning or end of line.  This is especially useful for
        whitespace-delimited files to prevent spurious columns at the beginning or end. 
        If splitting on whitespace then replace unquoted tabs with space first"""
        if self.delimiter == '\s':
            line = _replace_tab_with_space(line, self.escapechar, self.quotechar)
        return line.strip()

    def __init__(self):
        self.csv_writer = None
        self.csv_writer_out = io.StringIO()

    def __call__(self, lines):
        """Return an iterator over the table ``lines``, where each iterator output
        is a list of the split line values.

        :param lines: list of table lines
        :returns: iterator
        """
        if self.process_line:
            lines = [self.process_line(x) for x in lines]

        if self.delimiter == '\s':
            delimiter = ' '
        else:
            delimiter = self.delimiter

        csv_reader = csv.reader(lines,
                                delimiter = delimiter,
                                doublequote = self.doublequote,
                                escapechar =self.escapechar,
                                quotechar = self.quotechar,
                                quoting = self.quoting,
                                skipinitialspace = self.skipinitialspace
                                )
        for vals in csv_reader:
            if self.process_val:
                yield [self.process_val(x) for x in vals]
            else:
                yield vals
            
    def join(self, vals):
        if self.delimiter is None:
            delimiter = ' '
        else:
            delimiter = self.delimiter

        if self.csv_writer is None:
            self.csv_writer = csv.writer(self.csv_writer_out,
                                         delimiter = self.delimiter,
                                         doublequote = self.doublequote,
                                         escapechar = self.escapechar,
                                         quotechar = self.quotechar,
                                         quoting = self.quoting,
                                         lineterminator = '',
                                         )
        self.csv_writer_out.seek(0)
        self.csv_writer_out.truncate()
        self.csv_writer.writerow(vals)        

        return self.csv_writer_out.getvalue()
    
def _replace_tab_with_space(line, escapechar, quotechar):
    """Replace tab with space within ``line`` while respecting quoted substrings"""
    newline = []
    in_quote = False
    lastchar = 'NONE'
    for char in line:
        if char == quotechar and lastchar != escapechar:
            in_quote = not in_quote
        if char == '\t' and not in_quote:
            char = ' '
        lastchar = char
        newline.append(char)
    return ''.join(newline)

def _get_line_index(line_or_func, lines):
    if hasattr(line_or_func, '__call__'):
        return line_or_func(lines)
    else:
        return line_or_func

class BaseHeader(object):
    """Base table header reader

    :param auto_format: format string for auto-generating column names
    :param start_line: None, int, or a function of ``lines`` that returns None or int
    :param comment: regular expression for comment lines
    :param splitter_class: Splitter class for splitting data lines into columns
    :param names: list of names corresponding to each data column
    :param include_names: list of names to include in output (default=None selects all names)
    :param exclude_names: list of names to exlude from output (applied after ``include_names``)
    """
    auto_format = 'col%d'
    start_line = None
    comment = None
    splitter_class = DefaultSplitter
    names = None
    include_names = None
    exclude_names = None
    write_spacer_lines = ['ASCIITABLE_WRITE_SPACER_LINE']

    def __init__(self):
        self.splitter = self.__class__.splitter_class()
       
    def get_cols(self, lines):
        """Initialize the header Column objects from the table ``lines``.

        Based on the previously set Header attributes find or create the column names.
        Sets ``self.cols`` with the list of Columns.  This list only includes the actual
        requested columns after filtering by the include_names and exclude_names
        attributes.  See ``self.names`` for the full list.

        :param lines: list of table lines
        :returns: None
        """

        start_line = _get_line_index(self.start_line, lines)
        if start_line is None:
            # No header line so auto-generate names from n_data_cols
            if self.names is None:
                # Get the data values from the first line of table data to determine n_data_cols
                try:
                    first_data_vals = next(self.data.get_str_vals())
                except StopIteration:
                    raise InconsistentTableError('No data lines found so cannot autogenerate column names')
                n_data_cols = len(first_data_vals)
                self.names = [self.auto_format % i for i in range(1, n_data_cols+1)]

        elif self.names is None:
            # No column names supplied so read them from header line in table.
            for i, line in enumerate(self.process_lines(lines)):
                if i == start_line:
                    break
            else: # No header line matching
                raise ValueError('No header line found in table')

            self.names = next(self.splitter([line]))
        
        names = set(self.names)
        if self.include_names is not None:
            names.intersection_update(self.include_names)
        if self.exclude_names is not None:
            names.difference_update(self.exclude_names)
            
        self.cols = [Column(name=x, index=i) for i, x in enumerate(self.names) if x in names]

    def process_lines(self, lines):
        """Generator to yield non-comment lines"""
        if self.comment:
            re_comment = re.compile(self.comment)
        # Yield non-comment lines
        for line in lines:
            if line and (not self.comment or not re_comment.match(line)):
                yield line

    def write(self, lines, table):
        if self.start_line is not None:
            for i, spacer_line in izip(range(self.start_line),
                                       itertools.cycle(self.write_spacer_lines)):
                lines.append(spacer_line)
            lines.append(self.splitter.join([x.name for x in table.cols]))

    @property
    def colnames(self):
        """Return the column names of the table"""
        return tuple(col.name for col in self.cols)


class BaseData(object):
    """Base table data reader.

    :param start_line: None, int, or a function of ``lines`` that returns None or int
    :param end_line: None, int, or a function of ``lines`` that returns None or int
    :param comment: Regular expression for comment lines
    :param splitter_class: Splitter class for splitting data lines into columns
    """
    start_line = None
    end_line = None
    comment = None
    splitter_class = DefaultSplitter
    write_spacer_lines = ['ASCIITABLE_WRITE_SPACER_LINE']
    formats = {}
    default_formatter = str
    fill_values = []
    fill_include_names = None
    fill_exclude_names = None
    
    def __init__(self):
        self.splitter = self.__class__.splitter_class()

    def process_lines(self, lines):
        """Strip out comment lines and blank lines from list of ``lines``

        :param lines: all lines in table
        :returns: list of lines
        """
        nonblank_lines = (x for x in lines if x.strip())
        if self.comment:
            re_comment = re.compile(self.comment)
            return [x for x in nonblank_lines if not re_comment.match(x)]
        else:
            return [x for x in nonblank_lines]

    def get_data_lines(self, lines):
        """Set the ``data_lines`` attribute to the lines slice comprising the
        table data values."""
        data_lines = self.process_lines(lines)
        start_line = _get_line_index(self.start_line, data_lines)
        end_line = _get_line_index(self.end_line, data_lines)

        if start_line is not None or end_line is not None:
            self.data_lines = data_lines[slice(start_line, self.end_line)]
        else:  # Don't copy entire data lines unless necessary
            self.data_lines = data_lines

    def get_str_vals(self):
        """Return a generator that returns a list of column values (as strings)
        for each data line."""
        return self.splitter(self.data_lines)

    def masks(self, cols):
        """Set fill value for each column and then apply that fill value
        
        In the first step it is evaluated with value from ``fill_values`` applies to
        which column using ``fill_include_names`` and ``fill_exclude_names``.
        In the second step all replacements are done for the appropriate columns.
        """
        if self.fill_values:
            self._set_fill_values(cols)
            self._set_masks(cols)
    
    def _set_fill_values(self, cols):
        """Set the fill values of the individual cols based on fill_values of BaseData

        fill values has the following form:
        <fill_spec> = (<bad_value>, <fill_value>, <optional col_name>...)
        fill_values = <fill_spec> or list of <fill_spec>'s

        """
        if self.fill_values:
            #if input is only one <fill_spec>, then make it a list
            try:
                self.fill_values[0] + ''
                self.fill_values = [ self.fill_values ] 
            except TypeError:
                pass
            # Step 1: Set the default list of columns which are affected by fill_values
            colnames = set(self.header.colnames)
            if self.fill_include_names is not None:
                colnames.intersection_update(self.fill_include_names)
            if self.fill_exclude_names is not None:
                colnames.difference_update(self.fill_exclude_names)
        
            # Step 2a: Find out which columns are affected by this tuple
            # iterate over reversed order, so last condition is set first and overwritten by earlier conditions
            for replacement in reversed(self.fill_values):
                if len(replacement) < 2:
                    raise ValueError("Format of fill_values must be (<bad>, <fill>, <optional col1>, ...)")
                elif len(replacement) == 2:
                    affect_cols = colnames               
                else:
                    affect_cols = replacement[2:]
            
                for i, key in ((i, x) for i, x in enumerate(self.header.colnames) if x in affect_cols):
                    cols[i].fill_values[replacement[0]] = str(replacement[1])

    def _set_masks(self, cols):
        """Replace string values in col.str_vales and set masks"""
        if self.fill_values:
            for col in (col for col in cols if col.fill_values):
                col.mask = [False] * len(col.str_vals)
                for i, str_val in ((i, x) for i, x in enumerate(col.str_vals) if x in col.fill_values):
                    col.str_vals[i] = col.fill_values[str_val]
                    col.mask[i] = True

    def write(self, lines, table):
        if hasattr(self.start_line, '__call__'):
            raise TypeError('Start_line attribute cannot be callable for write()')
        else:
            data_start_line = self.start_line or 0

        while len(lines) < data_start_line:
            lines.append(itertools.cycle(self.write_spacer_lines))

        formatters = []
        for col in table.cols:
            formatter = self.formats.get(col.name, self.default_formatter)
            if not hasattr(formatter, '__call__'):
                formatter = _format_func(formatter)
            formatters.append(formatter)
            
        for vals in table.table:
            lines.append(self.splitter.join([formatter(val) for formatter, val in
                                             izip(formatters, vals)]))

def _format_func(format_str):
    def func(val):
        return format_str % val
    return func


class DictLikeNumpy(dict):
    """Provide minimal compatibility with numpy rec array API for BaseOutputter
    object::
      
      table = asciitable.read('mytable.dat', numpy=False)
      table.field('x')    # List of elements in column 'x'
      table.dtype.names   # get column names in order
      table[1]            # returns row 1 as a list
      table[1][2]         # 3nd column in row 1
      table['col1'][1]    # Row 1 in column col1
      for row_vals in table:  # iterate over table rows
          print row_vals  # print list of vals in each row

    """
    # To do: - add colnames property to set colnames and dtype.names as well.
    # - ordered dict?

    class Dtype(object):
        pass

    def __init__(self, *args, **kwargs):
        self.dtype = DictLikeNumpy.Dtype()
        dict.__init__(self, *args, **kwargs)

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item + '')
        except TypeError:
            return [dict.__getitem__(self, x)[item] for x in self.dtype.names]

    def field(self, colname):
        return self[colname]

    def __len__(self):
        return len(list(self.values())[0])

    def __iter__(self):
        self.__index = 0
        return self

    def __next__(self):
        try:
            vals = self[self.__index]
        except IndexError:
            raise StopIteration
        else:
            self.__index += 1
            return vals

    def next(self):
        return self.__next__()
        
def convert_list(python_type):
    """Return a function that converts a list into a list of the given
    ``python_type``.  This argument is a function that takes a single
    argument and returns a single value of the desired type.  In general
    this will be one of ``int``, ``float`` or ``str``.
    """
    def converter(vals):
        return [python_type(x) for x in vals]
    return converter

def convert_numpy(numpy_type):
    """Return a function that converts a list into a numpy array of the given
    ``numpy_type``.  This type must be a valid `numpy type
    <http://docs.scipy.org/doc/numpy/user/basics.types.html>`_, e.g.  numpy.int,
    numpy.uint, numpy.int8, numpy.int64, numpy.float, numpy.float64, numpy.str.
    """
    def converter(vals):
        return numpy.array(vals, numpy_type)
    return converter

class BaseOutputter(object):
    """Output table as a dict of column objects keyed on column name.  The
    table data are stored as plain python lists within the column objects.
    """
    converters = {}
    default_converter = [convert_list(int),
                         convert_list(float),
                         convert_list(str)]

    def __call__(self, cols):
        self._convert_vals(cols)
        table = DictLikeNumpy((x.name, x.data) for x in cols)
        table.dtype.names = tuple(x.name for x in cols)
        return table

    def _convert_vals(self, cols):
        for col in cols:
            converters = self.converters.get(col.name, self.default_converter)
            # Make a copy of converters and make sure converters is a list
            try:
                col.converters = converters[:]
            except TypeError:
                col.converters = [converters]

            while not hasattr(col, 'data'):
                try:
                    col.data = col.converters[0](col.str_vals)
                except (TypeError, ValueError):
                    col.converters.pop(0)
                except IndexError:
                    raise ValueError('Column %s failed to convert' % col.name)

class NumpyOutputter(BaseOutputter):
    """Output the table as a numpy.rec.recarray

    :param default_converter: default list of functions tried (in order) to convert a column
    
    Missing or bad data values are handled at two levels.  The first is in
    the data reading step where if ``data.fill_values`` is set then any
    occurences of a bad value are replaced by the correspond fill value.
    At the same time a boolean list ``mask`` is created in the column object.

    The second stage is when converting to numpy arrays which by default generates
    masked arrays, if ``data.fill_values`` is set and plain arrays if it is not.
    In the rare case that plain arrays are needed set ``auto_masked`` (default = True) and
    ``default_masked`` (default = False) to control this behavior as follows:

    ===========  ==============  ===========  ============
    auto_masked  default_masked  fill_values  output
    ===========  ==============  ===========  ============
    --            True           --           masked_array
    --            False          None         array
    True          --             dict(..)     masked_array
    False         --             dict(..)     array
    ===========  ==============  ===========  ============

    To set these values use::
    
      Outputter = asciitable.NumpyOutputter()
      Outputter.default_masked = True
    
    """

    auto_masked_array = True
    default_masked_array = False

    if has_numpy:
        default_converter = [convert_numpy(numpy.int),
                             convert_numpy(numpy.float),
                             convert_numpy(numpy.str)]

    def __call__(self, cols):
        self._convert_vals(cols)
        recarr = numpy.rec.fromarrays([x.data for x in cols], names=[x.name for x in cols])
        if self.default_masked_array or (self.auto_masked_array and
                                         any(col.fill_values for col in cols)):
            maarr = recarr.view(numpy.ma.MaskedArray)
            for col in cols:
                if col.fill_values:
                    maarr[col.name] = numpy.ma.masked_where(col.mask, maarr[col.name])
            return maarr
        else:
            return recarr


class BaseReader(object):
    """Class providing methods to read an ASCII table using the specified
    header, data, inputter, and outputter instances.

    Typical usage is to instantiate a Reader() object and customize the
    ``header``, ``data``, ``inputter``, and ``outputter`` attributes.  Each
    of these is an object of the corresponding class.

    """
    def __init__(self):
        self.header = BaseHeader()
        self.data = BaseData()
        self.inputter = BaseInputter()
        self.outputter = BaseOutputter()
        self.meta = {}                  # Placeholder for storing table metadata 
        self.keywords = []              # Placeholder for storing table Keywords

    def read(self, table):
        """Read the ``table`` and return the results in a format determined by
        the ``outputter`` attribute.

        The ``table`` parameter is any string or object that can be processed
        by the instance ``inputter``.  For the base Inputter class ``table`` can be
        one of:

        * File name
        * String (newline separated) with all header and data lines (must have at least 2 lines)
        * List of strings

        :param table: table input
        :returns: output table
        """
        # If ``table`` is a file then store the name in the ``data``
        # attribute. The ``table`` is a "file" if it is a string
        # without the new line specific to the OS.
        try:
            if os.linesep not in table + '':
                self.data.table_name = os.path.basename(table)
        except TypeError:
            # Not a string.
            pass
            
        # Data and Header instances benefit from a little cross-coupling.  Header may need to
        # know about number of data columns for auto-column name generation and Data may
        # need to know about header (e.g. for fixed-width tables where widths are spec'd in header.
        self.data.header = self.header
        self.header.data = self.data

        self.lines = self.inputter.get_lines(table)
        self.data.get_data_lines(self.lines)
        self.header.get_cols(self.lines)
        cols = self.header.cols         # header.cols corresponds to *output* columns requested
        n_data_cols = len(self.header.names) # header.names corresponds to *all* header columns in table
        self.data.splitter.cols = cols

        for i, str_vals in enumerate(self.data.get_str_vals()):
            if len(str_vals) != n_data_cols:
                errmsg = ('Number of header columns (%d) inconsistent with '
                          'data columns (%d) at data line %d\n'
                          'Header values: %s\n'
                          'Data values: %s' % (len(cols), len(str_vals), i,
                                               [x.name for x in cols], str_vals))
                raise InconsistentTableError(errmsg)

            for col in cols:
                col.str_vals.append(str_vals[col.index])

        self.data.masks(cols)
        self.table = self.outputter(cols)
        self.cols = self.header.cols

        return self.table

    @property
    def comment_lines(self):
        """Return lines in the table that match header.comment regexp"""
        if not hasattr(self, 'lines'):
            raise ValueError('Table must be read prior to accessing the header_comment_lines')
        if self.header.comment:
            re_comment = re.compile(self.header.comment)
            comment_lines = [x for x in self.lines if re_comment.match(x)]
        else:
            comment_lines = []
        return comment_lines

    def write(self, table=None):
        """Write ``table`` as list of strings.

        :param table: asciitable Reader object
        :returns: list of strings corresponding to ASCII table
        """
        if table is None:
            table = self

        # Write header and data to lines list 
        lines = []
        self.header.write(lines, table)
        self.data.write(lines, table)

        return lines

extra_reader_pars = ('Reader', 'Inputter', 'Outputter', 
                     'delimiter', 'comment', 'quotechar', 'header_start',
                     'data_start', 'data_end', 'converters',
                     'data_Splitter', 'header_Splitter',
                     'names', 'include_names', 'exclude_names',
                     'fill_values', 'fill_include_names', 'fill_exclude_names')

def get_reader(Reader=None, Inputter=None, Outputter=None, numpy=True, **kwargs):
    """Initialize a table reader allowing for common customizations.  Most of the
    default behavior for various parameters is determined by the Reader class.

    :param Reader: Reader class (default= :class:`BasicReader`)
    :param Inputter: Inputter class 
    :param Outputter: Outputter class
    :param numpy: use the NumpyOutputter class else use BaseOutputter (default=True)
    :param delimiter: column delimiter string
    :param comment: regular expression defining a comment line in table
    :param quotechar: one-character string to quote fields containing special characters
    :param header_start: line index for the header line not counting comment lines
    :param data_start: line index for the start of data not counting comment lines
    :param data_end: line index for the end of data (can be negative to count from end)
    :param converters: dict of converters
    :param data_Splitter: Splitter class to split data columns
    :param header_Splitter: Splitter class to split header columns
    :param names: list of names corresponding to each data column
    :param include_names: list of names to include in output (default=None selects all names)
    :param exclude_names: list of names to exlude from output (applied after ``include_names``)
    :param fill_values: specification of fill values for bad or missing table values
    :param fill_include_names: list of names to include in fill_values (default=None selects all names)
    :param fill_exclude_names: list of names to exlude from fill_values (applied after ``fill_include_names``)
    """
    if Reader is None:
        Reader = BasicReader
    reader = Reader()

    if Inputter is not None:
        reader.inputter = Inputter()

    if has_numpy and numpy:
        reader.outputter = NumpyOutputter()

    if Outputter is not None:
        reader.outputter = Outputter()

    bad_args = [x for x in kwargs if x not in extra_reader_pars]
    if bad_args:
        raise ValueError('Supplied arg(s) %s not allowed for get_reader()' % bad_args)

    if 'delimiter' in kwargs:
        reader.header.splitter.delimiter = kwargs['delimiter']
        reader.data.splitter.delimiter = kwargs['delimiter']
    if 'comment' in kwargs:
        reader.header.comment = kwargs['comment']
        reader.data.comment = kwargs['comment']
    if 'quotechar' in kwargs:
        reader.header.splitter.quotechar = kwargs['quotechar']
        reader.data.splitter.quotechar = kwargs['quotechar']
    if 'data_start' in kwargs:
        reader.data.start_line = kwargs['data_start']
    if 'data_end' in kwargs:
        reader.data.end_line = kwargs['data_end']
    if 'header_start' in kwargs:
        reader.header.start_line = kwargs['header_start']
    if 'converters' in kwargs:
        reader.outputter.converters = kwargs['converters']
    if 'data_Splitter' in kwargs:
        reader.data.splitter = kwargs['data_Splitter']()
    if 'header_Splitter' in kwargs:
        reader.header.splitter = kwargs['header_Splitter']()
    if 'names' in kwargs:
        reader.header.names = kwargs['names']
    if 'include_names' in kwargs:
        reader.header.include_names = kwargs['include_names']
    if 'exclude_names' in kwargs:
        reader.header.exclude_names = kwargs['exclude_names']
    if 'fill_values' in kwargs:
        reader.data.fill_values = kwargs['fill_values']
    if 'fill_include_names' in kwargs:
        reader.data.fill_include_names = kwargs['fill_include_names']
    if 'fill_exclude_names' in kwargs:
        reader.data.fill_exclude_names = kwargs['fill_exclude_names']


    return reader

def read(table, numpy=True, guess=None, **kwargs):
    """Read the input ``table``.  If ``numpy`` is True (default) return the
    table in a numpy record array.  Otherwise return the table as a dictionary
    of column objects using plain python lists to hold the data.  Most of the
    default behavior for various parameters is determined by the Reader class.

    :param table: input table (file name, list of strings, or single newline-separated string)
    :param numpy: use the :class:`NumpyOutputter` class else use :class:`BaseOutputter` (default=True)
    :param guess: try to guess the table format (default=True)
    :param Reader: Reader class (default= :class:`~asciitable.BasicReader`)
    :param Inputter: Inputter class
    :param Outputter: Outputter class
    :param delimiter: column delimiter string
    :param comment: regular expression defining a comment line in table
    :param quotechar: one-character string to quote fields containing special characters
    :param header_start: line index for the header line not counting comment lines
    :param data_start: line index for the start of data not counting comment lines
    :param data_end: line index for the end of data (can be negative to count from end)
    :param converters: dict of converters
    :param data_Splitter: Splitter class to split data columns
    :param header_Splitter: Splitter class to split header columns
    :param names: list of names corresponding to each data column
    :param include_names: list of names to include in output (default=None selects all names)
    :param exclude_names: list of names to exlude from output (applied after ``include_names``)
    :param fill_values: specification of fill values for bad or missing table values
    :param fill_include_names: list of names to include in fill_values (default=None selects all names)
    :param fill_exclude_names: list of names to exlude from fill_values (applied after ``fill_include_names``)

    """

    bad_args = [x for x in kwargs if x not in extra_reader_pars]
    if bad_args:
        raise ValueError('Supplied arg(s) %s not allowed for get_reader()' % bad_args)

    # Provide a simple way to choose between the two common outputters.  If an Outputter is
    # supplied in kwargs that will take precedence.
    new_kwargs = {}
    if has_numpy and numpy:
        new_kwargs['Outputter'] = NumpyOutputter
    else:
        new_kwargs['Outputter'] = BaseOutputter
    new_kwargs.update(kwargs)
        
    if guess is None:
        guess = GUESS
    if guess:
        dat = _guess(table, new_kwargs)
    else:
        reader = get_reader(**new_kwargs)
        dat = reader.read(table)
    return dat

def _is_number(x):
    try:
        x = float(x)
        return True
    except ValueError:
        pass
    return False
    
def _guess(table, read_kwargs):
    """Try to read the table using various sets of keyword args. First try the
    original args supplied in the read() call. Then try the standard guess
    keyword args. For each key/val pair specified explicitly in the read()
    call make sure that if there is a corresponding definition in the guess
    then it must have the same val.  If not then skip this guess."""

    # First try guessing
    for guess_kwargs in [read_kwargs.copy()] + _get_guess_kwargs_list():
        for key, val in read_kwargs.items():
            # Do guess_kwargs.update(read_kwargs) except that if guess_args has
            # a conflicting key/val pair then skip this guess entirely.
            if key not in guess_kwargs:
                guess_kwargs[key] = val
            elif val != guess_kwargs[key]:
                continue

        try:
            reader = get_reader(**guess_kwargs)
            dat = reader.read(table)
            # When guessing impose additional requirements on column names and number of cols
            bads = [" ", ",", "|", "\t", "'", '"']
            if (len(reader.cols) <= 1 or
                any(_is_number(col.name) or 
                     len(col.name) == 0 or 
                     col.name[0] in bads or 
                     col.name[-1] in bads for col in reader.cols)):
                raise ValueError
            return dat
        except (InconsistentTableError, ValueError):
            pass
    else:
        # failed all guesses, try the original read_kwargs without column requirements
        try:
            reader = get_reader(**read_kwargs)
            return reader.read(table)
        except (InconsistentTableError, ValueError):
            raise InconsistentTableError('Unable to read table with guess=True.')
    
def _get_guess_kwargs_list():
    guess_kwargs_list = [dict(Reader=Rdb),
                         dict(Reader=Tab),
                         dict(Reader=Cds),
                         dict(Reader=Daophot),
                         dict(Reader=Ipac),
                         ]
    for Reader in (CommentedHeader, BasicReader, NoHeader):
        for delimiter in ("|", ",", " ", "\s"):
            for quotechar in ('"', "'"):
                guess_kwargs_list.append(dict(
                    Reader=Reader, delimiter=delimiter, quotechar=quotechar))
    return guess_kwargs_list

extra_writer_pars = ('delimiter', 'comment', 'quotechar', 'formats',
                     'names', 'include_names', 'exclude_names')

def get_writer(Writer=None, **kwargs):
    """Initialize a table writer allowing for common customizations.  Most of the
    default behavior for various parameters is determined by the Writer class.

    :param Writer: Writer class (default= :class:`~asciitable.Basic` )
    :param delimiter: column delimiter string
    :param write_comment: string defining a comment line in table
    :param quotechar: one-character string to quote fields containing special characters
    :param formats: dict of format specifiers or formatting functions
    :param names: list of names corresponding to each data column
    :param include_names: list of names to include in output (default=None selects all names)
    :param exclude_names: list of names to exlude from output (applied after ``include_names``)
    """
    if Writer is None:
        Writer = Basic
    writer = Writer()

    bad_args = [x for x in kwargs if x not in extra_writer_pars]
    if bad_args:
        raise ValueError('Supplied arg(s) %s not allowed for get_writer()' % bad_args)

    if 'delimiter' in kwargs:
        writer.header.splitter.delimiter = kwargs['delimiter']
        writer.data.splitter.delimiter = kwargs['delimiter']
    if 'write_comment' in kwargs:
        writer.header.write_comment = kwargs['write_comment']
        writer.data.write_comment = kwargs['write_comment']
    if 'quotechar' in kwargs:
        writer.header.splitter.quotechar = kwargs['quotechar']
        writer.data.splitter.quotechar = kwargs['quotechar']
    if 'formats' in kwargs:
        writer.data.formats = kwargs['formats']
    if 'names' in kwargs:
        writer.header.names = kwargs['names']
    if 'include_names' in kwargs:
        writer.header.include_names = kwargs['include_names']
    if 'exclude_names' in kwargs:
        writer.header.exclude_names = kwargs['exclude_names']

    return writer

def write(table, output,  Writer=None, **kwargs):
    """Write the input ``table`` to ``filename``.  Most of the default behavior
    for various parameters is determined by the Writer class.

    :param table: input table (Reader object, NumPy struct array, list of lists, etc)
    :param output: output (filename, file-like object)
    :param Writer: Writer class (default= :class:`~asciitable.Basic` )
    :param delimiter: column delimiter string
    :param write_comment: string defining a comment line in table
    :param quotechar: one-character string to quote fields containing special characters
    :param formats: dict of format specifiers or formatting functions
    :param names: list of names corresponding to each data column
    :param include_names: list of names to include in output (default=None selects all names)
    :param exclude_names: list of names to exlude from output (applied after ``include_names``)
    """

    bad_args = [x for x in kwargs if x not in extra_writer_pars]
    if bad_args:
        raise ValueError('Supplied arg(s) %s not allowed for get_writer()' % bad_args)

    reader_kwargs = dict((key, val) for key, val in kwargs.items()
                         if key in ('names', 'include_names', 'exclude_names'))
    if not isinstance(table, BaseReader) or reader_kwargs:
        reader = get_reader(Reader=Memory, **reader_kwargs)
        reader.read(table)
        table = reader

    writer = get_writer(Writer=Writer, **kwargs)
    lines = writer.write(table)

    # Write the lines to output 
    outstr = os.linesep.join(lines)
    if not hasattr(output, 'write'):
        output = open(output, 'w')
        output.write(outstr)
        output.write(os.linesep)
        output.close()
    else:
        output.write(outstr)
        output.write(os.linesep)

############################################################################################################
############################################################################################################
##
##  Custom extensions
##
############################################################################################################
############################################################################################################

class Basic(BaseReader):
    """Read a character-delimited table with a single header line at the top
    followed by data lines to the end of the table.  Lines beginning with # as
    the first non-whitespace character are comments.  This reader is highly
    configurable.
    ::

        rdr = asciitable.get_reader(Reader=asciitable.Basic)
        rdr.header.splitter.delimiter = ' '
        rdr.data.splitter.delimiter = ' '
        rdr.header.start_line = 0
        rdr.data.start_line = 1
        rdr.data.end_line = None
        rdr.header.comment = r'\s*#'
        rdr.data.comment = r'\s*#'

    Example table::
    
      # Column definition is the first uncommented line
      # Default delimiter is the space character.
      apples oranges pears

      # Data starts after the header column definition, blank lines ignored
      1 2 3
      4 5 6
    """
    def __init__(self):
        BaseReader.__init__(self)
        self.header.splitter.delimiter = ' '
        self.data.splitter.delimiter = ' '
        self.header.start_line = 0
        self.data.start_line = 1
        self.header.comment = r'\s*#'
        self.header.write_comment = '# '
        self.data.comment = r'\s*#'
        self.data.write_comment = '# '

BasicReader = Basic

class ContinuationLinesInputter(BaseInputter):
    """Inputter where lines ending in ``continuation_char`` are joined
    with the subsequent line.  Example::

      col1 col2 col3
      1 \
      2 3
      4 5 \
      6
    """

    continuation_char = '\\'

    def process_lines(self, lines):
        striplines = (x.strip() for x in lines)
        lines = [x for x in striplines if len(x) > 0]

        parts = []
        outlines = []
        for line in lines:
            if line.endswith(self.continuation_char):
                parts.append(line.rstrip(self.continuation_char))
            else:
                parts.append(line)
                outlines.append(''.join(parts))
                parts = []

        return outlines


class NoHeader(BasicReader):
    """Read a table with no header line.  Columns are autonamed using
    header.auto_format which defaults to "col%d".  Otherwise this reader
    the same as the :class:`Basic` class from which it is derived.  Example::

      # Table data
      1 2 "hello there"
      3 4 world
    """
    def __init__(self):
        Basic.__init__(self)
        self.header.start_line = None
        self.data.start_line = 0

NoHeaderReader = NoHeader

class CommentedHeaderHeader(BaseHeader):
    """Header class for which the column definition line starts with the
    comment character.  See the :class:`CommentedHeader` class  for an example.
    """
    def process_lines(self, lines):
        """Return only lines that start with the comment regexp.  For these
        lines strip out the matching characters."""
        re_comment = re.compile(self.comment)
        for line in lines:
            match = re_comment.match(line)
            if match:
                yield line[match.end():]

    def write(self, lines, table):
        lines.append(self.write_comment + self.splitter.join([x.name for x in table.cols]))

class CommentedHeader(BaseReader):
    """Read a file where the column names are given in a line that begins with the
    header comment character.  The default delimiter is the <space> character.::

      # col1 col2 col3
      # Comment line
      1 2 3
      4 5 6
    """
    def __init__(self):
        BaseReader.__init__(self)
        self.header = CommentedHeaderHeader()
        self.header.splitter.delimiter = ' '
        self.data.splitter.delimiter = ' '
        self.header.start_line = 0
        self.data.start_line = 0
        self.header.comment = r'\s*#'
        self.header.write_comment = '# '
        self.data.comment = r'\s*#'
        self.data.write_comment = '# '

CommentedHeaderReader = CommentedHeader

class Tab(BasicReader):
    """Read a tab-separated file.  Unlike the :class:`Basic` reader, whitespace is 
    not stripped from the beginning and end of lines.  By default whitespace is
    still stripped from the beginning and end of individual column values.

    Example::

      col1 <tab> col2 <tab> col3
      # Comment line
      1 <tab> 2 <tab> 5
    """
    def __init__(self):
        Basic.__init__(self)
        self.header.splitter.delimiter = '\t'
        self.data.splitter.delimiter = '\t'
        # Don't strip line whitespace since that includes tabs
        self.header.splitter.process_line = None  
        self.data.splitter.process_line = None
        # Don't strip data value whitespace since that is significant in TSV tables
        self.data.splitter.process_val = None
        self.data.splitter.skipinitialspace = False

TabReader = Tab

class Rdb(TabReader):
    """Read a tab-separated file with an extra line after the column definition
    line.  The RDB format meets this definition.  Example::

      col1 <tab> col2 <tab> col3
      N <tab> S <tab> N
      1 <tab> 2 <tab> 5

    In this reader the second line is just ignored.
    """
    def __init__(self):
        TabReader.__init__(self)
        self.header = RdbHeader()
        self.header.start_line = 0
        self.header.comment = r'\s*#'
        self.header.write_comment = '# '
        self.header.splitter.delimiter = '\t'
        self.header.splitter.process_line = None  
        self.data.start_line = 2

RdbReader = Rdb

class Daophot(BaseReader):
    """Read a DAOphot file.
    Example::

      #K MERGERAD   = INDEF                   scaleunit  %-23.7g  
      #K IRAF = NOAO/IRAFV2.10EXPORT version %-23s
      #K USER = davis name %-23s
      #K HOST = tucana computer %-23s
      #
      #N ID    XCENTER   YCENTER   MAG         MERR          MSKY           NITER    \\
      #U ##    pixels    pixels    magnitudes  magnitudes    counts         ##       \\
      #F %-9d  %-10.3f   %-10.3f   %-12.3f     %-14.3f       %-15.7g        %-6d     
      #
      #N         SHARPNESS   CHI         PIER  PERROR                                \\
      #U         ##          ##          ##    perrors                               \\
      #F         %-23.3f     %-12.3f     %-6d  %-13s
      #
      14       138.538   256.405   15.461      0.003         34.85955       4        \\
      -0.032      0.802       0     No_error

    The keywords defined in the #K records are available via the Daophot reader object::

      reader = asciitable.get_reader(Reader=asciitable.DaophotReader)
      data = reader.read('t/daophot.dat')
      for keyword in reader.keywords:
          print keyword.name, keyword.value, keyword.units, keyword.format
    
    """
    
    def __init__(self):
        #if not has_numpy:
        #    raise NotImplementedError('Daophot reader requires NumPy')
        BaseReader.__init__(self)
        self.header = DaophotHeader()
        self.inputter = ContinuationLinesInputter()
        self.data.splitter.delimiter = ' '
        self.data.start_line = 0
        self.data.comment = r'\s*#'
    
    def read(self, table):
        output = BaseReader.read(self, table)
        if has_numpy:
            headerkeywords = read(self.comment_lines, comment=r'(?!#K)', Reader=NoHeaderReader,
                                  names = ['temp1','keyword','temp2','value','unit','format'])

            for line in headerkeywords:
                self.keywords.append(Keyword(line['keyword'], line['value'], 
                                             units=line['unit'], format=line['format']))
        self.table = output
        self.cols = self.header.cols

        return self.table

    def write(self, table=None):
        raise NotImplementedError

DaophotReader = Daophot

class DaophotHeader(BaseHeader):
    """Read the header from a file produced by the IRAF DAOphot routine."""
    def __init__(self):
        BaseHeader.__init__(self)
        self.comment = r'\s*#K'

    def get_cols(self, lines):
        """Initialize the header Column objects from the table ``lines`` for a DAOphot
        header.  The DAOphot header is specialized so that we just copy the entire BaseHeader
        get_cols routine and modify as needed.

        :param lines: list of table lines
        :returns: list of table Columns
        """

        self.names = []
        re_name_def = re.compile(r'#N([^#]+)#')
        for line in lines:
            if not line.startswith('#'):
                break                   # End of header lines
            else:
                match = re_name_def.search(line)
                if match:
                    self.names.extend(match.group(1).split())
        
        if not self.names:
            raise InconsistentTableError('No column names found in DAOphot header')
        
        names = set(self.names)
        if self.include_names is not None:
            names.intersection_update(self.include_names)
        if self.exclude_names is not None:
            names.difference_update(self.exclude_names)
            
        self.cols = [Column(name=x, index=i) for i, x in enumerate(self.names) if x in names]

class FixedWidthSplitter(BaseSplitter):
    """Split line based on fixed start and end positions for each ``col`` in
    ``self.cols``.

    This class requires that the Header class will have defined ``col.start``
    and ``col.end`` for each column.  The reference to the ``header.cols`` gets
    put in the splitter object by the base Reader.read() function just in time
    for splitting data lines by a ``data`` object.  This class won't work for
    splitting a fixed-width header but generally the header will be used to
    determine the column start and end positions.

    Note that the ``start`` and ``end`` positions are defined in the pythonic
    style so line[start:end] is the desired substring for a column.  This splitter
    class does not have a hook for ``process_lines`` since that is generally not
    useful for fixed-width input.
    """
    def __call__(self, lines):
        for line in lines:
            vals = [line[x.start:x.end] for x in self.cols]
            if self.process_val:
                yield [self.process_val(x) for x in vals]
            else:
                yield vals


class CdsHeader(BaseHeader):
    def __init__(self, readme=None):
        """Initialize ReadMe filename.

        :param readme: The ReadMe file to construct header from.
        :type readme: String
       
        CDS tables have their header information in a separate file
        named "ReadMe". The ``get_cols`` method will read the contents
        of the ReadMe file given by ``self.readme`` and set the various
        properties needed to read the data file. The data file name
        will be the ``table`` passed to the ``read`` method.
        """
        BaseHeader.__init__(self)
        self.readme = readme
        
    def get_cols(self, lines):
        """Initialize the header Column objects from the table ``lines`` for a CDS
        header. 

        :param lines: list of table lines
        :returns: list of table Columns
        """
        # Read header block for the table ``self.data.table_name`` from the read
        # me file ``self.readme``.
        if self.readme and self.data.table_name:
            in_header = False
            f = open(self.readme,"r")
            # Header info is not in data lines but in a separate file.
            lines = []
            comment_lines = 0
            for line in f:
                line = line.strip()
                if in_header:
                    lines.append(line)
                    if line.startswith('------') or line.startswith('======='):
                         comment_lines += 1
                         if comment_lines == 3: break
                else:
                    m = re.match(r'Byte-by-byte Description of file: (?P<name>\S*)',
                            line, re.IGNORECASE)
                    if m and m.group('name') == self.data.table_name:
                        in_header = True
                        lines.append(line)
            else:
                raise InconsistentTableError("Cant' find table {0} in {1}".format(
                        self.data.table_name, self.readme))
            f.close()
                       
        for i_col_def, line in enumerate(lines):
            if re.match(r'Byte-by-byte Description', line, re.IGNORECASE):
                break

        re_col_def = re.compile(r"""\s*
                                    (?P<start> \d+ \s* -)? \s*
                                    (?P<end>   \d+)        \s+
                                    (?P<format> [\w.]+)     \s+
                                    (?P<units> \S+)        \s+
                                    (?P<name>  \S+)        \s+
                                    (?P<descr> \S.+)""",
                                re.VERBOSE)

        cols = []
        for i, line in enumerate(itertools.islice(lines, i_col_def+4, None)):
            if line.startswith('------') or line.startswith('======='):
                break
            match = re_col_def.match(line)
            if match:
                col = Column(name=match.group('name'), index=i)
                col.start = int(re.sub(r'[-\s]', '', match.group('start') or match.group('end'))) - 1
                col.end = int(match.group('end'))
                col.units = match.group('units')
                col.descr = match.group('descr')
                col.format = match.group('format')
                if col.descr.startswith('?') and col.format[0] in ('F', 'E'):
                    self.data.fill_values.append(('', 'nan', match.group('name')))
                if col.descr.startswith('?=') and col.format[0] in ('F', 'E'):
                    self.data.fill_values.append((col.descr.split()[0][2:], 'nan', match.group('name')))
                cols.append(col)
            else:  # could be a continuation of the previous col's description
                if cols:
                    cols[-1].descr += line.strip()
                else:
                    raise ValueError('Line "%s" not parsable as CDS header' % line)

        self.names = [x.name for x in cols]
        names = set(self.names)
        if self.include_names is not None:
            names.intersection_update(self.include_names)
        if self.exclude_names is not None:
            names.difference_update(self.exclude_names)
            
        self.cols = [x for x in cols if x.name in names]

        # Re-index the cols because the FixedWidthSplitter does NOT return the ignored
        # cols (as is the case for typical delimiter-based splitters)
        for i, col in enumerate(self.cols):
            col.index = i
            

class CdsData(BaseData):
    """CDS table data reader
    """
    splitter_class = FixedWidthSplitter
    
    def process_lines(self, lines):
        """Skip over CDS header by finding the last section delimiter"""
        # If the header has a ReadMe and data has a filename
        # then no need to skip, as the data lines do not have header
        # info. The ``read`` method adds the table_name to the ``data``
        # attribute.
        if self.header.readme and self.table_name:
            return lines
        i_sections = [i for (i, x) in enumerate(lines)
                      if x.startswith('------') or x.startswith('=======')]
        if not i_sections:
            raise InconsistentTableError('No CDS section delimiter found')
        return lines[i_sections[-1]+1 : ]


class Cds(BaseReader):
    """Read a CDS format table: http://vizier.u-strasbg.fr/doc/catstd.htx.
    Example::

      Table: Spitzer-identified YSOs: Addendum
      ================================================================================
      Byte-by-byte Description of file: datafile3.txt
      --------------------------------------------------------------------------------
         Bytes Format Units  Label  Explanations
      --------------------------------------------------------------------------------
         1-  3 I3     ---    Index  Running identification number
         5-  6 I2     h      RAh    Hour of Right Ascension (J2000) 
         8-  9 I2     min    RAm    Minute of Right Ascension (J2000) 
        11- 15 F5.2   s      RAs    Second of Right Ascension (J2000) 
      --------------------------------------------------------------------------------
        1 03 28 39.09

    When ``Cds`` reader object is created with a ``readme`` parameter
    passed to it at initialization, then when the ``read`` method is
    executed with a table filename, the header information for the
    specified table is taken from the ``readme`` file.  An
    ``InconsistentTableError`` is raised if the ``readme`` file does not
    have header information for the given table.
    
        >>> readme = "t/vizier/ReadMe"
        >>> r = asciitable.Cds(readme)
        >>> table = r.read("t/vizier/table1.dat")
        >>> # table5.dat has the same ReadMe file
        >>> table = r.read("t/vizier/table5.dat")

    If no ``readme`` parameter is specified, then the header
    information is assumed to be at the top of the given table.

        >>> r = asciitable.Cds()
        >>> table = r.read("t/cds.dat")
        >>> #The following gives InconsistentTableError, since no
        >>> #readme file was given and table1.dat does not have a header.
        >>> table = r.read("t/vizier/table1.dat)
    
    Caveats:

    * Format, Units, and Explanations are available in the ``Reader.cols`` attribute,
      but are not otherwise used.
    * All of the other metadata defined by this format is ignored.

    Code contribution to enhance the parsing to include metadata in a Reader.meta
    attribute would be welcome.

    """
    def __init__(self, readme=None):
        BaseReader.__init__(self)
        self.header = CdsHeader(readme)
        self.data = CdsData()

    def write(self, table=None):
        """Not available for the Cds class (raises NotImplementedError)"""
        raise NotImplementedError

CdsReader = Cds

class Ipac(BaseReader):
    """Read an IPAC format table:
    http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html::

      \\name=value                                                    
      \\ Comment                                                      
      |  column1 |  column2 | column3 | column4  |    column5       |
      |  double  |  double  |   int   |   double |     char         |
      |   unit   |   unit   |   unit  |    unit  |     unit         |
      |   null   |   null   |   null  |    null  |     null         |
       2.0978     29.09056   73765     2.06000    B8IVpMnHg          
    
    Or::
    
      |-----ra---|----dec---|---sao---|------v---|----sptype--------|
        2.09708   29.09056     73765    2.06000   B8IVpMnHg
    
    Caveats:
    
    * Data type, Units, and Null value specifications are ignored.
    * Keywords are ignored.
    * The IPAC spec requires the first two header lines but this reader only 
      requires the initial column name definition line

    Overcoming these limitations would not be difficult, code contributions
    welcome from motivated users.
    """
    def __init__(self):
        BaseReader.__init__(self)
        self.header = IpacHeader()
        self.data = IpacData()

    def write(self, table=None):
        """Not available for the Ipac class (raises NotImplementedError)"""
        raise NotImplementedError

IpacReader = Ipac

class IpacHeader(BaseHeader):
    """IPAC table header"""
    comment = r'\\'
    splitter_class = BaseSplitter
    
    def __init__(self):
        self.splitter = self.__class__.splitter_class()
        self.splitter.process_line = None
        self.splitter.process_val = None
        self.splitter.delimiter = '|'

    def process_lines(self, lines):
        """Generator to yield IPAC header lines, i.e. those starting and ending with
        delimiter character."""
        delim = self.splitter.delimiter
        for line in lines:
            if line.startswith(delim) and line.endswith(delim):
                yield line.strip(delim)

    def get_cols(self, lines):
        """Initialize the header Column objects from the table ``lines``.

        Based on the previously set Header attributes find or create the column names.
        Sets ``self.cols`` with the list of Columns.  This list only includes the actual
        requested columns after filtering by the include_names and exclude_names
        attributes.  See ``self.names`` for the full list.

        :param lines: list of table lines
        :returns: list of table Columns
        """
        header_lines = self.process_lines(lines)  # generator returning valid header lines
        header_vals = [vals for vals in self.splitter(header_lines)]
        if len(header_vals) == 0:
            raise ValueError('At least one header line beginning and ending with delimiter required')
        elif len(header_vals) > 4:
            raise ValueError('More than four header lines were found')

        # Generate column definitions
        cols = []
        start = 1
        for i, name in enumerate(header_vals[0]):
            col = Column(name=name.strip(' -'), index=i)
            col.start = start
            col.end = start + len(name) 
            if len(header_vals) > 1:
                col.type = header_vals[1][i].strip(' -')
            if len(header_vals) > 2:
                col.units = header_vals[2][i].strip() # Can't strip dashes here
            if len(header_vals) > 3:
                col.null = header_vals[3][i].strip() # Can't strip dashes here
            start = col.end + 1
            cols.append(col)
        
        # Standard column name filtering (include or exclude names)
        self.names = [x.name for x in cols]
        names = set(self.names)
        if self.include_names is not None:
            names.intersection_update(self.include_names)
        if self.exclude_names is not None:
            names.difference_update(self.exclude_names)
            
        # Generate final list of cols and re-index the cols because the
        # FixedWidthSplitter does NOT return the ignored cols (as is the
        # case for typical delimiter-based splitters)
        self.cols = [x for x in cols if x.name in names]
        for i, col in enumerate(self.cols):
            col.index = i

class IpacData(BaseData):
    """IPAC table data reader"""
    splitter_class = FixedWidthSplitter
    comment = r'[|\\]'
    
class Memory(BaseReader):
    """Read a table from a data object in memory.  Several input data formats are supported:

    **Output of asciitable.read()**::

      table = asciitable.get_reader(Reader=asciitable.Daophot)
      data = table.read('t/daophot.dat')
      mem_data_from_table = asciitable.read(table, Reader=asciitable.Memory)
      mem_data_from_data = asciitable.read(data, Reader=asciitable.Memory)

    **Numpy structured array**::

      data = numpy.zeros((2,), dtype=[('col1','i4'), ('col2','f4'), ('col3', 'a10')])
      data[:] = [(1, 2., 'Hello'), (2, 3., "World")]
      mem_data = asciitable.read(data, Reader=asciitable.Memory)

    **Sequence of sequences**::
    
      data = [[1, 2,   3      ],
              [4, 5.2, 6.1    ],
              [8, 9,   'hello']]
      mem_data = asciitable.read(data, Reader=asciitable.Memory, names=('c1','c2','c3'))

    **Dict of sequences**::

      data = {'c1': [1, 2, 3],
              'c2': [4, 5.2, 6.1],
              'c3': [8, 9, 'hello']}
      mem_data = asciitable.read(data, Reader=asciitable.Memory, names=('c1','c2','c3'))

    """
    def __init__(self):
        self.header = MemoryHeader()
        self.data = MemoryData()
        self.inputter = MemoryInputter()
        self.outputter = BaseOutputter()
        self.meta = {}                  # Placeholder for storing table metadata 
        self.keywords = []              # Table Keywords

    def read(self, table):
        self.data.header = self.header
        self.header.data = self.data

        self.lines = self.inputter.get_lines(table, self.header.names)
        self.data.get_data_lines(self.lines)
        self.header.get_cols(self.lines)
        cols = self.header.cols         # header.cols corresponds to *output* columns requested
        n_data_cols = len(self.header.names) # header.names corresponds to *all* header columns in table
        self.data.splitter.cols = cols

        for i, str_vals in enumerate(self.data.get_str_vals()):
            if len(str_vals) != n_data_cols:
                errmsg = ('Number of header columns (%d) inconsistent with '
                          'data columns (%d) at data line %d\n'
                          'Header values: %s\n'
                          'Data values: %s' % (len(cols), len(str_vals), i,
                                               [x.name for x in cols], str_vals))
                raise InconsistentTableError(errmsg)

            for col in cols:
                col.str_vals.append(str_vals[col.index])

        self.data.masks(cols)
        self.cols = cols
        if hasattr(table, 'keywords'):
            self.keywords = table.keywords

        self.outputter.default_converter = lambda vals: vals
        self.table = self.outputter(cols)
        self.cols = self.header.cols

        return self.table

    def write(self, table=None):
        """Not available for the Memory class (raises NotImplementedError)"""
        raise NotImplementedError

class MemoryInputter(BaseInputter):
    """Get the lines from the table input and return an iterable object that contains the data lines.

    The input table can be one of:

    * asciitable Reader object
    * NumPy structured array
    * List of lists
    * Dict of lists
    """
    def get_lines(self, table, names):
        """Get the lines from the ``table`` input.
        
        :param table: table input
        :param names: list of column names (only used for dict of lists to set column order)
        :returns: list of lines

        """
        try:  
            # If table is dict-like this will return the first key.
            # If table is list-like this will return the first row.
            first_row_or_key = next(iter(table))
        except TypeError:
            # Not iterable, is it an asciitable Reader instance?
            if isinstance(table, BaseReader):
                lines = table.table
            else:
                raise TypeError('Input table must be iterable or else be a Reader object')
        else:
            # table is iterable, now see if it is dict-like or list-like
            try:
                table[first_row_or_key]
            except (TypeError, IndexError):
                lines = table
            else:
                lines = DictLikeNumpy(table)
                if names is None:
                    lines.dtype.names = sorted(lines.keys())
                else:
                    lines.dtype.names = names

        return lines

class MemoryHeader(BaseHeader):
    """Memory table header reader"""
    def __init__(self):
        pass

    def get_cols(self, lines):
        """Initialize the header Column objects from the table ``lines``.

        Based on the previously set Header attributes find or create the column names.
        Sets ``self.cols`` with the list of Columns.  This list only includes the actual
        requested columns after filtering by the include_names and exclude_names
        attributes.  See ``self.names`` for the full list.

        :param lines: list of table lines
        :returns: list of table Columns
        """

        if self.names is None:
            # No column names supplied so first try to get them from NumPy structured array
            try:
                self.names = lines.dtype.names
            except AttributeError:
                # Still no col names available so auto-generate them
                try:
                    first_data_vals = next(iter(lines))
                except StopIteration:
                    raise InconsistentTableError('No data lines found so cannot autogenerate column names')
                n_data_cols = len(first_data_vals)
                self.names = [self.auto_format % i for i in range(1, n_data_cols+1)]

        names = set(self.names)
        if self.include_names is not None:
            names.intersection_update(self.include_names)
        if self.exclude_names is not None:
            names.difference_update(self.exclude_names)
            
        self.cols = [Column(name=x, index=i) for i, x in enumerate(self.names) if x in names]

class MemorySplitter(BaseSplitter):
    """Splitter for data already in memory.  It is assumed that ``lines`` are
    iterable and that each line (aka row) is also an iterable object that
    provides the column values for that row."""
    def __call__(self, lines):
        for vals in lines:
            yield vals

class MemoryData(BaseData):
    """Memory table data reader.  Same as the BaseData reader but with a
    special splitter and a "pass-thru" process_lines function."""

    splitter_class = MemorySplitter

    def process_lines(self, lines):
        return lines

class RdbHeader(BaseHeader):
    def get_cols(self, lines):
        """Initialize the header Column objects from the table ``lines``.
        
        This is a specialized get_cols for the RDB type:
        Line 0: RDB col names
        Line 1: RDB col definitions
        Line 2+: RDB data rows

        :param lines: list of table lines
        :returns: None
        """
        header_lines = self.process_lines(lines)   # this is a generator
        header_vals_list = [hl for _, hl in zip(range(2), self.splitter(header_lines))]
        if len(header_vals_list) != 2:
            raise ValueError('RDB header requires 2 lines')
        self.names, rdb_types = header_vals_list

        if len(self.names) != len(rdb_types):
            raise ValueError('RDB header mismatch between number of column names and column types')
        
        if any(not re.match(r'\d*(N|S)$', x, re.IGNORECASE) for x in rdb_types):
            raise ValueError('RDB types definitions do not all match [num](N|S): %s' % rdb_types)
        
        names = set(self.names)
        if self.include_names is not None:
            names.intersection_update(self.include_names)
        if self.exclude_names is not None:
            names.difference_update(self.exclude_names)
            
        self.cols = [Column(name=name, index=i) 
                     for i, name in enumerate(self.names) if name in names]
        for col, rdb_type in zip(self.cols, rdb_types):
            col.rdb_type = rdb_type

    def write(self, lines, table):
        lines.append(self.splitter.join([x.name for x in table.cols]))
        lines.append(self.splitter.join([getattr(x, 'rdb_type', 'S') for x in table.cols]))

class WhitespaceSplitter(DefaultSplitter):
    def process_line(self, line):
        """Replace tab with space within ``line`` while respecting quoted substrings"""
        newline = []
        in_quote = False
        lastchar = None
        for char in line:
            if char == self.quotechar and (self.escapechar is None or 
                                           lastchar != self.escapechar):
                in_quote = not in_quote
            if char == '\t' and not in_quote:
                char = ' '
            lastchar = char
            newline.append(char)

        return ''.join(newline)

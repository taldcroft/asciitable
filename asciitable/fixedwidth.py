"""Asciitable: an extensible ASCII table reader and writer.

fixedwidth.py:
  Read or write a table with fixed width columns.

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
import itertools
import asciitable.core as core
from asciitable.core import io, next, izip, any

class FixedWidthHeader(core.BaseHeader):
    """Fixed width table header reader

    :param auto_format: format string for auto-generating column names
    :param start_line: None, int, or a function of ``lines`` that returns None or int
    :param comment: regular expression for comment lines
    :param splitter_class: Splitter class for splitting data lines into columns
    :param names: list of names corresponding to each data column
    :param include_names: list of names to include in output (default=None selects all names)
    :param exclude_names: list of names to exlude from output (applied after ``include_names``)
    """

    def get_cols(self, lines):
        """Initialize the header Column objects from the table ``lines``.

        Based on the previously set Header attributes find or create the column names.
        Sets ``self.cols`` with the list of Columns.  This list only includes the actual
        requested columns after filtering by the include_names and exclude_names
        attributes.  See ``self.names`` for the full list.

        :param lines: list of table lines
        :returns: None
        """

        start_line = core._get_line_index(self.start_line, self.process_lines(lines))
        if start_line is None:
            # Get the data values from the first line of table data to determine n_data_cols
            data_lines = self.data.process_lines(lines)
            if not data_lines:
                raise InconsistentTableError('No data lines found so cannot autogenerate column names')
            vals, starts, ends = self.get_fixedwidth_params(data_lines[0])

            if self.names is None:
                # No col names specified so auto-generate corresponding to data columns
                self.names = [self.auto_format % i for i in range(1, len(vals) + 1)]

        else:
            for i, line in enumerate(self.process_lines(lines)):
                if i == start_line:
                    break
            else: # No header line matching
                raise ValueError('No header line found in table')

            vals, starts, ends = self.get_fixedwidth_params(line)
            if self.names is None:
                self.names = vals
        
        self._set_cols_from_names()
        self.n_data_cols = len(self.cols)
        
        # Set column start and end positions.  Also re-index the cols because
        # the FixedWidthSplitter does NOT return the ignored cols (as is the
        # case for typical delimiter-based splitters)
        for i, col in enumerate(self.cols):
            col.start = starts[col.index]
            col.end = ends[col.index]
            col.index = i

    def get_fixedwidth_params(self, line):
        """ Split row on the delimiter and determine column values and column
        start and end positions.  This might include null columns with zero length
        (e.g. for header row = "| col1 | col2 |").  Leave the null columns in
        self.names until the very end."""

        if self.col_starts is not None and self.col_ends is not None:
            starts = list(self.col_starts)  # could be any iterable, e.g. np.array
            ends = [x + 1 for x in self.col_ends] # user supplies inclusive endpoint
            if len(starts) != len(ends):
                raise ValueError('Fixed width col_starts and col_ends must have the same length')
            vals = [line[start:end].strip() for start, end in zip(starts, ends)]
        else:
            vals = line.split(self.splitter.delimiter)
            starts = [0]
            ends = []
            for val in vals:
                if val:
                    ends.append(starts[-1] + len(val))
                    starts.append(ends[-1] + 1)
                else:
                    starts[-1] += 1
            starts = starts[:-1]
            vals = [x.strip() for x in vals if x]
            if len(vals) != len(starts) or len(vals) != len(ends):
                raise InconsistentTableError('Error parsing fixed width header')

        return vals, starts, ends

    def write(self, lines):
        if self.start_line is not None:
            for i, spacer_line in izip(range(self.start_line),
                                       itertools.cycle(self.write_spacer_lines)):
                lines.append(spacer_line)
            # Hheader line not written until data are formatted.  Until then
            # it is not known how wide each column will be for fixed width.


class FixedWidthData(core.BaseData):
    """Base table data reader.

    :param start_line: None, int, or a function of ``lines`` that returns None or int
    :param end_line: None, int, or a function of ``lines`` that returns None or int
    :param comment: Regular expression for comment lines
    :param splitter_class: Splitter class for splitting data lines into columns
    """

    splitter_class = core.FixedWidthSplitter

    def write(self, lines):
        if hasattr(self.start_line, '__call__'):
            raise TypeError('Start_line attribute cannot be callable for write()')
        else:
            data_start_line = self.start_line or 0

        formatters = []
        for col in self.cols:
            formatter = self.formats.get(col.name, self.default_formatter)
            if not hasattr(formatter, '__call__'):
                formatter = core._format_func(formatter)
            col.formatter = formatter
            
        vals_list = []
        # Col iterator does the formatting defined above so each val is a string
        # and vals is a tuple of strings for all columns of each row
        for vals in izip(*self.cols):
            vals_list.append(vals)
            
        for i, col in enumerate(self.cols):
            col.width = max([len(vals[i]) for vals in vals_list])
            if self.header.start_line is not None:
                col.width = max(col.width, len(col.name))

        widths = [col.width for col in self.cols]
        if self.header.start_line is not None:
            lines.append(self.splitter.join([col.name for col in self.cols], widths))

        while len(lines) < data_start_line:
            lines.append(itertools.cycle(self.write_spacer_lines))

        for vals in vals_list:
            lines.append(self.splitter.join(vals, widths))

        return lines


class FixedWidth(core.BaseReader):
    """Read or write a fixed width table with a single header line at the top
    followed by data lines to the end of the table.   
    """
    def __init__(self, col_starts=None, col_ends=None, delimiter_pad=' ', bookend=True):
        core.BaseReader.__init__(self)

        self.header = FixedWidthHeader()
        self.data = FixedWidthData()
        self.data.header = self.header
        self.header.data = self.data

        self.header.splitter.delimiter = '|'
        self.data.splitter.delimiter = '|'
        self.data.splitter.delimiter_pad = delimiter_pad
        self.data.splitter.bookend = bookend
        self.header.start_line = 0
        self.data.start_line = 1
        self.header.comment = r'\s*#'
        self.header.write_comment = '# '
        self.data.comment = r'\s*#'
        self.data.write_comment = '# '
        self.header.col_starts = col_starts
        self.header.col_ends = col_ends


class FixedWidthNoHeader(FixedWidth):
    """Read or write a fixed width table which has no header line.  
    followed by data lines to the end of the table.  Lines beginning with # as
    the first non-whitespace character are comments."""
    def __init__(self, col_starts=None, col_ends=None, delimiter_pad=' ', bookend=True):
        FixedWidth.__init__(self, col_starts, col_ends,
                            delimiter_pad=delimiter_pad, bookend=bookend)
        self.header.start_line = None
        self.data.start_line = 0

        

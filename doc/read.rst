.. _asciitable_read:

.. include:: references.txt

Reading tables
----------------------------
The majority of commonly encountered ASCII tables can be easily read with the |read|
function::

  import asciitable
  data = asciitable.read(table)

where ``table`` is the name of a file, a string representation of a table, or a 
list of table lines.  By default |read| will try to `guess the table format <#guess-table-format>`_
by trying all the supported formats.  If this does not work (for unusually
formatted tables) then one needs give asciitable additional hints about the
format, for example::

   data = asciitable.read('t/nls1_stackinfo.dbout', data_start=2, delimiter='|')
   data = asciitable.read('t/simple.txt', quotechar="'")
   data = asciitable.read('t/simple4.txt', Reader=asciitable.NoHeader, delimiter='|')
   table = ['col1 col2 col3', '1 2 hi', '3 4.2 there']
   data = asciitable.read(table, delimiter=" ")

The |read| function accepts a number of parameters that specify the detailed
table format.  Different Reader classes can define different defaults, so the
descriptions below sometimes mention "typical" default values.  This refers to
the :class:`~asciitable.Basic` reader and other similar Reader classes.

Commonly used parameters for ``read()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**table** : input table 
  There are four ways to specify the table to be read:

  - Name of a file (string)
  - Single string containing all table lines separated by newlines
  - File-like object with a callable read() method
  - List of strings where each list element is a table line

  The first two options are distinguished by the presence of a newline in the string.  
  This assumes that valid file names will not normally contain a newline.

**Reader** : Reader class (default= :class:`~asciitable.BasicReader`)
  This specifies the top-level format of the ASCII table, for example
  if it is a basic character delimited table, fixed format table, or
  a CDS-compatible table, etc.  The value of this parameter must
  be a Reader class.  For basic usage this means one of the 
  built-in :ref:`extension_reader_classes`.  

**numpy** : return a NumPy record array (default=True)
  By default the output from |read| is a 
  `NumPy record array <http://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html>`_ object.
  This powerful container efficiently supports both column-wise and row access to the
  table and comes with the full NumPy stack of array manipulation methods.

  If NumPy is not available or desired then set ``numpy=False``.  The output
  of |read| will then be a dictionary of :class:`~asciitable.Column` objects
  with each key for the corresponding named column.
  
**guess**: try to guess table format (default=True)
  If set to True then |read| will try to guess the table format by cycling
  through a number of possible table format permuations and attemping to read
  the table in each case.  See the `Guess table format`_ section for further details.
  
**delimiter** : column delimiter string
  A one-character string used to separate fields which typically defaults to
  the space character.  Other common values might be "\\s" (whitespace), "," or
  "|" or "\\t" (tab).  A value of "\\s" allows any combination of the tab and
  space characters to delimit columns.

**comment** : regular expression defining a comment line in table
  If the ``comment`` regular expression matches the beginning of a table line then that line
  will be discarded from header or data processing.  For the :class:`~asciitable.Basic` Reader this
  defaults to "\\s*#" (any whitespace followed by #).  

**quotechar** : one-character string to quote fields containing special characters
  This specifies the quote character and will typically be either the single or double
  quote character.  This is can be useful for reading text fields with spaces in a space-delimited
  table.  The default is typically the double quote.

**header_start** : line index for the header line not counting comment lines
  This specifies in the line index where the header line will be found.  Comment lines are
  not included in this count and the counting starts from 0 (first non-comment line has index=0).
  If set to None this indicates that there is no header line and the column names
  will be auto-generated.  The default is dependent on the Reader.

**data_start**: line index for the start of data not counting comment lines
  This specifies in the line index where the data lines begin where the counting starts
  from 0 and does not include comment lines.  The default is dependent on the Reader.

**data_end**: line index for the end of data (can be negative to count from end)
  If this is not None then it allows for excluding lines at the end that are not
  valid data lines.  A negative value means to count from the end, so -1 would 
  exclude the last line, -2 the last two lines, and so on.

**converters**: dict of data type converters
  See the `Converters`_ section for more information.

**names**: list of names corresponding to each data column
  Define the complete list of names for each data column.  This will override
  names found in the header (if it exists).  If not supplied then
  use names from the header or auto-generated names if there is no header.

**include_names**: list of names to include in output
  From the list of column names found from the header or the ``names``
  parameter, select for output only columns within this list.  If not supplied
  then include all names.
  
**exclude_names**: list of names to exlude from output
  Exclude these names from the list of output columns.  This is applied *after*
  the ``include_names`` filtering.  If not specified then no columns are excluded.

**fill_values**: fill value specifier of lists
  This can be used to fill missing values in the table or replace strings with special meaning.
  See the `Replace bad or missing values`_ section for more information and examples.

**fill_include_names**: list of column names, which are affected by ``fill_values``.
  If not supplied, then ``fill_values`` can affect all columns.

**fill_exclude_names**: list of column names, which are not affected by ``fill_values``.
  If not supplied, then ``fill_values`` can affect all columns.

Advanced parameters for ``read()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|read| can accept a few more parameters that allow for code-level customization
of the reading process.  These will be discussed in the `Advanced table reading`_ section.

**data_Splitter**: Splitter class to split data columns

**header_Splitter**: Splitter class to split header columns

**Inputter**: Inputter class

**Outputter**: Outputter class

.. _replace_bad_or_missing_values:

Replace bad or missing values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:mod:`Asciitable` can replace string values in the input data before they are
converted.  The most common use case is probably a table which contains string
values that are not a valid representation of a number, e.g. ``"..."`` for a
missing value or ``""``.  If :mod:`Asciitable` cannot convert all elements in a
column to a numeric type, it will format the column as strings. To avoid this,
``fill_values`` can be used at the string level to fill missing values with the
following syntax, which replaces ``<old>`` with ``<new>`` before the type
conversion is done::

  fill_values = <fill_spec> | [<fill_spec1>, <fill_spec2>, ...]
  <fill_spec> = (<old>, <new>, <optional col name 1>, <optional col name 2>, ...)

Within the ``<fill_spec>`` tuple the ``<old>`` and ``<new>`` values must be
strings.  These two values are then followed by zero or more column names.  If
column names are included the replacement is limited to those columns listed.
If no columns are specified then the replacement is done in every column,
subject to filtering by ``fill_include_names`` and ``fill_exclude_names`` (see
below).

The ``fill_values`` parameter in |read| takes a single ``<fill_spec>`` or a
list of ``<fill_spec>`` tuples.  If several ``<fill_spec>`` apply to a single
occurence of ``<old>`` then the first one determines the ``<new>`` value.  For
instance the following will replace an empty data value in the ``x`` or ``y``
columns with "1e38" while empty values in any other column will get "-999"::

  asciitable.read(table, fill_values=[('', '1e38', 'x', 'y'), ('', '-999')])

The following shows an example where string information needs to be exchanged 
before the conversion to float values happens. Here ``no_rain`` and ``no_snow`` is replaced by ``0.0``::

  table = ['day  rain     snow',    # column names
           #---  -------  --------
           'Mon  3.2      no_snow', 
           'Tue  no_rain  1.1', 
           'Wed  0.3      no_snow']
  asciitable.read(table, fill_values=[('no_rain', '0.0'), ('no_snow', '0.0')])
 
Sometimes these rules apply only to specific columns in the table. Columns can be selected with
``fill_include_names`` or excluded with ``fill_exclude_names``. Also, column names can be
given directly with fill_values::

  asciidata = ['text,no1,no2', 'text1,1,1.',',2,']
  asciitable.read(asciidata, fill_values = ('', 'nan','no1','no2'), delimiter = ',')

Here, the empty value ``''`` in column ``no2`` is replaced by ``nan``, but the ``text``
column remains unaltered. 

If the ``numpy`` module is available, then the default output is a 
`NumPy masked array <http://docs.scipy.org/doc/numpy/reference/maskedarray.html>`_, 
where all values, which were replaced by ``fill_values`` are masked.  See the
description of the :class:`~asciitable.NumpyOutputter` class for information on 
disabling masked arrays.

Guess table format
^^^^^^^^^^^^^^^^^^^^^^
If the ``guess`` parameter in |read| is set to True (which is the default) then
|read| will try to guess the table format by cycling through a number of
possible table format permutations and attemping to read the table in each case.
The first format which succeeds and will be used to read the table. To succeed
the table must be successfully parsed by the Reader and satisfy the following
column requirements:

 * At least two table columns
 * No column names are a float or int number
 * No column names begin or end with space, comma, tab, single quote, double quote, or
   a vertical bar (|). 

These requirements reduce the chance for a false positive where a table is
successfully parsed with the wrong format.  A common situation is a table
with numeric columns but no header row, and in this case ``asciitable`` will
auto-assign column names because of the restriction on column names that 
look like a number.

The order of guessing is shown by this Python code::
  
  for Reader in (Rdb, Tab, Cds, Daophot, Ipac):
      read(Reader=Reader)
  for Reader in (CommentedHeader, BasicReader, NoHeader):
      for delimiter in ("|", ",", " ", "\\s"):
          for quotechar in ('"', "'"):
              read(Reader=Reader, delimiter=delimiter, quotechar=quotechar)

Note that the :class:`~asciitable.FixedWidth` derived-readers are not included
in the default guess sequence (this causes problems), so to read such tables
one must explicitly specify the reader class with the ``Reader`` keyword.

If none of the guesses succeed in reading the table (subject to the column
requirements) a final try is made using just the user-supplied parameters but
without checking the column requirements.  In this way a table with only one
column or column names that look like a number can still be successfully read.

The guessing process respects any values of the Reader, delimiter, and
quotechar parameters that were supplied to the read() function.  Any guesses
that would conflict are skipped.  For example the call::

 dat = asciitable.read(table, Reader=NoHeader, quotechar="'")

would only try the four delimiter possibilities, skipping all the conflicting
Reader and quotechar combinations.

Guessing can be disabled in two ways::

  import asciitable
  data = asciitable.read(table)               # guessing enabled by default
  data = asciitable.read(table, guess=False)  # disable for this call
  asciitable.set_guess(False)                 # set default to False globally
  data = asciitable.read(table)               # guessing disabled
  
Converters
^^^^^^^^^^^^^^

:mod:`Asciitable` converts the raw string values from the table into
numeric data types by using converter functions such as the Python ``int`` and
``float`` functions.  For example ``int("5.0")`` will fail while float("5.0")
will succeed and return 5.0 as a Python float.  

Without NumPy
+++++++++++++++++
The default set of converters
for the :class:`~asciitable.BaseOutputter` class is defined as such::

  default_converters = [asciitable.convert_list(int),
                        asciitable.convert_list(float),
                        asciitable.convert_list(str)]

These take advantage of the :func:`~asciitable.convert_list` function which
returns a 2-element tuple.  The first element is function that will convert 
a list of values to the desired type.  The second element is an :mod:`asciitable` 
class that specifies the type of data produced.  This element should be one of 
:class:`~asciitable.StrType`, :class:`~asciitable.IntType`, or
:class:`~asciitable.FloatType`.  

The conversion code steps through each applicable converter function and tries
to call the function with a column of string values.  If it succeeds without
throwing an exception it will then break out, but otherwise move on to the next
conversion function.

Use the ``converters`` keyword argument in order to force a specific data type
for a column.  This should be a dictionary with keys corresponding to the
column names.  Each dictionary value is a list similar to the
``default_converter``.  For example::

  # col1 is int, col2 is float, col3 is string
  converters = {'col1': [asciitable.convert_list(int)],
                'col2': [asciitable.convert_list(float)],
                'col3': [asciitable.convert_list(str)]}
  read('file.dat', converters=converters)

Note that it is also possible to specify a list of converter functions that
will be tried in order::

  converters = {'col1': [asciitable.convert_list(float),
                         asciitable.convert_list(str)]}
  read('file.dat', converters=converters)

With NumPy
++++++++++++++++

If the ``numpy`` module is available then the
:class:`~asciitable.NumpyOutputter` is selected by default.  In this case  the
default converters are::

    default_converters = [asciitable.convert_numpy(numpy.int),
                          asciitable.convert_numpy(numpy.float),
                          asciitable.convert_numpy(numpy.str)]

These take advantage of the :func:`~asciitable.convert_numpy` function which
returns a 2-element tuple ``(converter_func, converter_type)`` as described in
the previous section.  The type provided to ``convert_numpy()`` must be a valid
`numpy type <http://docs.scipy.org/doc/numpy/user/basics.types.html>`_, for
example ``numpy.int``, ``numpy.uint``, ``numpy.int8``, ``numpy.int64``,
``numpy.float``, ``numpy.float64``, ``numpy.str``.

The converters for each column can be specified with the ``converters``
keyword::

  converters = {'col1': [asciitable.convert_numpy(numpy.uint)],
                'col2': [asciitable.convert_numpy(numpy.float32)]}
  read('file.dat', converters=converters)

Advanced table reading
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This section is not finished.  It will discuss ways of making custom reader
functions and how to write custom ``Reader``, ``Splitter``, ``Inputter`` and
``Outputter`` classes.  For now please look at the examples and especially the
code for the existing :ref:`extension_reader_classes`.

Examples
+++++++++++++++
**Define a custom reader functionally**
::

   def read_rdb_table(table):
       reader = asciitable.Basic()
       reader.header.splitter.delimiter = '\t'
       reader.data.splitter.delimiter = '\t'
       reader.header.splitter.process_line = None  
       reader.data.splitter.process_line = None
       reader.data.start_line = 2

       return reader.read(table)

**Define custom readers by class inheritance**
::

   # Note: Tab and Rdb are already included in asciitable for convenience.
   class Tab(asciitable.Basic):
       def __init__(self):
           asciitable.Basic.__init__(self)
           self.header.splitter.delimiter = '\t'
           self.data.splitter.delimiter = '\t'
           # Don't strip line whitespace since that includes tabs
           self.header.splitter.process_line = None  
           self.data.splitter.process_line = None
           # Don't strip data value spaces since that is significant in TSV tables
           self.data.splitter.process_val = None
           self.data.splitter.skipinitialspace = False

   class Rdb(asciitable.Tab):
       def __init__(self):
           asciitable.Tab.__init__(self)
           self.data.start_line = 2

**Create a custom splitter.process_val function**
::

   # The default process_val() normally just strips whitespace.  
   # In addition have it replace empty fields with -999.
   def process_val(x):
       """Custom splitter process_val function: Remove whitespace at the beginning
       or end of value and substitute -999 for any blank entries."""
       x = x.strip()
       if x == '':
           x = '-999'
       return x

   # Create an RDB reader and override the splitter.process_val function
   rdb_reader = asciitable.get_reader(Reader=asciitable.Rdb)
   rdb_reader.data.splitter.process_val = process_val



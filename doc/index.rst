.. |read| replace:: :func:`~asciitable.read`
.. |write| replace:: :func:`~asciitable.write`
.. _structured array: http://docs.scipy.org/doc/numpy/user/basics.rec.html

Asciitable
======================
An extensible ASCII table reader and writer for Python 2 and 3.

:mod:`Asciitable` can read and write a wide range of ASCII table formats via
built-in `Extension Reader Classes`_:

* :class:`~asciitable.Basic`: basic table with customizable delimiters and header configurations
* :class:`~asciitable.Cds`: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* :class:`~asciitable.CommentedHeader`: column names given in a line that begins with the comment character
* :class:`~asciitable.Daophot`: table from the IRAF DAOphot package
* :class:`~asciitable.Ipac`: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* :class:`~asciitable.Latex`, :class:`~asciitable.AASTex`: LaTeX tables (plain and AASTex)
* :class:`~asciitable.Memory`: table already in memory (list of lists, dict of lists, etc)
* :class:`~asciitable.NoHeader`: basic table with no header where columns are auto-named
* :class:`~asciitable.Rdb`: tab-separated values with an extra line after the column definition line
* :class:`~asciitable.Tab`: tab-separated values

At the top level :mod:`asciitable` looks like many other ASCII table interfaces
since it provides default |read| and |write| functions with long lists of
parameters to accommodate the many variations possible in commonly encountered
ASCII table formats.  Below the hood however :mod:`asciitable` is built on a
modular and extensible class structure.  The basic functionality required for
reading or writing a table is largely broken into independent `base class
elements`_ so that new formats can be accomodated by modifying the underlying
class methods as needed.

:Copyright: Smithsonian Astrophysical Observatory (2010) 
:Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)

Requirements
---------------
* :mod:`asciitable` passes its nosetests for the following platform / Python
  version combinations.  Other combinations may work but have not been
  tried. 

=========== ===================
OS          Python version
=========== ===================
Linux       2.4, 2.6, 2.7, 3.2
MacOS 10.6  2.7
Windows XP  2.7
=========== ===================

* Though not required `NumPy <http://numpy.scipy.org/>`_ is recommended.  
* NumPy versions 1.2 and 1.3 (Python 2) and 1.5 (Python 3) have been tested
  in previous releases, while current testing uses NumPy 1.6.

Download
---------------------------

The latest release of the :mod:`asciitable` package is available on the Python Package Index at
`<http://pypi.python.org/pypi/asciitable>`_.

The latest git repository version is available at `<https://github.com/taldcroft/asciitable>`_ or with::

  git clone git://github.com/taldcroft/asciitable.git

Installation and test
---------------------

The :mod:`asciitable` package includes a number of component modules that must
be made available to the Python interpreter.

Easy way
^^^^^^^^^^^

The easy way to install :mod:`asciitable` is using ``pip install`` or
``easy_install``.  Either one will work, but ``pip`` is the more "modern"
alternative.  The following will download and install the package::

  pip install [--user] asciitable
     ** OR **
  easy_install [--user] asciitable

The ``--user`` option will install :mod:`asciitable` in a local user directory
instead of within the Python installation directory structure.  See the
discussion on `where packages get installed
<http://python4astronomers.github.com/installation/packages.html#where-to-packages-get-installed>`_
for more information.  The ``--user`` option requires Python 2.6 or later.

Less easy way  
^^^^^^^^^^^^^^

Download and untar the package tarball, then change into the source directory::

  tar zxf asciitable-<version>.tar.gz
  cd asciitable-<version>

If you have the `nose <http://somethingaboutorange.com/mrl/projects/nose>`_ module 
installed then at this point you can run the test suite::

  nosetests    # Python 2
  nosetests3   # Python 3

There are several methods for installing.  Choose ONE of them.

**Python site-packages**

If you have write access to the python site-packages directory you can do::

  python setup.py install

**Local user library**

If you running python 2.6 or later the following command installs the
:mod:`asciitable` module to the appropriate local user directory::

  python setup.py install --user

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
  built-in `Extension Reader Classes`_.  

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
code for the existing `Extension Reader Classes`_.

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


Writing tables
--------------

:mod:`Asciitable` is able to write ASCII tables out to a file or file-like
object using the same class structure and basic user interface as for reading
tables.  


Input data formats
^^^^^^^^^^^^^^^^^^^
A number of data formats for the input table are supported:

- `Existing ASCII table with metadata`_ (:class:`~asciitable.BaseReader` object)
- `Data from asciitable.read()`_ (:class:`~asciitable.DictLikeNumpy` object)
- `NumPy structured array`_ or record array
- `Sequence of sequences`_ (row-oriented list of lists)
- `Dict of sequences`_ (column oriented dictionary of lists)

Existing ASCII table with metadata
+++++++++++++++++++++++++++++++++++

The example below highlights that the :func:`~asciitable.get_reader` function
returns a :class:`~asciitable.Reader` object that supports keywords and table
metadata.  The :class:`~asciitable.Reader` object can then be an input to the
:func:`~asciitable.write` function and allow for any associated metadata to be
written.

Note that in the current release there is no support for actually writing the 
available keywords or other metadata, but the infrastructure is available and 
this is the top priority for development.

::

    # Get a Reader object
    table = asciitable.get_reader(Reader=asciitable.Daophot)

    # Read a table from a file.  Return a NumPy record array object and also
    # update column and metadata attributes in the "table" Reader object.
    data = table.read('t/daophot.dat')

    # Write the data in a variety of ways using as input both the NumPy record 
    # array and the higher-level Reader object.
    asciitable.write(table, "table.dat", Writer=asciitable.Tab )
    asciitable.write(table, open("table.dat", "w"), Writer=asciitable.NoHeader )
    asciitable.write(table, sys.stdout, Writer=asciitable.CommentedHeader )
    asciitable.write(table, sys.stdout, Writer=asciitable.Rdb, exclude_names=['CHI'] )

    asciitable.write(table, sys.stdout, formats={'XCENTER': '%12.1f',
                                                 'YCENTER': lambda x: round(x, 1)},
                                        include_names=['XCENTER', 'YCENTER'])


Data from asciitable.read()
+++++++++++++++++++++++++++++

:mod:`Asciitable.read` returns a data object that can be an input to the
|write| function.  If NumPy is available the default data
object type is a NumPy record array.  However it is possible to use
:mod:`asciitable` without NumPy in which case a :class:`~asciitable.DictLikeNumpy` 
object is returned.  This object supports the most basic column and row indexing 
API of a NumPy `structured array`_.  This object can be used as input to the |write| 
function.

::

    table = asciitable.get_reader(Reader=asciitable.Daophot, numpy=False)
    data = table.read('t/daophot.dat')

    asciitable.write(data, sys.stdout)

NumPy structured array
++++++++++++++++++++++++

A NumPy `structured array`_ (aka record array) can serve as input to the |write| function.

::

    data = numpy.zeros((2,), dtype=('i4,f4,a10'))
    data[:] = [(1, 2., 'Hello'), (2, 3., "World")]
    asciitable.write(data, sys.stdout)

Sequence of sequences
+++++++++++++++++++++++++

A doubly-nested structure of iterable objects (e.g. lists or tuples) can serve as input to |write|.  
The outer layer represents rows while the inner layer represents columns.

::

    data = [[1, 2,   3      ], 
            [4, 5.2, 6.1    ], 
            [8, 9,   'hello']]
    asciitable.write(data, 'table.dat')
    asciitable.write(data, 'table.dat', names=['x', 'y', 'z'], exclude_names=['y'])

Dict of sequences
+++++++++++++++++++++++

A dictionary containing iterable objects can serve as input to |write|.  Each
dict key is taken as the column name while the value must be an iterable object
containing the corresponding column values.  Note the difference in output between
this example and the previous example.

::

    data = {'x': [1, 2, 3], 
            'y': [4, 5.2, 6.1], 
            'z': [8, 9, 'hello world']}
    asciitable.write(data, 'table.dat')


Commonly used parameters for ``write()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The |write| function accepts a number of parameters that specify the detailed
output table format.  Different Reader classes can define different defaults, so the
descriptions below sometimes mention "typical" default values.  This refers to
the :class:`~asciitable.Basic` reader and other similar Reader classes.

Some Reader classes, e.g. :class:`~asciitable.Latex` or :class:`~asciitable.AASTex`
accept aditional keywords, that can customize the output further. See the documentation
of these classes for details.

**output** : output specifier
  There are two ways to specify the output for the write operation:

  - Name of a file (string)
  - File-like object (from open(), StringIO, etc)

**table** : input table 
  The are five possible formats for the data table that is to be written:

  - :mod:`Asciitable` Reader object (returned by :func:`~asciitable.get_reader`)
    which has been used to read a table
  - Output from :func:`~asciitable.read` (:class:`~asciitable.DictLikeNumpy`)
  - NumPy `structured array`_ or record array
  - List of lists: e.g. ``[[2, 3], [4, 5], [6, 7]]`` (3 rows, 2 columns)
  - Dict of lists: e.g. ``{'c1': [2, 3, 4], 'c2': [5, 6, 7]}`` (3 rows, 2 columns)

**Writer** : Writer class (default= :class:`~asciitable.Basic`)
  This specifies the top-level format of the ASCII table to be written, for
  example if it is a basic character delimited table, fixed format table, or a
  CDS-compatible table, etc.  The value of this parameter must be a Reader
  class.  For basic usage this means one of the built-in `Extension Reader
  Classes`_.  Note: Reader classes and Writer classes are synonymous, in other
  words Reader classes can also write, but for historical reasons they are
  called Reader classes.

**delimiter** : column delimiter string
  A one-character string used to separate fields which typically defaults to the space character.
  Other common values might be "," or "|" or "\\t".

**comment** : string defining a comment line in table
  For the :class:`~asciitable.Basic` Reader this defaults to "#". 

**formats**: dict of data type converters
  For each key (column name) use the given value to convert the column data to a string.  
  If the format value is string-like then it is used as a Python format statement,
  e.g. '%0.2f' % value.  If it is a callable function then that function
  is called with a single argument containing the column value to be converted.
  Example::

    asciitable.write(table, sys.stdout, formats={'XCENTER': '%12.1f',
                                                 'YCENTER': lambda x: round(x, 1)},

**names**: list of names corresponding to each data column
  Define the complete list of names for each data column.  This will override
  names determined from the data table (if available).  If not supplied then
  use names from the data table or auto-generated names.

**include_names**: list of names to include in output
  From the list of column names found from the data table or the ``names``
  parameter, select for output only columns within this list.  If not supplied
  then include all names.
  
**exclude_names**: list of names to exlude from output
  Exclude these names from the list of output columns.  This is applied *after*
  the ``include_names`` filtering.  If not specified then no columns are excluded.

**fill_values**: fill value specifier of lists
  This can be used to fill missing values in the table or replace values with special meaning.
  The syntax is the same as used on input.
  See the `Replace bad or missing values`_ section for more information on the syntax.
  When writing a table, all values are converted to strings, before any value is replaced. Thus,
  you need to provide the string representation (stripped of whitespace) for each value.
  Example::

    asciitable.write(table, sys.stdout, fill_values = [('nan', 'no data'),
                                                       ('-999.0', 'no data')])

**fill_include_names**: list of column names, which are affected by ``fill_values``.
  If not supplied, then ``fill_values`` can affect all columns.

**fill_exclude_names**: list of column names, which are not affected by ``fill_values``.
  If not supplied, then ``fill_values`` can affect all columns.



Base class elements
----------------------------

The key elements in :mod:`asciitable` are:

* :class:`~asciitable.Column`: Internal storage of column properties and data ()
* :class:`Inputter <asciitable.BaseInputter>`: Get the lines from the table input.
* :class:`Splitter <asciitable.BaseSplitter>`: Split the lines into string column values.
* :class:`Header <asciitable.BaseHeader>`: Initialize output columns based on the table header or user input.
* :class:`Data <asciitable.BaseData>`: Populate column data from the table.
* :class:`Outputter <asciitable.BaseOutputter>`: Convert column data to the specified output format, e.g. `NumPy <http://numpy.scipy.org/>`_ structured array.

Each of these elements is an inheritable class with attributes that control the
corresponding functionality.  In this way the large number of tweakable
parameters is modularized into managable groups.  Where it makes sense these
attributes are actually functions that make it easy to handle special cases.

Asciitable API
==============

.. automodule:: asciitable

Functions
--------------

.. autofunction:: read

.. autofunction:: get_reader

.. autofunction:: write

.. autofunction:: get_writer

.. autofunction:: convert_list

.. autofunction:: convert_numpy

.. autofunction:: set_guess

Core Classes
--------------
.. autoclass:: BaseReader
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseData
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseHeader
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseInputter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseOutputter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseSplitter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: Column
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: DefaultSplitter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: DictLikeNumpy
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: InconsistentTableError
   :show-inheritance:

.. autoclass:: NumpyOutputter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:


Extension Reader Classes
-------------------------

The following classes extend the base Reader functionality to handle different
table formats.  Some, such as the :class:`Basic` Reader class are fairly
general and include a number of configurable attributes.  Others such as
:class:`Cds` or :class:`Daophot` are specialized to read certain well-defined
but idiosyncratic formats.

* :class:`~asciitable.AASTex`: AASTeX `deluxetable` used for AAS journals
* :class:`~asciitable.Basic`: basic table with customizable delimiters and header configurations
* :class:`~asciitable.Cds`: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* :class:`~asciitable.CommentedHeader`: column names given in a line that begins with the comment character
* :class:`~asciitable.Daophot`: table from the IRAF DAOphot package
* :class:`~asciitable.Ipac`: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* :class:`~asciitable.Latex`: LaTeX table with datavalue in the `tabular` environment
* :class:`~asciitable.NoHeader`: basic table with no header where columns are auto-named
* :class:`~asciitable.Rdb`: tab-separated values with an extra line after the column definition line
* :class:`~asciitable.Tab`: tab-separated values

.. autoclass:: AASTex
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: Basic
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: Cds
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: CommentedHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: Daophot
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: Ipac
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: Latex
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: Memory
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: NoHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: Rdb
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: Tab
   :show-inheritance:
   :members:
   :undoc-members:

Other extension classes
-----------------------
These classes provide support for extension readers.

.. autoclass:: asciitable.cds.CdsData
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.cds.CdsHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.basic.CommentedHeaderHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: ContinuationLinesInputter
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.daophot.DaophotHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: FixedWidthSplitter
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.ipac.IpacData
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.ipac.IpacHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.latex.LatexHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.latex.LatexData
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.latex.LatexSplitter
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.latex.AASTexHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.latex.AASTexData
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: asciitable.latex.AASTexHeaderSplitter
   :show-inheritance:
   :members:
   :undoc-members:


.. toctree::
   :maxdepth: 1

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


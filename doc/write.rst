.. _asciitable_write:

.. include:: references.txt

Writing tables
--------------

:mod:`Asciitable` is able to write ASCII tables out to a file or file-like
object using the same class structure and basic user interface as for reading
tables.  


Input data formats
^^^^^^^^^^^^^^^^^^^
A number of data formats for the input table are supported:

- `Dict of sequences`_ (column oriented dictionary of lists)
- `NumPy structured array`_ or record array
- `Sequence of sequences`_ (row-oriented list of lists)
- `Data from asciitable.read()`_ (:class:`~asciitable.DictLikeNumpy` object)
- `Existing ASCII table with metadata`_ (:class:`~asciitable.BaseReader` object)

Dict of sequences
+++++++++++++++++++++++

A dictionary containing iterable objects can serve as input to |write|.  Each
dict key is taken as the column name while the value must be an iterable object
containing the corresponding column values.  The ``names`` keyword argument
is needed if you want a certain column order, otherwise it will be alphabetical
by default.

::

    data = {'x': [1, 2, 3], 
            'y': [4, 5.2, 6.1], 
            'z': [8, 9, 'hello world']}
    asciitable.write(data, 'table.dat', names=['x', 'y', 'z'])

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


Data from asciitable.read()
++++++++++++++++++++++++++++++++++++++++++++

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
  class.  For basic usage this means one of the built-in :ref:`extension_reader_classes`.
  Note: Reader classes and Writer classes are synonymous, in other
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
  See the :ref:`replace_bad_or_missing_values` section for more information on the syntax.
  When writing a table, all values are converted to strings, before any value is replaced. Thus,
  you need to provide the string representation (stripped of whitespace) for each value.
  Example::

    asciitable.write(table, sys.stdout, fill_values = [('nan', 'no data'),
                                                       ('-999.0', 'no data')])

**fill_include_names**: list of column names, which are affected by ``fill_values``.
  If not supplied, then ``fill_values`` can affect all columns.

**fill_exclude_names**: list of column names, which are not affected by ``fill_values``.
  If not supplied, then ``fill_values`` can affect all columns.




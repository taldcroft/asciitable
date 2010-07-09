.. |read| replace:: :func:`~asciitable.read`

:mod:`asciitable`
======================
An extensible ASCII table reader.

:mod:`Asciitable` can read a wide range of ASCII table formats via built-in `Extension Reader Classes`_:

* :class:`~asciitable.Basic`: basic table with customizable delimiters and header configurations
* :class:`~asciitable.Cds`: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* :class:`~asciitable.CommentedHeader`: column names given in a line that begins with the comment character
* :class:`~asciitable.Daophot`: table from the IRAF DAOphot package
* :class:`~asciitable.Ipac`: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* :class:`~asciitable.NoHeader`: basic table with no header where columns are auto-named
* :class:`~asciitable.Rdb`: tab-separated values with an extra line after the column definition line
* :class:`~asciitable.Tab`: tab-separated values

At the top level :mod:`asciitable` looks like many other ASCII table readers
since it provides a default |read| function with a long list of parameters to
accommodate the many variations possible in commonly encountered ASCII table
formats.  Below the hood however :mod:`asciitable` is built on a modular and
extensible class structure.  The basic functionality required for reading a table
is largely broken into independent `base class elements`_ so that new formats
can be accomodated by modifying the underlying class methods as needed.

:Copyright: Smithsonian Astrophysical Observatory (2010) 
:Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)

Requirements
---------------
* :mod:`asciitable` has been tested with Python 2.4, 2.5 and 2.6.  It might work with other versions.
* Though not required `NumPy <http://numpy.scipy.org/>`_ is highly recommended.  Version 1.3.0 has been tested.

Download
---------------------------

The latest release of the :mod:`asciitable` package is available in the
`<http://cxc.harvard.edu/contrib/asciitable/downloads>`_ directory as
``asciitable.tar.gz``.  Previous releases are also available there.

The latest mercurial repository version is available on google code::

  hg clone https://asciitable.googlecode.com/hg/ asciitable 

Installation
--------------

The :mod:`asciitable` package includes a single module that must be made
available to the Python interpreter.  The first step is to untar the package
tarball and change into the source directory.  ::

  tar zxvf asciitable.tar.gz
  cd asciitable-<version>

There are several methods for installing.  Choose ONE of them.

**Python site-packages**

If you have write access to the python site-packages directory you can do::

  python setup.py install

**Local user library**

If you running python 2.6 or later the following command installs the :mod:`asciitable` module to the appropriate directory in 
``$HOME/.local/lib/``::

  python setup.py install --user

**PYTHONPATH**

An alternate and simple installation strategy is to just leave the module file in
the source directory and set the ``PYTHONPATH`` environment variable to point
to the source directory::

  setenv PYTHONPATH $PWD

This method is fine in the short term but you always have to make sure
``PYTHONPATH`` is set appropriately (perhaps in your ~/.cshrc file).  And if you
start doing much with Python you will have ``PYTHONPATH`` conflicts and things
will get messy.

Basic Usage with ``read()``
----------------------------
The majority of commonly encountered ASCII tables can be read with the |read|
function using one of the `Extension Reader Classes`_ supplied with :mod:`asciitable`.  
Here are a few very simple examples to give the basic flavor::

   import asciitable
   data = asciitable.read('t/nls1_stackinfo.dbout', data_start=2, delimiter='|')
   data = asciitable.read('t/simple.txt', quotechar="'")
   data = asciitable.read('t/simple4.txt', Reader=asciitable.NoHeader, delimiter='|')
   table = ['col1 col2 col3', '1 2 hi', '3 4.2 there']
   data = asciitable.read(table)

The |read| function accepts a number of parameters that specify the detailed
table format.  Different Reader classes can define different defaults, so the
descriptions below sometimes mention "typical" default values.  This refers to
the :class:`~asciitable.Basic` reader and other similar Reader classes.

Commonly used parameters for ``read()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**table** : input table 
  There are three ways to specify the table to be read:

  - Name of a file (string)
  - Single string containing all table lines separated by newlines
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
  
**delimiter** : column delimiter string
  A one-character string used to separate fields which typically defaults to the space character.
  Other common values might be "," or "|" or "\\t".  Note that when reading a table with 
  tab-separated fields one needs to disable the whitespace stripping that normally 
  takes place.  For this reason the separate :class:`~asciitable.Tab` reader is provided that
  handles these specifics.

**comment** : regular expression defining a comment line in table
  If the ``comment`` regular expression matches the beginning of a table line then that line
  will be discarded from header or data processing.  For the :class:`~asciitable.Basic` Reader this
  defaults to "\s*#" (any whitespace followed by #).  

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

Advanced parameters for ``read()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|read| can accept a few more parameters that allow for code-level customization
of the reading process.  These will be discussed in the `Advanced Usage`_ section.

**data_Splitter**: Splitter class to split data columns

**header_Splitter**: Splitter class to split header columns

**Inputter**: Inputter class

**Outputter**: Outputter class

Converters
-----------

Normally :mod:`asciitable` converts the raw string values from the table into
numeric data types by trying to convert the values using the Python ``int`` and
``float`` functions.  For example ``int("5.0")`` will fail while float("5.0")
will succeed and return 5.0 as a Python float.  The default set of converters
is defined as such::

  default_converter = [lambda vals: [int(x) for x in vals],
                       lambda vals: [float(x) for x in vals],
                       lambda vals: vals]

This is a list of lambda functions.  Each function takes as an argument a list
of string values for a single column as read from the table.  It uses a list
comprehension to apply the ``int`` or ``float`` function and return the result
as a list.  The conversion code steps through each lambda function and tries to
call the function with a column of string values.  If it succeeds without
throwing an exception then break out, but otherwise move on to the next
conversion lambda function.  For the ``default_converter`` list there is a
catch-all at the end and so a column that is neither ``int`` nor ``float`` is
returned as ``string``.

Use the ``converters`` keyword argument in order to force a specific data type
for a column.  This should be a dictionary with keys corresponding to the
column names.  Each dictionary value is a list similar to the
``default_converter``.  For example::

  # col1 is int, col2 is float, col3 is string
  converters = dict(col1=[lambda vals: [int(x) for x in vals]],
                    col2=[lambda vals: [float(x) for x in vals]],
                    col3=[lambda vals: vals])
  read('file.dat', converters=converters)

There is currently no easy way to have fine-grained control of the final NumPy
data type, i.e. whether you get int8 versus int64 etc.

Specifying the dictionary value as a list allows the choice of multiple 
converters that will be tried in succession.  For convenience it is
also possible to specify a converter without a list::

  converters = dict(col1=[lambda vals: [int(x) for x in vals],
                          lambda vals: vals],
                    col2=lambda vals: [float(x) for x in vals],
                    col3=lambda vals: vals)
  read('file.dat', converters=converters)

Advanced Usage
--------------

This section is not finished.  It will discuss ways of making custom reader
functions and how to write custom ``Reader``, ``Splitter``, ``Inputter`` and
``Outputter`` classes.  For now please look at the examples and especially the
code for the existing `Extension Reader Classes`_.

Examples
^^^^^^^^^^
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

asciitable API
==============

.. automodule:: asciitable

Functions
--------------

.. autofunction:: read

.. autofunction:: get_reader

.. autofunction:: convert_numpy

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

.. autoclass:: InconsistentTableError
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

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

* :class:`~asciitable.Basic`: basic table with customizable delimiters and header configurations
* :class:`~asciitable.Cds`: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* :class:`~asciitable.CommentedHeader`: column names given in a line that begins with the comment character
* :class:`~asciitable.Daophot`: table from the IRAF DAOphot package
* :class:`~asciitable.Ipac`: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* :class:`~asciitable.NoHeader`: basic table with no header where columns are auto-named
* :class:`~asciitable.Rdb`: tab-separated values with an extra line after the column definition line
* :class:`~asciitable.Tab`: tab-separated values

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

.. autoclass:: CdsData
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: CdsHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: CommentedHeaderHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: ContinuationLinesInputter
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: DaophotHeader
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: FixedWidthSplitter
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: IpacData
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: IpacHeader
   :show-inheritance:
   :members:
   :undoc-members:

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


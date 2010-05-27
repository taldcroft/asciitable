:mod:`asciitable`
======================
An extensible ASCII table reader.

At the top level :mod:`asciitable` looks like many other ASCII table readers since
it provides a default :func:`~asciitable.read` function with a long list of parameters to
accommodate the many variations possible in commonly encountered ASCII table
formats.  But unlike other monolithic table reader implementations,
:mod:`asciitable` is based on a modular and extensible class structure.  Formats
that cannot be handled by the existing hooks in the ``read()`` function can be
accomodated by modifying the underlying class methods as needed.

:mod:`Asciitable` can read a wide range of ASCII table formats via built-in `Extension Reader Classes`_ (derived from `base class elements`_):

* :class:`~asciitable.Basic`: basic table with customizable delimiters and header configurations
* :class:`~asciitable.Cds`: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* :class:`~asciitable.CommentedHeader`: column names given in a line that begins with the comment character
* :class:`~asciitable.Daophot`: table from the IRAF DAOphot package
* :class:`~asciitable.Ipac`: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* :class:`~asciitable.NoHeader`: basic table with no header where columns are auto-named
* :class:`~asciitable.Rdb`: tab-separated values with an extra line after the column definition line
* :class:`~asciitable.Tab`: tab-separated values

:Copyright: Smithsonian Astrophysical Observatory (2010) 
:Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)

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

Requirements
---------------
* :mod:`asciitable` has been tested with Python 2.4, 2.5 and 2.6.  It might work with other versions.
* Though not required `NumPy <http://numpy.scipy.org/>`_ is highly recommended.  Version 1.3.0 has been tested.

Download
---------------------------
The :mod:`asciitable` package is available in the `<http://cxc.harvard.edu/contrib/asciitable/downloads>`_ directory as
``asciitable-<version>.tar.gz``.  

Examples
--------
In most cases an ASCII table can be read with the ``read()`` function by
specifying the delimiter and the location of the header and data.  The
following examples use test files providing the in source distribution.  The
``test.py`` file also contains numerous other examples showing how to read the
test datasets in the ``t/`` directory of the source distribution.

.. code-block:: python

   import asciitable
   data = asciitable.read('t/nls1_stackinfo.dbout', data_start=2, delimiter='|')
   data = asciitable.read('t/simple.txt' quotechar="'")

   # Read a file with no header using the NoHeader Reader class.  Column names are auto-generated.
   data = asciitable.read('t/simple4.txt', Reader=asciitable.NoHeader, delimiter='|')

   table = ['col1 col2 col3', '1 2 hi', '3 4.2 there']
   data = asciitable.read(table)

   # Define a custom reader functionally
   def read_rdb_table(table):
       reader = asciitable.Basic()
       reader.header.splitter.delimiter = '\t'
       reader.data.splitter.delimiter = '\t'
       reader.header.splitter.process_line = None  
       reader.data.splitter.process_line = None
       reader.data.start_line = 2

       return reader.read(table)

   # Define custom readers by class inheritance.
   # Note: Tab and Rdb are already included in asciitable for convenience.
   class Tab(asciitable.Basic):
       def __init__(self):
           asciitable.Basic.__init__(self)
           self.header.splitter.delimiter = '\t'
           self.data.splitter.delimiter = '\t'
           # Don't strip line whitespace since that includes tabs
           self.header.splitter.process_line = None  
           self.data.splitter.process_line = None

   class Rdb(asciitable.Tab):
       def __init__(self):
           asciitable.Tab.__init__(self)
           self.data.start_line = 2

   # Create a custom splitter.process_val function.  The default normally just
   # strips whitespace.  In addition have it replace empty fields with -999.
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


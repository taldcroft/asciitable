:mod:`asciitable`
======================
An extensible ASCII table reader.

At the top level ``asciitable`` looks like many other ASCII table readers since
it provides a default ``read()`` function with a long list of parameters to accommodate
the many variations possible in commonly encountered ASCII table formats.  But unlike
other monolithic table reader implementations, ``asciitable`` is based on a modular
and extensible class structure.  If a new format is encountered that cannot be handled
by the existing hooks in the ``read()`` function then underlying class methods can be 
tweaked as needed.  

The key elements in ``asciitable`` are:

* **Column**: Internal storage of column properties and data.
* **Inputter**: Get the lines from the table input.
* **Splitter**: Split the lines into string column values.
* **Header**: Initialize output columns based on the table header or user input.
* **Data**: Populate column data from the table.
* **Outputter**: Convert column data to the specified output format, e.g. numpy structured array.

Each of these elements is an inheritable class with attributes that control the
corresponding functionality.  In this way the large number of tweakable
parameters is modularized into managable groups.  Where it makes sense these
attributes are actually functions that make it easy to handle special cases.

Requirements
---------------
* ``asciitable`` has been tested with Python 2.4, 2.5 and 2.6.  It might work with other versions.

Download
---------------------------
The :mod:`asciitable` package is available in the `<http://cxc.harvard.edu/contrib/asciitable/downloads>`_ directory as
``asciitable-<version>.tar.gz``.  

Examples
--------
In most cases an ASCII table can be read with the ``read()`` function by specifying the 
delimiter and the location of the header and data.  The following examples use test files
providing the in source distribution.::

  import asciitable
  data = asciitable.read('t/nls1_stackinfo.dbout', data_start=2, delimiter='|')
  data = asciitable.read('t/simple.txt' quotechar="'")

  # Read a file with no header using the NoHeaderReader.  Column names are auto-generated.
  data = asciitable.read('t/simple4.txt', Reader=asciitable.NoHeaderReader, delimiter='|')

  table = ['col1 col2 col3', '1 2 hi', '3 4.2 there']
  data = asciitable.read(table)

  # Define a custom reader functionally
  def read_rdb_table(table):
      reader = asciitable.BasicReader()
      reader.header.splitter.delimiter = '\t'
      reader.data.splitter.delimiter = '\t'
      reader.header.splitter.process_line = None  
      reader.data.splitter.process_line = None
      reader.data.start_line = 2

      return reader.read(table)

  # Define custom readers by class inheritance.
  # Note: TabReader and RdbReader are already included in asciitable for convenience.
  class TabReader(BasicReader):
      def __init__(self):
          BasicReader.__init__(self)
          self.header.splitter.delimiter = '\t'
          self.data.splitter.delimiter = '\t'
          # Don't strip line whitespace since that includes tabs
          self.header.splitter.process_line = None  
          self.data.splitter.process_line = None

  class RdbReader(TabReader):
      def __init__(self):
          TabReader.__init__(self)
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
  rdb_reader = asciitable.get_reader(Reader=asciitable.RdbReader)
  rdb_reader.data.splitter.process_val = process_val


More complicated examples are provided in the nose testing file ``test.py`` in the source
distribution.

.. automodule:: asciitable

Functions
----------

.. autofunction:: read

.. autofunction:: get_reader

.. autofunction:: convert_numpy

Classes
--------
.. autoclass:: BaseReader
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BasicReader
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: NoHeaderReader
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: TabReader
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: RdbReader
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: Column
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseInputter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseSplitter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: DefaultSplitter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: TextSimpleSplitter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseHeader
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseData
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: BaseOutputter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: ListOutputter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: NumpyOutputter
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: InconsistentTableError
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


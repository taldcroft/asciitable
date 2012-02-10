.. include:: references.txt

.. _base_class_elements:

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

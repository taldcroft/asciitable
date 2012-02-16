.. include:: references.txt

===============================
Asciitable
===============================
An extensible ASCII table reader and writer for Python 2 and 3.

The :mod:`asciitable` packge can read and write a wide range of ASCII table
formats via built-in :ref:`extension_reader_classes`:

* :class:`~asciitable.Basic`: basic table with customizable delimiters and header configurations
* :class:`~asciitable.Cds`: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* :class:`~asciitable.CommentedHeader`: column names given in a line that begins with the comment character
* :class:`~asciitable.Daophot`: table from the IRAF DAOphot package
* :class:`~asciitable.FixedWidth`: table with fixed-width columns (:ref:`fixed_width_gallery`)
* :class:`~asciitable.Ipac`: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* :class:`~asciitable.Latex`, :class:`~asciitable.AASTex`: LaTeX tables (plain and AASTex)
* :class:`~asciitable.Memory`: table already in memory (list of lists, dict of lists, etc)
* :class:`~asciitable.NoHeader`: basic table with no header where columns are auto-named
* :class:`~asciitable.Rdb`: tab-separated values with an extra line after the column definition line
* :class:`~asciitable.Tab`: tab-separated values

The :mod:`asciitable` package is built on a modular and extensible class
structure with independent :ref:`base_class_elements` so that new formats can
be easily accomodated.

Contents:

.. include:: toc.txt


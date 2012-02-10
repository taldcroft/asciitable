.. include:: references.txt

Asciitable
======================
An extensible ASCII table reader and writer for Python 2 and 3.

:mod:`Asciitable` can read and write a wide range of ASCII table formats via
built-in :ref:`extension_reader_classes`:

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

At the top level :mod:`asciitable` looks like many other ASCII table interfaces
since it provides default |read| and |write| functions with long lists of
parameters to accommodate the many variations possible in commonly encountered
ASCII table formats.  Below the hood however :mod:`asciitable` is built on a
modular and extensible class structure.  The basic functionality required for
reading or writing a table is largely broken into independent :ref:`base_class_elements` so that new formats can be accomodated by modifying the underlying
class methods as needed.

.. only:: asciitable

   .. toctree::
      :maxdepth: 2

      install
      read
      write
      base_classes
      fixed_width_gallery
      ascii_api

   :Copyright: Smithsonian Astrophysical Observatory (2011) 
   :Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)

.. only:: astropy

   .. toctree::
      :maxdepth: 2

      read
      write
      base_classes
      fixed_width_gallery
      ascii_api




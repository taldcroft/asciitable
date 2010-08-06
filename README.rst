asciitable
======================
An extensible ASCII table reader.

Asciitable can read a wide range of ASCII table formats via built-in Extension Reader Classes:

* ``Basic``: basic table with customizable delimiters and header configurations
* ``Cds``: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* ``CommentedHeader``: column names given in a line that begins with the comment character
* ``Daophot``: table from the IRAF DAOphot package
* ``Ipac``: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* ``NoHeader``: basic table with no header where columns are auto-named
* ``Rdb``: tab-separated values with an extra line after the column definition line
* ``Tab``: tab-separated values

At the top level :mod:`asciitable` looks like many other ASCII table readers
since it provides a default |read| function with a long list of parameters to
accommodate the many variations possible in commonly encountered ASCII table
formats.  Below the hood however :mod:`asciitable` is built on a modular and
extensible class structure.  The basic functionality required for reading a table
is largely broken into independent `base class elements`_ so that new formats
can be accomodated by modifying the underlying class methods as needed.

:Copyright: Smithsonian Astrophysical Observatory (2010) 
:Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)

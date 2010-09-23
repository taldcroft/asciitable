asciitable
======================
An extensible ASCII table reader and writer for Python 2 and 3.

Asciitable can read and write a wide range of ASCII table formats via built-in
Extension Reader Classes:

* `Basic`: basic table with customizable delimiters and header configurations
* `Cds`: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* `CommentedHeader`: column names given in a line that begins with the comment character
* `Daophot`: table from the IRAF DAOphot package
* `Ipac`: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* `Memory`: table already in memory (list of lists, dict of lists, etc)
* `NoHeader`: basic table with no header where columns are auto-named
* `Rdb`: tab-separated values with an extra line after the column definition line
* `Tab`: tab-separated values

At the top level asciitable looks like many other ASCII table interfaces
since it provides default read() and write() functions with long lists of
parameters to accommodate the many variations possible in commonly encountered
ASCII table formats.  Below the hood however asciitable is built on a
modular and extensible class structure.  The basic functionality required for
reading or writing a table is largely broken into independent base class
elements so that new formats can be accomodated by modifying the underlying
class methods as needed.

:Copyright: Smithsonian Astrophysical Observatory (2010) 
:Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)



from distutils.core import setup
import os

long_description = """
Asciitable can read and write a wide range of ASCII table formats via built-in
Extension Reader Classes:

* **Basic**: basic table with customizable delimiters and header configurations
* **Cds**: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* **CommentedHeader**: column names given in a line that begins with the comment character
* **Daophot**: table from the IRAF DAOphot package
* **Ipac**: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* **Memory**: table already in memory (list of lists, dict of lists, etc)
* **NoHeader**: basic table with no header where columns are auto-named
* **Rdb**: tab-separated values with a column types line after the column names line
* **Tab**: tab-separated values

At the top level asciitable looks like many other ASCII table interfaces
since it provides default read() and write() functions with long lists of
parameters to accommodate the many variations possible in commonly encountered
ASCII table formats.  Below the hood however asciitable is built on a
modular and extensible class structure.  The basic functionality required for
reading or writing a table is largely broken into independent base class
elements so that new formats can be accomodated by modifying the underlying
class methods as needed.
"""

version = open(os.path.join(os.path.dirname(__file__), 'VERSION')).read().strip()

setup(name='asciitable',
      version=version,
      description='Extensible ASCII table reader and writer',
      long_description=long_description,
      author='Tom Aldcroft',
      author_email='aldcroft@head.cfa.harvard.edu',
      url='http://cxc.harvard.edu/contrib/asciitable',
      license='BSD',
      platforms=['any'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Topic :: Scientific/Engineering :: Astronomy',
          'Topic :: Scientific/Engineering :: Physics',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          ],
      py_modules=['asciitable'],
      )

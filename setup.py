from distutils.core import setup
import os

long_description = """
At the top level **asciitable** looks like many other ASCII table readers since
it provides a default ``read()`` function with a long list of parameters to
accommodate the many variations possible in commonly encountered ASCII table
formats.  But unlike other monolithic table reader implementations,
**asciitable** is based on a modular and extensible class structure.  Formats
that cannot be handled by the existing hooks in the ``read()`` function can be
accomodated by modifying the underlying class methods as needed.

**Asciitable** can read a wide range of ASCII table formats via built-in Extension Reader Classes:

* **Basic**: basic table with customizable delimiters and header configurations
* **Cds**: `CDS format table <http://vizier.u-strasbg.fr/doc/catstd.htx>`_ (also Vizier and ApJ machine readable tables)
* **CommentedHeader**: column names given in a line that begins with the comment character
* **Daophot**: table from the IRAF DAOphot package
* **Ipac**: `IPAC format table <http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html>`_
* **NoHeader**: basic table with no header where columns are auto-named
* **Rdb**: tab-separated values with an extra line after the column definition line
* **Tab**: tab-separated values

"""

version = open(os.path.join(os.path.dirname(__file__), 'VERSION')).read().strip()

setup(name='asciitable',
      version=version,
      description='Extensible ASCII table reader',
      long_description=long_description,
      author='Tom Aldcroft',
      author_email='aldcroft@head.cfa.harvard.edu',
      url='http://cxc.harvard.edu/contrib/asciitable',
      download_url='http://cxc.harvard.edu/contrib/asciitable/downloads',
      license='BSD',
      platforms=['any'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Topic :: Scientific/Engineering :: Astronomy',
          'Topic :: Scientific/Engineering :: Physics',
          ],
      py_modules=['asciitable'],
      use_2to3 = True,
      )

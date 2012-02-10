Requirements
---------------
* :mod:`asciitable` passes its nosetests for the following platform / Python
  version combinations.  Other combinations may work but have not been
  tried. 

=========== ===================
OS          Python version
=========== ===================
Linux       2.4, 2.6, 2.7, 3.2
MacOS 10.6  2.7
Windows XP  2.7
=========== ===================

* Though not required `NumPy <http://numpy.scipy.org/>`_ is recommended.  
* NumPy versions 1.2 and 1.3 (Python 2) and 1.5 (Python 3) have been tested
  in previous releases, while current testing uses NumPy 1.6.

Download
---------------------------

The latest release of the :mod:`asciitable` package is available on the Python Package Index at
`<http://pypi.python.org/pypi/asciitable>`_.

The latest git repository version is available at `<https://github.com/taldcroft/asciitable>`_ or with::

  git clone git://github.com/taldcroft/asciitable.git

Installation and test
---------------------

The :mod:`asciitable` package includes a number of component modules that must
be made available to the Python interpreter.

Easy way
^^^^^^^^^^^

The easy way to install :mod:`asciitable` is using ``pip install`` or
``easy_install``.  Either one will work, but ``pip`` is the more "modern"
alternative.  The following will download and install the package::

  pip install [--user] asciitable
     ** OR **
  easy_install [--user] asciitable

The ``--user`` option will install :mod:`asciitable` in a local user directory
instead of within the Python installation directory structure.  See the
discussion on `where packages get installed
<http://python4astronomers.github.com/installation/packages.html#where-to-packages-get-installed>`_
for more information.  The ``--user`` option requires Python 2.6 or later.

Less easy way  
^^^^^^^^^^^^^^

Download and untar the package tarball, then change into the source directory::

  tar zxf asciitable-<version>.tar.gz
  cd asciitable-<version>

If you have the `nose <http://somethingaboutorange.com/mrl/projects/nose>`_ module 
installed then at this point you can run the test suite::

  nosetests    # Python 2
  nosetests3   # Python 3

There are several methods for installing.  Choose ONE of them.

**Python site-packages**

If you have write access to the python site-packages directory you can do::

  python setup.py install

**Local user library**

If you running python 2.6 or later the following command installs the
:mod:`asciitable` module to the appropriate local user directory::

  python setup.py install --user


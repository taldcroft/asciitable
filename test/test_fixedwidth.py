import re
import glob
from nose.tools import *

import asciitable
if asciitable.has_numpy:
    import numpy as np

from test.common import has_numpy_and_not_has_numpy, has_numpy

@has_numpy_and_not_has_numpy
def test_read_1(numpy):
    """Nice, typical fixed format table"""
    table = """
# comment (with blank line above)
|  col1  |  col2   |
|  1.2   | "hello" |
|  2.4   |'s worlds|
"""
    reader = asciitable.get_reader(Reader=asciitable.FixedWidth)
    dat = reader.read(table)
    print dat
    assert_equal(reader.header.colnames, ('col1', 'col2'))
    assert_almost_equal(dat[1][0], 2.4)
    assert_equal(dat[0][1], '"hello"')
    assert_equal(dat[1][1], "'s worlds")

@has_numpy_and_not_has_numpy
def test_read_2(numpy):
    """Weird input table with data values chopped by col extent """
    table = """
  col1  |  col2 |
  1.2       "hello" 
  2.4   sdf's worlds
"""
    reader = asciitable.get_reader(Reader=asciitable.FixedWidth)
    dat = reader.read(table)
    print dat
    assert_equal(reader.header.colnames, ('col1', 'col2'))
    assert_almost_equal(dat[1][0], 2.4)
    assert_equal(dat[0][1], '"hel')
    assert_equal(dat[1][1], "df's wo")
    
@has_numpy_and_not_has_numpy
def test_read_3(numpy):
    """Table with double delimiters"""
    table = """
|| Name ||   Phone ||         TCP||
|  John  | 555-1234 |192.168.1.10X|
|  Mary  | 555-2134 |192.168.1.12X|
|   Bob  | 555-4527 | 192.168.1.9X|
"""
    dat = asciitable.read(table, Reader=asciitable.FixedWidth, guess=False)
    print dat
    assert_equal(tuple(dat.dtype.names), ('Name', 'Phone', 'TCP'))
    assert_equal(dat[1][0], "Mary")
    assert_equal(dat[0][1], "555-1234")
    assert_equal(dat[2][2], "192.168.1.9")
    

    # WRITE THIS TO test_fixedwidth.py and commit.

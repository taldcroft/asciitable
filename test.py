import re
import glob
from nose.tools import *

import asciitable
try:
    import numpy
    has_numpy = True
except ImportError:
    has_numpy = False
    

# Set up information about the columns, number of rows, and reader params to
# read a bunch of test files and verify columns and number of rows
cols = {
    "t/short.tab"      : ('agasc_id', 'n_noids', 'n_obs'),
    "t/short.rdb"      : ('agasc_id', 'n_noids', 'n_obs'),
    "t/apostrophe.tab" : ('agasc_id', 'n_noids', 'n_obs'),
    "t/apostrophe.rdb" : ('agasc_id', 'n_noids', 'n_obs'),
    "t/simple3.txt"    : ('obsid', 'redshift', 'X', 'Y', 'object', 'rad'),
    "t/simple4.txt"    : ('col1', 'col2', 'col3', 'col4', 'col5', 'col6'),
    "t/test4.dat"      : ('zabs1.nh', 'p1.gamma', 'p1.ampl', 'statname', 'statval'),
    "t/simple.txt"     : ('test 1a', 'test2', 'test3', 'test4'),
    "t/simple2.txt"    : ('obsid', 'redshift', 'X', 'Y', 'object', 'rad'),
    "t/nls1_stackinfo.dbout" : ('', 'objID', 'osrcid', 'xsrcid', 'SpecObjID', 'ra', 'dec',
                                  'obsid', 'ccdid', 'z', 'modelMag_i',
                                  'modelMagErr_i', 'modelMag_r', 'modelMagErr_r', 'expo',
                                  'theta', 'rad_ecf_39', 'detlim90', 'fBlim90'),
    }
nrows = {
    "t/short.tab" : 7,
    "t/short.rdb" : 7,
    "t/apostrophe.tab" : 3,
    "t/apostrophe.rdb" : 2,
    "t/simple3.txt" : 2,
    "t/simple4.txt" : 3,
    "t/test4.dat" : 1172,
    "t/simple.txt" : 2,
    "t/simple2.txt" : 3,
    "t/nls1_stackinfo.dbout" : 58,
    }

opt = {
    't/short.rdb' : {'Reader': asciitable.RdbReader},
    't/short.tab' : {'Reader': asciitable.TabReader},
    't/apostrophe.rdb' : {'Reader': asciitable.RdbReader},
    't/apostrophe.tab' : {'Reader': asciitable.TabReader},
    't/nls1_stackinfo.dbout' : {'data_start': 2, 'delimiter': '|'},
    't/simple.txt' : {'quotechar': "'"},
    't/simple2.txt' : {'delimiter': '|'},
    't/simple3.txt' : {'delimiter': '|'},
    't/simple4.txt' : {'Reader': asciitable.NoHeaderReader, 'delimiter': '|'},
    }    

def test_read_all_files_numpy():
    for f in glob.glob('t/*'):
        if f in cols:
            print 'Reading', f
            options = opt.get(f, {})
            table = asciitable.read(f, **options)
            assert_equal(table.dtype.names, cols[f])
            assert_equal(len(table), nrows[f])

def test_read_all_files_list():
    for f in glob.glob('t/*'):
        if f in cols:
            print 'Reading', f
            options = opt.get(f, {})
            table = asciitable.read(f, numpy=False, **options)
            assert_equal(set(table.keys()), set(cols[f]))
            for colval in table.values():
                assert_equal(len(colval.data), nrows[f])

@raises(asciitable.InconsistentTableError)
def test_wrong_quote():
    table = asciitable.read('t/simple.txt')

@raises(asciitable.InconsistentTableError)
def test_extra_data_col():
    table = asciitable.read('t/bad.txt')

@raises(asciitable.InconsistentTableError)
def test_extra_data_col():
    table = asciitable.read('t/simple5.txt', delimiter='|')

@raises(IOError)
def test_missing_file():
    table = asciitable.read('does_not_exist')

def test_set_names():
    names = ('c1','c2','c3', 'c4', 'c5', 'c6')
    include_names = ('c1', 'c3')
    exclude_names = ('c4', 'c5', 'c6')
    data = asciitable.read('t/simple3.txt', names=names, delimiter='|')
    assert_equal(data.dtype.names, names)

def test_set_include_names():
    names = ('c1','c2','c3', 'c4', 'c5', 'c6')
    include_names = ('c1', 'c3')
    data = asciitable.read('t/simple3.txt', names=names, include_names=include_names, delimiter='|')
    assert_equal(data.dtype.names, include_names)

def test_set_exclude_names():
    exclude_names = ('Y', 'object')
    data = asciitable.read('t/simple3.txt', exclude_names=exclude_names, delimiter='|')
    assert_equal(data.dtype.names, ('obsid', 'redshift', 'X', 'rad'))

def test_custom_process_line():
    def process_line(line):
        line_out = re.sub(r'^\|\s*', '', line.strip())
        return line_out
    reader = asciitable.get_reader(data_start=2, delimiter='|')
    reader.header.splitter.process_line = process_line
    reader.data.splitter.process_line = process_line
    data = reader.read('t/nls1_stackinfo.dbout')
    assert_equal(data.dtype.names, cols["t/nls1_stackinfo.dbout"][1:])

def test_custom_splitters():
    reader = asciitable.get_reader()
    reader.header.splitter = asciitable.BaseSplitter()
    reader.data.splitter = asciitable.BaseSplitter()
    f = 't/test4.dat'
    data = reader.read(f)
    assert_equal(data.dtype.names, cols[f])
    assert_equal(len(data), nrows[f])
    assert_almost_equal(data.field('zabs1.nh')[2], 0.0839710433091)
    assert_almost_equal(data.field('p1.gamma')[2], 1.25997502704)
    assert_almost_equal(data.field('p1.ampl')[2], 0.000696444029148)
    assert_equal(data.field('statname')[2], 'chi2modvar')
    assert_almost_equal(data.field('statval')[2], 497.56468441)
    
def test_start_end():
    data = asciitable.read('t/test5.dat', header_start=1, data_start=3, data_end=-5)
    assert_equal(len(data), 13)
    assert_equal(data.field('statname')[0], 'chi2xspecvar')
    assert_equal(data.field('statname')[-1], 'chi2gehrels')

def test_set_converters():
    if not has_numpy:
        return
    converters = {'zabs1.nh': [asciitable.convert_numpy('int32'),
                               asciitable.convert_numpy('float32')],
                  'p1.gamma': asciitable.convert_numpy('str')
                  }
    data = asciitable.read('t/test4.dat', converters=converters)
    assert_equal(str(data['zabs1.nh'].dtype), 'float32')
    assert_equal(str(data['p1.gamma'].dtype), '|S13')
    assert_equal(data['p1.gamma'][0], '1.26764544642')
    
def test_from_string():
    f = 't/simple.txt'
    table = open(f).read()
    data = asciitable.read(table, **opt[f])
    assert_equal(data.dtype.names, cols[f])
    assert_equal(len(data), nrows[f])
    
def test_from_lines():
    f = 't/simple.txt'
    table = open(f).readlines()
    data = asciitable.read(table, **opt[f])
    assert_equal(data.dtype.names, cols[f])
    assert_equal(len(data), nrows[f])
    

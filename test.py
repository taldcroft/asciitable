from nose.tools import *

import asciitable
try:
    import numpy
except ImportError:
    pass

class TableNumpy(asciitable.Table):
    outputter_class = asciitable.NumpyOutputter

class TabTable(TableNumpy):
    def __init__(self):
        super(TabTable, self).__init__()
        self.header.splitter.delimiter = '\t'
        self.data.splitter.delimiter = '\t'

class RdbTable(TabTable):
    def __init__(self):
        super(RdbTable, self).__init__()
        self.data.skip_header = 2

def read_rdb_table(table):
    reader = asciitable.TableNumpy()
    reader.header.splitter.delimiter = '\t'
    reader.data.splitter.delimiter = '\t'
    reader.data.skip_header = 2
    return reader.read(table)

def read_table(table,
               delimiter=None,
               header_start=None,
               data_start=None,
               data_end=None,
               converters=None,
               numpy=True,
               Reader=asciitable.Table):
    reader = Reader()

    if numpy:
        reader.outputter = asciitable.NumpyOutputter()
    if delimiter is not None:
        reader.header.splitter.delimiter = delimiter
        reader.data.splitter.delimiter = delimiter
    if data_start is not None:
        reader.data.start_line = data_start
    if data_end is not None:
        reader.data.end_line = data_end
    if header_start is not None:
        reader.header.start_line = header_start
    if converters is not None:
        reader.outputter.converters = converters

    return reader.read(table)

cols = {}
cols["t/short.tab"]      = ('agasc_id', 'n_noids', 'n_obs')
cols["t/simple5.txt"]    = ('3102  |  0.32     |     4167 |  4085   |  Q1250+568-A  |  9',)
cols["t/short.rdb"]      = ('agasc_id', 'n_noids', 'n_obs')
cols["t/apostrophe.tab"] = ('agasc_id', 'n_noids', 'n_obs')
cols["t/apostrophe.rdb"] = ('agasc_id', 'n_noids', 'n_obs')
cols["t/simple3.txt"]    = ('obsid', 'redshift', 'X', 'Y', 'object', 'rad')
cols["t/simple4.txt"]    = ('col1', 'col2', 'col3', 'col4', 'col5', 'col6')
cols["t/test4.dat"]      = ('zabs1.nh', 'p1.gamma', 'p1.ampl', 'statname', 'statval')
cols["t/simple.txt"]     = ('test 1a', 'test2', 'test3', 'test4')
cols["t/simple2.txt"]    = ('obsid', 'redshift', 'X', 'Y', 'object', 'rad')
cols["t/nls1_stackinfo.dbout"] = ('', 'objID', 'osrcid', 'xsrcid', 'SpecObjID', 'ra', 'dec',
                                  'obsid', 'ccdid', 'z', 'modelMag_i',
                                  'modelMagErr_i', 'modelMag_r', 'modelMagErr_r', 'expo',
                                  'theta', 'rad_ecf_39', 'detlim90', 'fBlim90')

nrows = {}
nrows["t/short.tab"] = 7
nrows["t/simple5.txt"] = 2
nrows["t/short.rdb"] = 7
nrows["t/apostrophe.tab"] = 3
nrows["t/apostrophe.rdb"] = 2
nrows["t/simple3.txt"] = 2
nrows["t/simple4.txt"] = 3
nrows["t/test4.dat"] = 1172
nrows["t/simple.txt"] = 2
nrows["t/simple2.txt"] = 3
nrows["t/nls1_stackinfo.dbout"] = 58

opt = {}
opt['t/short.rdb'] = {'headertype': 'rdb'}
opt['t/apostrophe.rdb'] = {'headertype': 'rdb'}
opt['t/simple4.txt'] = {'headertype': 'none'}
opt["t/nls1_stackinfo.dbout"] = {'headerrow': 1, 'datastart': 3}


## def test10_read_all_files():
##     from glob import glob
##     for f in glob('t/*'):
##         if f in cols:
##             parseopt = (f in opt and opt[f]) or {}
##             data_array = read_table(f, **parseopt)
##             assert_equal(data_array.dtype.names, cols[f])
##             assert_equal(len(data_array), nrows[f])

## def test20_missing_file():
##     assertRaises(IOError,
##                       read_table,
##                       'file_doesnt_exist')

## def test40_ascii_colnames():
##     colnames = ('c1','c2','c3', 'c4', 'c5', 'c6')
##     data = read_ascii_table('t/simple3.txt',
##                              colnames=colnames)
##     assert_equal(data.dtype.names, colnames)


import sys
from nose.tools import *
import asciitable
import StringIO

test_defs = [
    dict(kwargs=dict(),
         out="""\
ID XCENTER YCENTER MAG MERR MSKY NITER SHARPNESS CHI PIER PERROR
14 138.538 256.405 15.461 0.003 34.85955 4 -0.032 0.802 0 No_error
18 18.114 280.17 22.329 0.206 30.12784 4 -2.544 1.104 0 No_error
"""
         ),
    dict(kwargs=dict(formats={'XCENTER': '%12.1f',
                              'YCENTER': lambda x: round(x, 1)},
                     include_names=['XCENTER', 'YCENTER']),
         out="""\
XCENTER YCENTER
"       138.5" 256.4
"        18.1" 280.2
"""
         ),   
    dict(kwargs=dict(Writer=asciitable.Rdb, exclude_names=['CHI']),
         out="""\
ID	XCENTER	YCENTER	MAG	MERR	MSKY	NITER	SHARPNESS	PIER	PERROR
S	S	S	S	S	S	S	S	S	S
14	138.538	256.405	15.461	0.003	34.85955	4	-0.032	0	No_error
18	18.114	280.17	22.329	0.206	30.12784	4	-2.544	0	No_error
"""
         ),   
    dict(kwargs=dict(Writer=asciitable.Tab),
         out="""\
ID	XCENTER	YCENTER	MAG	MERR	MSKY	NITER	SHARPNESS	CHI	PIER	PERROR
14	138.538	256.405	15.461	0.003	34.85955	4	-0.032	0.802	0	No_error
18	18.114	280.17	22.329	0.206	30.12784	4	-2.544	1.104	0	No_error
"""
         ),   
    dict(kwargs=dict(Writer=asciitable.NoHeader),
         out="""\
14 138.538 256.405 15.461 0.003 34.85955 4 -0.032 0.802 0 No_error
18 18.114 280.17 22.329 0.206 30.12784 4 -2.544 1.104 0 No_error
"""
         ),   
    dict(kwargs=dict(Writer=asciitable.CommentedHeader),
         out="""\
# ID XCENTER YCENTER MAG MERR MSKY NITER SHARPNESS CHI PIER PERROR
14 138.538 256.405 15.461 0.003 34.85955 4 -0.032 0.802 0 No_error
18 18.114 280.17 22.329 0.206 30.12784 4 -2.544 1.104 0 No_error
"""
         ),   
    ]

def check_write_table(test_def, table):
    out = StringIO.StringIO()
    asciitable.write(table, out, **test_def['kwargs'])
    print 'Expected:\n', test_def['out']
    print 'Actual:\n', out.getvalue()
    if out.getvalue() != test_def['out']:
        with open('out.dat', 'w') as f:
            f.write(out.getvalue())
    assert(out.getvalue() == test_def['out'])

def test_write_table():
    table = asciitable.get_reader(Reader=asciitable.Daophot)
    data = table.read('t/daophot.dat')

    for test_def in test_defs:
        yield check_write_table, test_def, table
        yield check_write_table, test_def, data

def test_write_table_no_numpy():
    table = asciitable.get_reader(Reader=asciitable.Daophot, numpy=False)
    data = table.read('t/daophot.dat')

    for test_def in test_defs:
        yield check_write_table, test_def, table
        yield check_write_table, test_def, data

##asciitable.write(data, sys.stdout)
##asciitable.write(table, sys.stdout, formats={'XCENTER': '%12.1f',
##                                             'YCENTER': lambda x: round(x, 1)},
##                 include_names=['XCENTER', 'YCENTER'])

##asciitable.write(table, sys.stdout, Writer=asciitable.Rdb, exclude_names=['CHI'] )
##asciitable.write(table, sys.stdout, Writer=asciitable.Tab )
##asciitable.write(table, sys.stdout, Writer=asciitable.NoHeader )
##asciitable.write(table, sys.stdout, Writer=asciitable.CommentedHeader )

##table = asciitable.get_reader(Reader=asciitable.Daophot, numpy=False)
##data = table.read('t/daophot.dat')
##asciitable.write(table, sys.stdout)
##asciitable.write(data, sys.stdout)

##data = [[1, 2, 3], [4, 5.2, 6.1], [8, 9, 'hello']]
##asciitable.write(data, sys.stdout)
##asciitable.write(data, sys.stdout, names=['x', 'y', 'z'], exclude_names=['y'])

##data = {'x': [1,2,3], 'y': [4, 5.2, 6.1], 'z': [8, 9, 'hello world']}
##asciitable.write(data, sys.stdout)

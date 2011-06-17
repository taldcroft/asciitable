import sys
from nose.tools import *
import asciitable

try:
    import StringIO as io
except ImportError:
    import io

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
N	N	N	N	N	N	N	N	N	N
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
    dict(kwargs=dict(Writer=asciitable.Latex),
         out="""\
\\begin{table}
\\begin{tabular}{ccccccccccc}
\\hline
\\hline
ID & XCENTER & YCENTER & MAG & MERR & MSKY & NITER & SHARPNESS & CHI & PIER & PERROR \\\\
\\hline
\\hline
14 & 138.538 & 256.405 & 15.461 & 0.003 & 34.85955 & 4 & -0.032 & 0.802 & 0 & No_error \\\\
18 & 18.114 & 280.17 & 22.329 & 0.206 & 30.12784 & 4 & -2.544 & 1.104 & 0 & No_error \\\\
\\hline
\\end{tabular}
\\end{table}
"""
         ),
    dict(kwargs=dict(Writer=asciitable.Latex, caption = r'\caption{DaoPhot results \label{tab1}}', col_align = 'rlcc|ccccccc'),
         out="""\
\\begin{table}
\\caption{DaoPhot results \\label{tab1}}
\\begin{tabular}{rlcc|ccccccc}
\\hline
\\hline
ID & XCENTER & YCENTER & MAG & MERR & MSKY & NITER & SHARPNESS & CHI & PIER & PERROR \\\\
\\hline
\\hline
14 & 138.538 & 256.405 & 15.461 & 0.003 & 34.85955 & 4 & -0.032 & 0.802 & 0 & No_error \\\\
18 & 18.114 & 280.17 & 22.329 & 0.206 & 30.12784 & 4 & -2.544 & 1.104 & 0 & No_error \\\\
\\hline
\\end{tabular}
\\end{table}
"""
         ),
]

def check_write_table(test_def, table):
    out = io.StringIO()
    asciitable.write(table, out, **test_def['kwargs'])
    print('Expected:\n%s' % test_def['out'])
    print('Actual:\n%s' % out.getvalue())
    assert(out.getvalue().splitlines() == test_def['out'].splitlines())

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


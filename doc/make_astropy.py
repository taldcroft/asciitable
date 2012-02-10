import glob
import re

filenames = glob.glob('*.rst')

re_asciitable = re.compile('asciitable', re.IGNORECASE)
for filename in filenames:
    if filename == 'install.rst':
        continue
    out = open('.astropy/' + filename, 'w')
    for line in open(filename, 'r'):
        line = re_asciitable.sub('astropy.io.ascii', line)
        out.write(line)
    out.close()

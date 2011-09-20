"""
Version numbering for asciitable. The `major`, `minor`, and `bugfix` varaibles hold
the respective parts of the version number (bugfix is '0' if absent). The 
`release` variable is True if this is a release, and False if this is a 
development version. For the actual version string, use::

    from astropy.version import version
    
or::

    from astropy import __version__
    
NOTE: this code copied from astropy.version and modified.  Any license restrictions
therein are applicable.
"""

version = '0.7.1'

_versplit = version.replace('dev', '').split('.')
major = int(_versplit[0])
minor = int(_versplit[1])
if len(_versplit) < 3:
    bugfix = 0
else:
    bugfix = int(_versplit[2])
del _versplit

release = not version.endswith('dev')

def _get_git_devstr(sha=False):
    """Determines the number of revisions in this repository.

    Parameters
    ----------
    sha : bool
        If True, the full SHA1 hash will be at the end of the devstr. Otherwise,
        the total count of commits in the repository will be used as a "revision
        number".

    Returns
    -------
    devstr : str
        A string that begins with 'dev' to be appended to the astropy version
        number string.
        
    """
    from os import path
    from subprocess import Popen, PIPE
    from warnings import warn
    
    if release:
        raise ValueError('revision devstring should not be used in a release version')

    currdir = path.abspath(path.split(__file__)[0])
    
    p = Popen(['git', 'rev-list', 'HEAD'], cwd=currdir,
              stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = p.communicate()
        
    if p.returncode == 128:
        warn('No git repository present! Using default dev version.')
        return ''
    elif p.returncode != 0:
        warn('Git failed while determining revision count: '+stderr)
        return ''
    
    if sha:
        return '-git-'+stdout[:40]
    else:
        nrev = stdout.count('\n')
        return  '-r%i'%nrev
    
if not release:
    version = version + _get_git_devstr(False)

# distutils: language=c
# cython: language_level=3

cimport cython
cimport numpy as np
import numpy as np
from tempfile import NamedTemporaryFile as NTF
from rawdatarinator import read

cdef extern from "twixread.h":
    int main_twixread(int argc, char* argv[])

@cython.boundscheck(False)
@cython.wraparound(False)
def twixread(
        filename=None,
        outname=None,
        unsigned int x=0,
        unsigned int r=0,
        unsigned int y=0,
        unsigned int z=0,
        unsigned int s=0,
        unsigned int v=0,
        unsigned int c=0,
        unsigned int n=0,
        unsigned int a=0,
        int A=False, # bool
        int L=False, # bool
        int P=False, # bool
        int M=False, # bool
        int h=False, # bool
    ):
    '''Read TWIX file.

    Parameters
    ----------
    filename : str
        Path to Siemens raw data file.
    outname : str or None, optional
        Path to output file (without extension).  If outname=None,
        then the data will be returned as a numpy array.
    x : int, optional
        number of samples (read-out)
    r : int, optional
        radial lines
    y : int, optional
        phase encoding steps
    z : int, optional
        partition encoding steps
    s : int, optional
        number of slices
    v : int, optional
        number of averages
    c : int, optional
        number of channels
    n : int, optional
        number of repetitions
    a : int, optional
        total number of ADCs
    A : bool, optional
        automatic [guess dimensions]
    L : bool, optional
        use linectr offset
    P : bool, optional
        use partctr offset
    M : bool, optional
        MPI mode
    h : bool, optional
        help.  Note that Python scipt will stop if this function
        is called with this option, as BART calls exit(0) after
        displaying help info.

    Returns
    -------
    data : array_like, optional
        If outname=None, the data from the raw data file.

    Notes
    -----
    Cython-compiled twixread function from BART [1]_.

    References
    ----------
    .. [1] Uecker, Martin, et al. "Berkeley advanced reconstruction
           toolbox." Proc. Intl. Soc. Mag. Reson. Med. Vol. 23. 2015.
    '''

    # Define all c vars:
    cdef:
        int cargs
        int retVal
        int ii
        char* vargs[16] # 16 possible arguments

    # We need to figure out how many arguments there are.  We know
    # the first one will always be 'twixread' and the last two will
    # always be filenames, so count the rest of them:
    lst = [x, r, y, z, s, v, c, n, a, A, L, P, M, h]
    lbls = [
        '-x%d' % x, '-r%d' % r, '-y%d' % y, '-z%d' % z, '-s%d' % s,
        '-v%d' % v, '-c%d' % c, '-n%d' % n, '-a%d' % a, '-A', '-L',
        '-P', '-M', '-h']
    cargs = sum(el > 0 for el in lst) + 3
    _vargs = [lbl0.encode() for l0, lbl0 in zip(lst, lbls) if bool(l0)]
    _vargs.insert(0, b'twixread')

    # filename can only be None when help is desired
    if filename is None:
        assert h, 'Filename required!'
        filename = ''
        outname = ''
    _vargs.append(filename.encode())

    # do it once if the outfile is not given, and once if it is
    if outname is None:
        with NTF() as f:
            _vargs.append(f.name.encode())

            # Assign all arguments we got to the first cargs slots
            # of vargs
            for ii in range(cargs):
                vargs[ii] = _vargs[ii]
            retVal = main_twixread(cargs, vargs)
            return read.read(f.name)

    # If we have the outfile, we can just put the data there
    _vargs.append(outname.encode())
    for ii in range(cargs):
        vargs[ii] = _vargs[ii]
    retVal = main_twixread(cargs, vargs)
    return retVal

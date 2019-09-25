# distutils: language=c
# cython: language_level=3

cimport numpy as np
import numpy as np
import cython

@cython.boundscheck(False)
@cython.wraparound(False)
def read(filename):
    '''Read BART file.

    Parameters
    ----------
    filename : str
        Path (without extension) of data stored in BART file format.

    Returns
    -------
    data : array_like
        numpy array with data from BART file.
    '''

    # Open files the right way...
    # get dims from .hdr
    with open(filename + '.hdr', 'r') as h:
        h.readline() # skip
        l = h.readline()
    dims = [int(ii) for ii in l.split()]

    # remove singleton dimensions from the end
    n = np.prod(dims)
    dims_prod = np.cumprod(dims)
    dims = dims[:np.searchsorted(dims_prod, n)+1]

    # load data and reshape into dims
    with open(filename + '.cfl', 'r') as d:
        a = np.fromfile(d, dtype=np.complex64, count=n)

    return a.reshape(dims, order='F') # column-major

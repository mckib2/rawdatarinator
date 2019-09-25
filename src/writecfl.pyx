# distutils: language=c
# cython: language_level=3

cimport numpy as np
import numpy as np
import cython

@cython.boundscheck(False)
@cython.wraparound(False)
def write(filename, arr):
    '''Write BART file.

    Parameters
    ----------
    filename : str
        Path (without extension) to write data in BART file format.
    arr : array_like
        numpy array containing data to store at filename.

    Returns
    -------
    None

    Notes
    -----
    Two files will be written: the data ([filename].cfl) and the
    header ([filename].hdr).
    '''

    cdef int ii

    with open(filename + '.hdr', 'w') as h:
        h.write('# Dimensions\n')
        for ii in arr.shape[:]:
                h.write('%d ' % ii)
        h.write('\n')

    with open(filename + '.cfl', 'w') as d:
        # tranpose for column-major order
        arr.T.astype(np.complex64).tofile(d)

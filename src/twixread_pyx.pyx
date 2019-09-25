# distutils: language=c
# cython: language_level=3

cimport cython
from tempfile import NamedTemporaryFile as NTF
from rawdatarinator import read

cdef extern from "twixread.h":
    int main_twixread(int argc, char* argv[])

@cython.boundscheck(False)
@cython.wraparound(False)
def twixread(filename, outname=None):
    '''Read TWIX file.

    Parameters
    ----------
    filename : str
        Path to Siemens raw data file.
    outname : str or None, optional
        Path to output file (without extension).  If outname=None,
        then the data will be returned as a numpy array.

    Returns
    -------
    data : array_like, optional
        If outname=None, the data from the raw data file.

    Notes
    -----
    Cython-compiled twixread function from BART [1]_. Currently only
    supports -A option.

    References
    ----------
    .. [1] Uecker, Martin, et al. "Berkeley advanced reconstruction
           toolbox." Proc. Intl. Soc. Mag. Reson. Med. Vol. 23. 2015.
    '''

    # We only accept -A option, so we will always have 4 args:
    #     [twixread, -A, infile, outfile]
    cdef char* vargs[4]
    cdef int val

    # If outname is None, then we want to return the data, so shove
    # it in a temporary file
    if outname is None:
        with NTF() as f:
            vargs[:] = [
                "twixread", "-A", filename.encode(), f.name.encode()]
            val = main_twixread(4, vargs)
            return read.read(f.name)

    # Otherwise, save the BART files where the user wanted them
    vargs[:] = ["twixread", "-A", filename.encode(), outname.encode()]
    val = main_twixread(4, vargs)
    return val

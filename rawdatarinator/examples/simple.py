'''Simple tests.'''

from tempfile import NamedTemporaryFile as NTF

import numpy as np
from rawdatarinator import twixread, read, write

if __name__ == '__main__':

    # Read a .dat raw data file into memory
    val = twixread(
        'data/meas_MID288_se_tr2000_te10_ti50_FID47023.dat', A=True)
    print(val.shape)

    # Read and write data:
    with NTF() as f:
        data = np.random.random((10, 10))
        write(f.name, data)
        rdata = read(f.name)

        assert np.allclose(data, rdata)
        print('IT WORKED!')

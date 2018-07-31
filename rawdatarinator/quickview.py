import matplotlib.pyplot as plt
import numpy as np
from rawdatarinator.decode_opts import decode_simple_opts
import sys
import h5py

def quickview(filename,
              noIFFT=False):
    '''
    Display processed MRI data from `.hdf5`, `.npz`, or `.dat` files.  No arguments displays the IFFT of the k-space data.  The type of file is guessed by the file extension (i.e., if extension is `.dat` then readMeasData15 will be run to get the data).

    Command-line Options:
    -nifft (no IFFT)
                 Display k-space data, log magnitude and phase plots.

    '''

    if filename.endswith('.npz'):
        data = np.load(filename)
    elif filename.endswith('.dat'):
        from readMeasDataVB15 import readMeasDataVB15 as rmd
        data = rmd(filename)
    else:
        data = h5py.File(filename,'r')

    if 'kSpace' in data:
        key = 'kSpace'
    else:
        key = 'imSpace'
        noIFFT = not noIFFT

    # Average over all the averages, use first coil
    coil = 0
    num_avgs = data[key].shape[2]
    avg = (np.squeeze(np.sum(data[key],axis=2))/num_avgs)[:,:,coil]

    if noIFFT is False:
        imData = np.fft.ifftshift(np.fft.ifft2(avg))
        plt.imshow(np.absolute(imData),cmap='gray')
        plt.title('Image Data')
    else:
        mag = np.log(np.absolute(avg))
        phase = np.angle(avg)
        f,(ax1,ax2) = plt.subplots(1,2,sharey=True)
        ax1.imshow(mag,cmap='gray')
        ax2.imshow(phase,cmap='gray')
        ax1.set_title('log(Magnitude)')
        ax2.set_title('Phase')

    plt.show()

if __name__ == '__main__':
    decode_simple_opts({ '-nifft':['noIFFT',False] },sys.argv[1:],quickview)

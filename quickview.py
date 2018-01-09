import matplotlib.pyplot as plt
import numpy as np
from decode_opts import decode_simple_opts
import sys

def quickview(filename,
              noIFFT=False):
    '''
    Display processed MRI data from .npz file.

    No arguments displays the IFFT of the k-space data.

    Command-line Options:
    -nifft (no IFFT)
                 Display k-space data, log magnitude and phase plots.

    '''      
    data = np.load(filename)
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

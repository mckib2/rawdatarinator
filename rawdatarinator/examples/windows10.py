'''Make sure test data runs.'''

import numpy as np
import matplotlib.pyplot as plt

from rawdatarinator import twixread

if __name__ == '__main__':

    # Read in the test data
    data = twixread('data/meas_MID11_gre_FID42801.dat', A=True)
    data = data.squeeze()
    print(data.shape) # Make sure dimensions make sense

    # Put into image space
    ax = (0, 1)
    im = np.fft.ifftshift(np.fft.ifft2(np.fft.fftshift(
        data, axes=ax), axes=ax), axes=ax)

    # SOS along coil dimension, remove 2x oversampling
    sy4 = int(im.shape[0]/4)
    sos = np.sqrt(np.sum(np.abs(im[sy4:-sy4, ...])**2, axis=-1))

    # Take a gander at the images
    plt_opts = {'cmap':'gray'}
    plt.subplot(1, 2, 1)
    plt.imshow(sos[..., 0], **plt_opts)
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.imshow(sos[..., 1], **plt_opts)
    plt.axis('off')
    plt.show()

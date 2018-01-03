import matplotlib.pyplot as plt
import numpy as np

def quickview(filename):
    data = np.load(filename)
    print(data.keys())
    print(data['kSpace'].shape)
    
    #plt.plot()
    #plt.title('test')
    #plt.show()

if __name__ == '__main__':
    quickview('test-data/test_Kspace.npz')

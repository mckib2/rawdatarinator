### Load in MATLAB workspace and check to make sure we're getting the right values

import numpy as np
import scipy.io as spio
from readMeasDataVB15 import readMeasDataVB15

wkspace = spio.loadmat('test-data/test.mat')
pydata = readMeasDataVB15('test-data/test.dat')

for key,val in pydata.items():
    matval = wkspace[key][0][0]
    matvalcmp = type(val)(matval)

    # If it's a float, we have some precision issues to deal with
    if type(val) is float:
        test = lambda x,y: not np.isclose(x,y)
    else:
        test = lambda x,y: x is not y

    # Find the values that don't match
    if test(val,matvalcmp):
        print('Error: %s' % key)
        print('\tMATLAB: %s %s\n' % (matval,type(matval)) +
              '\tMATCON: %s %s\n' % (matvalcmp,type(matvalcmp)) +
              '\tPYTHON: %s %s'   % (val,type(val)))

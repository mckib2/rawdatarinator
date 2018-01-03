## Load in MATLAB workspace and check to make sure we're getting the right values

import numpy as np
import scipy.io as spio
from colorama import init, Fore
from readMeasDataVB15 import readMeasDataVB15
from timer import Timer
init()
timer = Timer()

timer.tic('load MATLAB data')
wkspace = spio.loadmat('test-data/test.mat')
timer.toc()

timer.tic('run readMeasVB15')
pydata = readMeasDataVB15('test-data/test.dat')
timer.toc()

passed = 0
failed = 0
warning = 0

# Sort the keys alphabetically so we can make our way around more quickly
keys = sorted(pydata.keys(),key=str.lower)

timer.tic('Compare keys')
for key in keys:
    val = pydata[key]
    if key not in wkspace:
        print(Fore.YELLOW + 'Warning: ' + Fore.RESET + '%s' % key)
        print('\tKey does not exist in MATLAB!')
        warning += 1
        continue

    matval = wkspace[key][0][0]
    if type(val) is not np.ndarray:
        matvalcmp = type(val)(matval)

    # If it's a float, we have some precision issues to deal with
    if type(val) is float:
        test = lambda x,y: not np.isclose(x,y)
    # If they're arrays, then do an array comparison
    elif type(val) is np.ndarray:
        matval = wkspace[key]
        matvalcmp = np.squeeze(matval) # scipy introduces extra singleton dims
        test = lambda x,y: not np.allclose(x,y)
    else:
        test = lambda x,y: x != y

    # Find the values that don't match
    if test(val,matvalcmp):
        failed += 1
        valshow = val.shape if type(val) is np.ndarray else val
        matshow = matvalcmp.shape if type(val) is np.ndarray else matvalcmp

        if key == 'noiseMeas':
            print(matvalcmp)
            print(val)
        
        print(Fore.RED + 'Error: ' + Fore.RESET + '%s' % key)
        print('\tMATLAB: %s %s\n' % (matshow,type(matval)) +
              '\tMATCON: %s %s\n' % (matshow,type(matvalcmp)) +
              '\tPYTHON: %s %s'   % (valshow,type(val)))
    else:
        passed += 1
        valprint = 'array' if type(val) is np.ndarray else val
        print(Fore.GREEN + 'Passed: ' + Fore.RESET + '%s (%s)' % (key,valprint))

timer.toc()
print('----------------------------------------------------------')
print(Fore.GREEN + 'Passed : %s' % passed)
print(Fore.YELLOW + 'Warning: %s' % warning)
print(Fore.RED + 'Failed : %s' % failed)

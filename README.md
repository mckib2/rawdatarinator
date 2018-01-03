# The Raw-Datar-Inator

Python implementation based on MATLAB version written by Eugene G. Kholmovski, PhD (UCAIR, Department of Radiology, University of Utah).

The name of the project pays homage to the naming convention of the main antagonist in Disney's hit cartoon "Phineas and Ferb" (see <a href="http://phineasandferb.wikia.com/wiki/List_of_Doofenshmirtz%27s_schemes_and_inventions">List of Doofenshmirtz's schemes and inventions</a>).

## Installation

`requirements.txt` contains package dependencies.  You can install it using pip like this:

```
git clone https://github.com/mckib2/raw-datar-inator.git
cd raw-datar-inator
pip install -r requirements.txt
```

## readMeasDataVB15

Read raw data from Siemens MRI scanners with IDEA VB15.

 Will return an array of measured k-space data from raw data from
 Siemens MRI scanners using IDEA VB15 (single value). If the option
 `-I` is used, then image space data will be returned instead.

### Usage:
```
readMeasDataVB15 filename [ -t ] [ -rfft ] [ -r1 ] [ -rp ] [ -rn ]
                          [ -skipts ] [ -nnavek ] [ -ros ]
                          [ -rosa ] [ -I ] [ -w ]
```

### Example:
```./readMeasDataVB15 raw.dat -w```

### Command-line Options:
```
filename
  Filename of file containing raw measurements.
                    
-rfft (resetFFTscale)
  Resets FFTscale and DataCorrection for each coil
  to 1.

-r1 (readOneCoil)
  Read measurement data from from individual coil.

-rp (readPhaseCorInfo)
  _

-rn (readNavigator)
  _

-skipts (skip readTimeStamp)
  _

-nnavek (nNavEK)
  _

-ros (removeOS)
  Flag to remove oversampling (OS) in the x
  direction. removeOS=True is more efficient as it
  processes each readout line independently,
  reducing the required memory space to keep all
  measured data.

-rosa (removeOSafter)
  Flag to remove oversampling (OS) in the x
  direction. This works in image space, cutting FOV.
  Not likely a good idea for radial.

-I (transformToImageSpace)
  Produce image space representation. Note that
  there is no correction for partial Fourier or
  parallel imaging k-space undersampling.  The given
  version of code only uses numpy's FFT operation.

-w (writeToFile)
  Save k-space or image space volume. Currently the
  output filename is auto generated.
    
-h (help)
  Displays this documentation.
```

## Testing

`testsuite.py` compares the values generated in the Python implementation to the workspace variables of the MATLAB implementation to ensure correct output.

## Quick View

`quickview.py` gives a quick way to visualize simple datasets.

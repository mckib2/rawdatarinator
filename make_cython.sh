#!/usr/bin/env bash

# Make sure all Cython business is current
pip install --upgrade Cython

# Make sure .pyx files have been processed
python setup.py build_ext --inplace -f

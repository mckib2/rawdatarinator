#!/bin/bash

# Remove any existing distribution archives
rm -rf dist
mkdir dist

# Get BART updates
source update_bart.sh

# Update BART version references
echo 'VERSION('`bart/git-version.sh`')' > src/version.inc

# Update Cython, get dependencies, and make C files
export __DO_CYTHON_BUILD=1
source make_cython.sh
export __DO_CYTHON_BUILD=0

# Generate distribution archives
pip install --upgrade setuptools wheel
python setup.py sdist # bdist_wheel

# Upload
pip install --upgrade twine
python -m twine upload dist/*

#!/bin/bash

# Remove any existing distribution archives
rm -rf dist
mkdir dist

# Get BART updates
source update_bart.sh

# Update BART version references
(cd bart && echo 'VERSION('`./git-version.sh`')' > ../src/version.inc)

# Update Cython, get dependencies, and make C files
source make_cython.sh

# Generate distribution archives
pip install --upgrade setuptools wheel
python setup.py sdist # bdist_wheel

# Upload
pip install --upgrade twine
python -m twine upload dist/*

from distutils.core import setup
from setuptools import find_packages

setup(
    name='rawdatarinator',
    version='0.1.8',
    author='Nicholas McKibben',
    author_email='mri@byu.edu',
    packages=find_packages(exclude=['test-data']),
    scripts=[],
    url='https://github.com/mckib2/rawdatarinator',
    license='GPL',
    description='Read raw data from Siemens MRI scanners with IDEA VB15.',
    long_description=open('README.rst').read(),
    install_requires=[
        "numpy==1.14.1",
        "scipy==1.0.0",
        "regex==2017.12.12",
        "h5py==2.7.1",
        "matplotlib==2.1.1",
        "ply==3.10"
    ],
    python_requires='>=2.7',
)

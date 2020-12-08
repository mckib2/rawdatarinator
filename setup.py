'''Setup.py'''

from distutils.spawn import find_executable
import subprocess
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    '''Subclass build_ext to bootstrap numpy and deal with compile.'''

    def finalize_options(self):
        _build_ext.finalize_options(self)

        # Prevent numpy from thinking it's still in its setup process
        import numpy as np
        self.include_dirs.append(np.get_include())

    def build_extensions(self):
        '''We want different opts and potentially preprocess.'''
        _build_ext.build_extensions(self)


# If we have Cython, go ahead and regenerate the sources
if find_executable('cython') is not None:
    print('Running cython...')
    try:
        subprocess.call(['cython -3 src/*.pyx'], shell=True)
    except subprocess.CalledProcessError:
        print('Cython failed! Going to try to keep going...')

MACROS = [
    ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
]
extensions = [
    Extension(
        'rawdatarinator.twixread_pyx',
        sources=[
            "bart/src/misc/version.c",
            "bart/src/num/vecops.c",
            "bart/src/num/simplex.c",
            "bart/src/num/optimize.c",
            "bart/src/num/multind.c",
            "bart/src/misc/ya_getopt.c",
            "bart/src/misc/opts.c",
            "bart/src/misc/misc.c",
            "bart/src/misc/io.c",
            "bart/src/misc/mmio.c",
            "bart/src/misc/debug.c",
            "bart/src/twixread.c",
            "src/twixread_pyx.c",
        ],
        include_dirs=['src/', 'bart/src/'],
        define_macros=MACROS,
    ),
    Extension(
        'rawdatarinator.readcfl',
        sources=['src/readcfl.c'],
        include_dirs=[],
        define_macros=MACROS,
    ),
    Extension(
        'rawdatarinator.writecfl',
        sources=['src/writecfl.c'],
        include_dirs=[],
        define_macros=MACROS,
    ),
]

setup(
    name='rawdatarinator',
    version='1.3.2',
    author='Nicholas McKibben',
    author_email='nicholas.bgp@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/mckib2/rawdatarinator',
    license='GPL',
    description='Read Siemens raw data.',
    long_description=open('README.rst').read(),
    install_requires=[
        "numpy>=1.17.2",
    ],
    cmdclass={'build_ext': build_ext},
    setup_requires=['numpy'],
    python_requires='>=3.5',

    # And now for Cython generated files...
    ext_modules=extensions
)

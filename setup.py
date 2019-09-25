'''Setup.py
'''

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as _build_ext

class build_ext(_build_ext):
    '''Subclass build_ext to bootstrap numpy.'''
    def finalize_options(self):
        _build_ext.finalize_options(self)

        # Prevent numpy from thinking it's still in its setup process
        import numpy as np
        self.include_dirs.append(np.get_include())

extensions = [
    Extension(
        'rawdatarinator.twixread',
        [
            "src/num/vecops.c",
            "src/num/simplex.c",
            "src/num/optimize.c",
            "src/num/multind.c",
            "src/misc/ya_getopt.c",
            "src/misc/opts.c",
            "src/misc/misc.c",
            "src/misc/io.c",
            "src/misc/mmio.c",
            "src/misc/debug.c",
            "src/twixread.c",
            "src/twixread_pyx.pyx"
        ],
        include_dirs=['src/'],
        extra_compile_args=['-O3']#, '-ffast-math']
    ),
    Extension(
        'rawdatarinator.read',
        ['src/readcfl.pyx'],
        include_dirs=[]),
    Extension(
        'rawdatarinator.write',
        ['src/writecfl.pyx'],
        include_dirs=[]),
]

setup(
    name='rawdatarinator',
    version='1.0.0',
    author='Nicholas McKibben',
    author_email='nicholas.bgp@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/mckib2/rawdatarinator',
    license='GPL',
    description='Read Siemens raw data.',
    long_description=open('README.rst').read(),
    install_requires=[
        "numpy>=1.14.1",
    ],
    cmdclass={'build_ext': build_ext},
    setup_requires=['numpy'],
    python_requires='>=3.5',

    # And now for Cython generated files...
    ext_modules=extensions
)

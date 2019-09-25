from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

import numpy as np

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
        include_dirs=['src/', np.get_include()],
        extra_compile_args=['-O3']#, '-ffast-math'],
    ),
    Extension(
        'rawdatarinator.read',
        ['src/readcfl.pyx'],
        include_dirs=[np.get_include()]),
    Extension(
        'rawdatarinator.write',
        ['src/writecfl.pyx'],
        include_dirs=[np.get_include()]),
]

setup(
    ext_modules=cythonize(extensions),
)

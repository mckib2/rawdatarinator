RawDatarInator
==============

Python bindings for BART's `twixread` function ([1]_).  This new
version of rawdatarinator replaces the old Python port of a MATLAB
script.  Consequently, this one runs much faster and breaks less
often.  A cleaner interface is provided which will break all old
code.  See usage for examples.  In general, this new release has
fewer features that work better.

The name of the project pays homage to the naming convention of the
main antagonist in Disney's hit cartoon "Phineas and Ferb" ([2]_).

Installation
============

This package is known to work with Python 3.6.8 using Ubuntu 18.04.
If it doesn't work on your system, please submit an issue and we can
try to figure something out.  The goal is to provide a simple
pip-installable Python interface for BART's twixread function.  The
Cythonized BART code is compiled during the installation, so you will
need a C compiler installed.

Use pip to install:

.. code-block:: bash

    pip install rawdatarinator

Usage
=====
You get a few functions:

.. code-block:: python

    # BART's twixread function can be invoked right from a Python
    # script:
    from rawdatarinator import twixread
    twixread('path/to/input/data.dat', 'path/to/output')

    # A pair of .cfl, .hdr will be created: path/to/output.[cfl/hdr]
    # as BART normally does.  However, if you're using these Python
    # bindings, you might want to just grab the data straight away.
    # You can do this by not providing any output file:
    data = twixread('path/to/data.dat', A=True)

    # You can read existing BART files like this:
    from rawdatarinator import read
    data = read('path/to/file/without/extentsion')

    # If you've used BART's Python interface, this is a modified
    # verison of readcfl.  It works just like that.  Similarly,
    # BART's writecfl functionality can be found:
    from rawdatarinator import write
    write('path/to/out', data)

References
==========
.. [1] Uecker, Martin, et al. "Berkeley advanced reconstruction
       toolbox." Proc. Intl. Soc. Mag. Reson. Med. Vol. 23. 2015.
.. [2] `List of Doofenshmirtz's schemes and inventions <http://phineasandferb.wikia.com/wiki/List_of_Doofenshmirtz%27s_schemes_and_inventions>`_

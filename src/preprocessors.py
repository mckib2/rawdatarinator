'''Any code changes for compatibility.'''

import re
import pathlib

def mingw_preprocessor(filename):
    '''MinGW fixes.'''

    # We need to try both .c and .h files
    path0 = pathlib.Path(filename)
    for ext in ['.c', '.h']:
        filename0 = path0.with_suffix(ext)
        if not filename0.exists():
            continue

        # Read all the source into memory
        with open(filename0, 'r') as f:
            code = f.read()

        ## Let's put the modified files in a new home
        #newfilename = pathlib.Path(*filename0.parts[1:])
        #newfilename.parent.mkdir(parents=True, exist_ok=True)

        # Windows doesn't have <alloca.h>, use <malloc.h> instead
        code = re.sub(r'<alloca.h>', r'<malloc.h>', code)

        # MinGW does not provide execinfo.h, remove it and code it
        # calls in debug.c
        #if str(filename0) == 'bart/src/misc/debug.c':
        if filename0.name == 'debug.c':
            code = re.sub(r'#include <execinfo.h>', r'', code)
            code = re.sub(r'#ifndef __CYGWIN__\s+(^[\s\S]*?)#else\s(^[\s\S]*?)\s#endif', r'', code, flags=re.MULTILINE)
            #print(code)

        # Is it this easy?
        #code = re.sub(r'vdprintf', r'printf', code)

        # Add required headers
        if 'va_start' in code and '<stdarg.h>' not in code:
            code = '#include <stdarg.h>\n' + code
        
        # rewrite the modified source file
        with open(filename0, 'w') as f:
            f.write(code)
    #assert False

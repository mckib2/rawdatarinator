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

        # Windows doesn't have <alloca.h>, use <malloc.h> instead
        code = re.sub(r'<alloca.h>', r'<malloc.h>', code)

        # MinGW does not provide execinfo.h, remove it and code it
        # calls in debug.c
        if filename0.name == 'debug.c':
            code = re.sub(r'#ifndef __CYGWIN__\s#include <execinfo.h>\s#endif', r'', code, flags=re.MULTILINE)
            code = re.sub(r'#ifndef __CYGWIN__\s+(^[\s\S]*?)#else\s(^[\s\S]*?)\s#endif', r'', code, flags=re.MULTILINE)

        # Is it this easy?
        if 'vdprintf' in code:
            #code = re.sub('int ret = vdprintf(fd, fmt, ap);', 'int ret = 0;', code)
            code = re.sub(r'vdprintf\(fd, fmt, ap\)', '0', code)
            #print(code)
            #assert False

        # Name ffs to something that MinGW recognizes
        code = re.sub(r'ffs', r'__builtin_ffs', code)

        # Add required headers
        if 'va_start' in code and '<stdarg.h>' not in code:
            code = '#include <stdarg.h>\n' + code
        
        # rewrite the modified source file
        newfilename = re.sub('bart', 'mingw32', str(filename0))
        pathlib.Path(newfilename).parents[0].mkdir(parents=True, exist_ok=True)
        with open(newfilename, 'w') as f:
            f.write(code)
    #assert False

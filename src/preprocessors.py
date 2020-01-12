'''Any code changes for compatibility.'''

import re

def mingw_preprocessor(filename):
    '''MinGW fixes.'''

    # Read all the source into memory
    with open(filename, 'r') as f:
        code = f.read()

    # Windows doesn't have <alloca.h>, use <malloc.h> instead
    code = re.sub(r'<alloca.h>', r'<malloc.h>', code)

    # rewrite the source file
    with open(filename, 'w') as f:
        f.write(code)

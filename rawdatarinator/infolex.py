import ply.lex as lex
from cleanraw import cleanraw
import sys

class InfoLex(object):
    # List of token names
    tokens = (
        'RANGLE',
        'LANGLE',
        'PERIOD',
        'RBRACE',
        'LBRACE',
        'STRING',
        'INTEGER',
        'FLOAT',
        'HEX',
        'SCINOT',

        'XPROT',
        'PMAP',
        'PSTR',
        'PLNG',
        'PDBL',
        'PBOOL',
        'PARRAY',
        'PFUNCT',
        'PCHOICE',
        'PCARDLAYOUT',
        'PIPE',
        'PIPESERVICE',
        'EVENT',
        'CONN',
        'METHOD',
        'DEPEND',
        'PROTCOMP',
        'NAME',
        'EVASTRTAB',
        'COMMENT',

        # modifiers
        'DEFAULT',
        'CLASS',
        'PRECISION',
        'MINSIZE',
        'MAXSIZE',
        'LABEL',
        'TOOLTIP',
        'LIMRANGE',
        'LIMIT',
        'REPR',
        'POS',
        'PARAM',
        'CONTROL',
        'LINE',
        'DLL',
        'CONTEXT',
        'ID',
        'USERVERSION',
        'INFILE',
        'VISIBLE',
        'COM',
        'UNIT',

        # There are major divisions, we achieve this with modifiers
        'DICOM',
        'MEAS',
        'MEASYAPS',
        'PHOENIX',
        'SPICE',

        # one liners
        'LEFTHAND'
    )


    # Regular expression rules for simple tokens
    t_LANGLE = r'<'
    t_RANGLE = r'>'
    t_PERIOD = r'\.'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_XPROT = r'XProtocol'
    t_PMAP = r'ParamMap'
    t_PSTR = r'ParamString'
    t_PLNG = r'ParamLong'
    t_PDBL = r'ParamDouble'
    t_PBOOL = r'ParamBool'
    t_PARRAY = r'ParamArray'
    t_PFUNCT = r'ParamFunctor'
    t_PCHOICE = r'ParamChoice'
    t_PCARDLAYOUT = r'ParamCardLayout'
    t_PIPE = r'Pipe'
    t_PIPESERVICE = r'PipeService'
    t_EVENT = r'Event'
    t_CONN = r'Connection'
    t_METHOD = r'Method'
    t_DEPEND = r'Dependency'
    t_PROTCOMP = r'ProtocolComposer'
    t_NAME = r'Name'
    t_EVASTRTAB = r'EVAStringTable'
    t_STRING = r'\"(.|\n)*?\"'
    t_INTEGER = r'-?\d+'
    t_FLOAT = r'((\d*\.\d+)(E[\+-]?\d+)?|([1-9]\d*E[\+-]?\d+))'
    t_HEX = r'0x[\dabcdef]+'
    t_SCINOT = r'([+-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+))'
    t_DEFAULT = r'Default'
    t_CLASS = r'Class'
    t_PRECISION = r'Precision'
    t_MINSIZE = r'MinSize'
    t_MAXSIZE = r'MaxSize'
    t_LABEL = r'Label'
    t_TOOLTIP = r'Tooltip'
    t_LIMRANGE = r'LimitRange'
    t_LIMIT = r'Limit'
    t_POS = r'Pos'
    t_PARAM = r'Param'
    t_REPR = r'Repr'
    t_CONTROL = r'Control'
    t_LINE = r'Line'
    t_DLL = r'Dll'
    t_CONTEXT = r'Context'
    t_ID = r'ID'
    t_USERVERSION = r'Userversion'
    t_INFILE = r'InFile'
    t_VISIBLE = r'Visible'
    t_COM = r'Comment'
    t_UNIT = r'Unit'

    t_DICOM = r'Dicom'
    t_MEAS = r'Meas'
    t_MEASYAPS = r'MeasYaps'
    t_PHOENIX = r'Phoenix'
    t_SPICE = r'Spice'

    def t_LEFTHAND(t):
         r'[a-zA-Z\[\]0-9\. _]+='
         # remove the equal sign at the end
         t.value = t.value[:-1].rstrip()
         return(t)

    # Comments are ignored
    def t_COMMENT(t):
        r'\#.*'
        pass

    # Define a rule so we can track line numbers
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters
    t_ignore = ' \t'

    # Error handling rule
    def t_error(t):
        print('Illegal character %s on line %s' % (t.value[0],t.lexer.lineno))
        t.lexer.skip(1)

    # Build the lexer
    lexer = lex.lex()

    # # Give the lexer some input
    # info = cleanraw(sys.argv[1])
    # lexer.input(info)

    # # Tokenize
    # while True:
    #     tok = lexer.token()
    #     if not tok:
    #         break
    #     #print(tok)

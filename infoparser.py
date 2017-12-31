import ply.yacc as yacc
from cleanraw import cleanraw
import xml.etree.ElementTree as ET

# Get the token map from the lexer
from infolex import tokens

# make a stack of the brace state
brace_state = []

# Global variables - not elegant, but a relic of previous versions of the code
xml = ''
node_label = ''
name = ''
mod = ''

def raw2xml(filename):
    global xml,name,mod,node_label
    
    class Node:
        def __init__(self):
            self.tag = ''
            self.attr = dict()
            
        def makeAttrs(self):
            innards = ''
            for key,val in self.attr.items():
                innards += ' ' + key + '=' + val
            return(innards)
            
        def openString(self):
            return('<' + self.tag + self.makeAttrs() + '>')
        
        def closeString(self):
            return('</' + self.tag + '>')
                
    # escape invalid xml entities
    def xml_clean(string):
        return(string.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'))
            
            
    def p_document(p):
        '''document : document line
                            | line'''
                
    def p_modifier(p):
        '''modifier : DEFAULT
                    | CLASS
                    | PRECISION
                    | MINSIZE
                    | MAXSIZE
                    | LABEL
                    | TOOLTIP
                    | LIMRANGE
                    | LIMIT
                    | REPR
                    | POS
                    | PARAM
                    | CONTROL
                    | LINE
                    | DLL
                    | CONTEXT
                    | NAME
                    | ID
                    | USERVERSION
                    | INFILE
                    | VISIBLE
                    | COM
                    | UNIT

                    | DICOM
                    | MEAS
                    | MEASYAPS
                    | PHOENIX
                    | SPICE'''

        global mod
        mod = '"' + p[1] + '"'
    
    def p_line(p):
        '''line : tag LBRACE
                | LANGLE modifier RANGLE tag LBRACE
                | LANGLE modifier RANGLE LBRACE
                | LBRACE
                | RBRACE
                
                | STRING
                | INTEGER
                | FLOAT
                
                | LANGLE modifier RANGLE STRING
                | LANGLE modifier RANGLE INTEGER
                | LANGLE modifier RANGLE FLOAT
                
                | LEFTHAND
                | LANGLE modifier RANGLE LEFTHAND
                | HEX
                | SCINOT'''

        global xml,name,mod
        if len(p) is 3:
            # This means we have an open brace
            brace_state.append((p[2],node_label))
            
            n = Node()
            n.tag = node_label
            
            if name != '':
                n.attr['name'] = name
                name = ''
            if mod != '':
                n.attr['mod'] = mod
                mod = ''
            xml += n.openString()
        
        else:
            # This means we might have close brace
            if p[1] == '}':
                try:
                    tag_name = brace_state.pop()
                    n = Node()
                    n.tag = tag_name[1]
                    xml += n.closeString()
                except:
                    pass
                
            elif p[1] == '{':
                # we got another open brace
                brace_state.append((p[1],'InducedBrace'))
                
                n = Node()
                n.tag = 'InducedBrace'
                xml += n.openString()
            else:
                # This is the value of the tag
                n = Node()
                n.tag = 'value'
                
                if p[1] == '<':
                    n.attr['mod'] = mod
                    mod = ''
                    
                    if p[4] is None:
                        n.tag = node_label
                        brace_state.append((p[5],node_label))
                        xml += n.openString()
                    else:
                        xml += n.openString() + xml_clean(p[4]) + n.closeString()
                else:
                    xml += n.openString() + xml_clean(p[1]) + n.closeString()


    def p_tag(p):
        '''tag : LANGLE tagtype PERIOD STRING RANGLE
                | LANGLE tagtype RANGLE'''
        
        global name
        if len(p) > 4:
            if node_label != '':
                name = p[4]


    def p_tagtype(p):
        '''tagtype : PMAP
                | PSTR
                | PLNG
                | PDBL
                | PBOOL
                | PARRAY
                | PFUNCT
                | PCHOICE
                | PCARDLAYOUT
                | PIPE
                | PIPESERVICE
                | EVENT
                | CONN
                | METHOD
                | DEPEND
                | PROTCOMP
                | EVASTRTAB
                | XPROT'''
    
        global node_label
        node_label = p[1]

    # Error rule for syntax errors
    def p_error(p):
        print('Syntax error in input!')
        print(p)
    
    # Build the parser
    parser = yacc.yacc()
    
    # load in the real data
    info = cleanraw(filename)

    result = parser.parse(info)

    # We have multiple roots, so we need to provide a parent
    xml = '<doc_root>' + xml + '</doc_root>'
    #print(xml)

    # Check to make sure all our braces matched up
    if len(brace_state) > 0:
        print('Mismatched Braces!')

    # Parse the string to make sure XML is well formed
    root = ET.fromstring(xml)

    # Return the xml string
    return(xml)

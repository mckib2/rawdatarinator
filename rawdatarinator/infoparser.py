import ply.yacc as yacc
from rawdatarinator.cleanraw import cleanraw
import xml.etree.ElementTree as ET
from rawdatarinator.infolex import InfoLex

class InfoParser(object):

    # make a stack of the brace state
    brace_state = []

    xml = ''
    node_label = ''
    name = ''
    mod = ''

    def raw2xml(self,filename):
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

            self.mod = '"' + p[1] + '"'
        
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

            if len(p) is 3:
                # This means we have an open brace
                self.brace_state.append((p[2],self.node_label))
                
                n = Node()
                n.tag = self.node_label
                
                if self.name != '':
                    n.attr['name'] = self.name
                    self.name = ''
                if self.mod != '':
                    n.attr['mod'] = self.mod
                    self.mod = ''
                self.xml += n.openString()
            
            else:
                # This means we might have close brace
                if p[1] == '}':
                    try:
                        tag_name = self.brace_state.pop()
                        n = Node()
                        n.tag = tag_name[1]
                        self.xml += n.closeString()
                    except:
                        pass
                    
                elif p[1] == '{':
                    # we got another open brace
                    self.brace_state.append((p[1],'InducedBrace'))
                    
                    n = Node()
                    n.tag = 'InducedBrace'
                    self.xml += n.openString()
                else:
                    # This is the value of the tag
                    n = Node()
                    n.tag = 'value'
                    
                    if p[1] == '<':
                        n.attr['mod'] = self.mod
                        self.mod = ''
                        
                        if p[4] is None:
                            n.tag = self.node_label
                            self.brace_state.append((p[5],self.node_label))
                            self.xml += n.openString()
                        else:
                            self.xml += n.openString() + xml_clean(p[4]) + n.closeString()
                    else:
                        self.xml += n.openString() + xml_clean(p[1]) + n.closeString()


        def p_tag(p):
            '''tag : LANGLE tagtype PERIOD STRING RANGLE
                    | LANGLE tagtype RANGLE'''
            
            if len(p) > 4:
                if self.node_label != '':
                    self.name = p[4]


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
        
            self.node_label = p[1]

        # Error rule for syntax errors
        def p_error(p):
            print('Syntax error in input!')
            print(p)

        # get the lexer and token mappings to pass to yacc
        infoLex = InfoLex()
        lexer = infoLex.lexer
        tokens = infoLex.tokens

        # Build the parser
        parser = yacc.yacc()
        
        # load in the real data
        info = cleanraw(filename)
        result = parser.parse(info)

        # We have multiple roots, so we need to provide a parent
        self.xml = '<doc_root>' + self.xml + '</doc_root>'
        #print(xml)

        # Check to make sure all our braces matched up
        if len(self.brace_state) > 0:
            print('Mismatched Braces!')

        # Parse the string to make sure XML is well formed
        root = ET.fromstring(self.xml)

        # Return the xml string
        return(self.xml)

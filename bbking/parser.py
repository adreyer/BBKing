
import StringIO

import ply.yacc as yacc

from bbking.lexer import tokens

def compress(contents):
    compressed = []
    sio = None
    for item in contents:
        if isinstance(item, Tagged):
            if sio:
                compressed.append(sio.getvalue())
                sio = None
            compressed.append(item)
        else:
            if not sio:
                sio = StringIO.StringIO()
            sio.write(item)

    if sio:
        compressed.append(sio.getvalue())
        
    return compressed

class Tagged(object):
    def __init__(self, name, contents, arg=None, **kwargs): 
        self.name = name
        self.contents = contents
        self.arg = arg
        self.kwargs = kwargs

def p_main(p):
    '''main : content'''
    p[0] = compress(p[1])

def p_content(p):
    '''content : content tagged
               | content untagged
               | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = []

def p_tagged(p):
    '''tagged : opentag content closetag'''
    name, arg, kwargs, raw = p[1]
    close_name, close_raw = p[3]
    if name != close_name:
        p[0] = [raw] + p[2] + [close_raw]
        return
    p[0] = [Tagged(name, compress(p[2]), arg, **kwargs)]

def p_tagged_error(p):
    '''tagged : opentag content error'''

    print "p_tagged_error", list(p)

def p_untagged(p):
    '''untagged : SYMBOL
                | WHITESPACE
                | MISC
                | RBRACKET
                | EQ
                | SLASH
                | errors
    '''
    p[0] = [p[1]]

def p_errors(p):
    '''errors : LBRACKET error
              | LBRACKET SYMBOL error
              | LBRACKET SLASH error
              | LBRACKET SYMBOL WHITESPACE error
    '''
    if len(p) == 3:
        p[0] = p[1]
    if len(p) == 4:
        p[0] = p[1] + p[2]
    if len(p) == 5:
        p[0] = p[1] + p[2] + p[3]

def p_errors_with_args(p):
    '''errors : LBRACKET SYMBOL WHITESPACE arg_errors'''
    p[0] = p[1] + p[2] + p[3] + p[4]

def p_args_errors(p):
    '''arg_errors : SYMBOL error
                  | SYMBOL EQ error
                  | args arg_errors
    '''

    if len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = [p[1],p[2]]

def p_empty(p):
    'empty :'
    pass

def p_text(p):
    '''text : text term 
            | term
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_term(p):
    '''
       term : WHITESPACE 
            | SYMBOL
            | MISC
            | SLASH
            | LBRACKET
    '''
    p[0] = p[1]

def p_text_no_ws(p):
    '''text_no_ws : text_no_ws term_no_ws
            | term_no_ws
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_term_no_ws(p):
    ''' term_no_ws : SYMBOL
                   | MISC
                   | SLASH
    '''
    p[0] = p[1]

def p_close_tag(p):
    'closetag : LBRACKET SLASH SYMBOL RBRACKET'
    raw = "".join(p[1:])
    p[0] = (p[3], raw)

def p_simple_tag(p):
    'opentag : LBRACKET SYMBOL RBRACKET'
    raw = "".join(p[1:])
    p[0] = (p[2], None, {}, raw)

def p_single_arg_tag(p):
    'opentag : LBRACKET SYMBOL EQ text RBRACKET'
    raw = p[1] + p[2] + p[3] + p[4][0] + p[5]
    p[0] = (p[2], compress(p[4])[0], {}, raw)

def p_multi_arg_tag(p):
    'opentag : LBRACKET SYMBOL WHITESPACE args RBRACKET'
    args, raw_args = p[4]
    raw = p[1] + p[2] + p[3] + p[4][1] + p[5]
    p[0] = (p[2], None, args, raw)

def p_tag_args(p):
    '''args : args WHITESPACE arg
            | arg
    '''
    if len(p) == 4:
        key,value,raw_arg = p[3]
        d, raw_args = p[1]
        raw = raw_args + p[2] + raw_arg
        p[0] = (dict(d,**{ key : value}), raw)
    else:
        key,value,raw = p[1]
        p[0] = ({ key : value }, raw)

def p_tag_arg(p):
    'arg  : SYMBOL EQ text_no_ws'
    p[3] = compress(p[3])[0]
    raw = "".join(p[1:])
    p[0] = (p[1], p[3], raw)

def p_error(p):
    # ignore errors for now simply don't run bbcode if it does not parse
    return p

parser = yacc.yacc()

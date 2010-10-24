
import StringIO

import ply.yacc as yacc

from bbking.lexer import tokens

def flatten(items):
    if not isinstance(items, list):
        return items
    flattened = []
    for item in items:
        if isinstance(item, list):
            flattened += flatten(item)
        else:
            flattened.append(item)
    return flattened

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
    '''tagged : opentag content closetag
    '''
    name, arg, kwargs, raw = p[1]
    close_name, close_raw = p[3]
    if name != close_name:
        p[0] = [raw] + p[2] + [close_raw]
        return
    p[0] = [Tagged(name, compress(p[2]), arg, **kwargs)]

def p_untagged(p):
    '''untagged : SYMBOL
                | WHITESPACE
                | MISC
                | RBRACKET
                | EQ
                | SLASH
    '''
    p[0] = [p[1]]

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
    raw = "".join(p[1:4] + p[4] + [p[5]])
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


#Error Handling

def p_malformed_open_tag(p):
    '''malformed_opentag : LBRACKET SYMBOL WHITESPACE RBRACKET
               | LBRACKET SYMBOL WHITESPACE malformed_args RBRACKET
               | LBRACKET RBRACKET
    '''
    raw = "".join(flatten(p[1:]))
    p[0] = [raw]

def p_malformed_args(p):
    '''malformed_args : EQ errors
                      | MISC errors
                      | LBRACKET errors
                      | SLASH errors
    '''
    p[0] = flatten([p[1], p[2]])

def p_malformed_args_symbol(p):
    '''malformed_args : SYMBOL SYMBOL errors
                      | SYMBOL SLASH errors
                      | SYMBOL WHITESPACE errors
                      | SYMBOL MISC errors
                      | SYMBOL LBRACKET errors
    '''
    p[0] = flatten([p[1],p[2],p[3]])

def p_malformed_args_symbol_only(p):
    '''malformed_args : SYMBOL'''
    p[0] = [p[1]]

def p_malformed_close_tag(p):
    '''closetag : LBRACKET SLASH errors RBRACKET
    '''
    raw = "".join(p[1:3] + p[3] + [p[4]])
    p[0] = ('!malformed-close', raw)

def p_errors(p):
    '''errors : SYMBOL errors error
              | SLASH errors error
              | WHITESPACE errors error
              | EQ errors error
              | MISC errors error
              | LBRACKET errors error
              | error
    '''
    if len(p) == 4:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_malformed_tags(p):
    '''untagged : malformed_opentag
    '''
    p[0] = p[1]

def p_error(p):
    # ignore errors for now simply don't run bbcode if it does not parse
    return p

parser = yacc.yacc(debug=True)

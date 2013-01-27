import ply.lex as lex

reserved = {"print" : "PRINT",
            "if": "IF",
            "else": "ELSE",
            "endif": "ENDIF"}

tokens = [
   "NUMBER",
   "STRING",
   "PLUS",
   "MINUS",
   "TIMES",
   "DIVIDE",
   "EQUALS",
   "GT",
   "LT",
   "GE",
   "LE",
   "LPAREN",
   "RPAREN",
   "LBRACE",
   "RBRACE",
   "IDENTIFIER",
   "ASSIGN",
   "SEMI",
   "DOT",
   "COMMA"
   ] + list(reserved.values())

t_PLUS = r"\+"
t_MINUS = r"-"
t_DIVIDE = r"/"
t_EQUALS = r"=="
t_GT = r">"
t_LT = r"<"
t_GE = r">="
t_LE = r"<="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"{"
t_RBRACE = r"}"
t_ASSIGN = r"="
t_SEMI = r";"
t_DOT = r"\."
t_COMMA = r","

def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)    
    return t

def t_STRING(t):
    r"\".*\""
    t.value = t.value[1:-1]
    return t

def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFIER")
    return t

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

t_ignore  = " \t"

def t_COMMENT(t):
    r'\#.*'
    pass

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

lexer = lex.lex()

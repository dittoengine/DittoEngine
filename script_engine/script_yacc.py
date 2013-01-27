import ply.yacc as yacc

from script_lex import tokens
import script_error

CURRENTFILE = None
CURRENTSCRIPT = None

precedence = (
   ("left", "PLUS", "MINUS"),
   ("left", "TIMES", "DIVIDE"),
   ("left", "GT", "LT", "GE", "LE")
   )

def p_statementlist(p):
   """
   statementlist : statement
                 | statementlist statement
   """
   if len(p) == 2:
      p[0] = Node("STATEMENTLIST", p.lineno(1), [p[1]])
   else:
      p[1].children.append(p[2])
      p[0] = p[1]

def p_statementblock(p):
   "statementblock : LBRACE statementlist RBRACE"
   p[0] = p[2]

def p_statement_if(p):
   """
   statement : IF expression statementblock ENDIF
             | IF expression statementblock ELSE statementblock ENDIF
   """

   if len(p) == 5:
      p[0] = Node("IF", p.lineno(1), [p[2], p[3]])
   elif len(p) == 7:
      p[0] = Node("IF", p.lineno(1), [p[2], p[3], p[5]])

def p_statement_print(p):
   """
   statement : PRINT expression SEMI
   """
   p[0] = Node("PRINT", p.lineno(1), [p[2]])

def p_statement_assign(p):
   """
   statement : identifierchain ASSIGN expression SEMI
   """
   p[0] = Node("ASSIGN", p.lineno(2), [p[1], p[3]])

def p_statement_assigncommand(p):
   """
   statement : identifierchain ASSIGN commandcall SEMI
   """
   p[0] = Node("ASSIGNCOMMAND", p.lineno(2), [p[1], p[3]])

def p_statement_commandcall(p):
   """
   statement : commandcall SEMI
   """
   p[0] = Node("COMMANDCALL", p.lineno(1), [p[1]])

def p_commandcall(p):
   """
   commandcall : identifierchain LPAREN expressionlist RPAREN
               | identifierchain LPAREN RPAREN
   """
   if len(p) == 5:      
      p[0] = Node("COMMAND", p.lineno(1), [p[1], p[3]])
   elif len(p) == 4:
      exprlistNode = Node("EXPRESSIONLIST", p.lineno(1), [])
      p[0] = Node("COMMAND", p.lineno(1), [p[1], exprlistNode])

def p_expressionlist(p):
   """
   expressionlist : expression
                  | expressionlist COMMA expression
   """
   if len(p) == 2:
      p[0] = Node("EXPRESSIONLIST", p.lineno(1), [p[1]])
   else:
      p[1].children.append(p[3])
      p[0] = p[1]
      
def p_expression_binop(p):
   """
   expression : expression PLUS expression
              | expression MINUS expression
              | expression TIMES expression
              | expression DIVIDE expression
              | expression EQUALS expression
              | expression GT expression
              | expression LT expression
              | expression GE expression
              | expression LE expression
   """   
   p[0] = BinopNode("BINOP", p.lineno(2), [p[1], p[3]], p[2])

def p_expression_num(p):
    'expression : NUMBER'
    p[0] = NumberNode("NUMBER", p.lineno(1), [], p[1])

def p_expression_string(p):
   "expression : STRING"
   p[0] = StringNode("STRING", p.lineno(1), [], p[1])

def p_identifierchain(p):
   """
   identifierchain : IDENTIFIER
                   | IDENTIFIER DOT identifierchain
   """
   if len(p) == 2:
      p[0] = IdentifierNode("IDENTIFIER", p.lineno(1), [], p[1], CURRENTFILE[:], CURRENTSCRIPT[:])
   elif len(p) == 4:
      p[0] = IdentifierNode("IDENTIFIER", p.lineno(1), [p[3]], p[1], CURRENTFILE[:], CURRENTSCRIPT[:])

def p_expression_identifier(p):
   """
   expression : identifierchain
   """
   p[0] = p[1]

def p_expression_expr(p):
    'expression : LPAREN expression RPAREN'
    p[0] = ParensNode("PARENS", p.lineno(1), [p[2]])

def p_error(p):
    raise script_error.DSyntaxError(CURRENTFILE, CURRENTSCRIPT, p.lineno, p.value)

class Node():
   def __init__(self, kind, lineno, children=None, leaf=None):
      self.kind = kind
      self.lineno = lineno
      if children:
         self.children = children
      else:
         self.children = []
      self.leaf = leaf

   def pprint(self, f, level=0):
      line = ("  "*level, str(self.kind))
      if self.leaf is not None:
         line += (": ", str(self.leaf))
      f.write("".join(line))
      f.write("\n")
      for child in self.children:
         try:
            child.pprint(f, level+1)
         except AttributeError:
            print child.kind, child.children, child.leaf

class NumberNode(Node):
   def evaluate(self, symbols):
      return self.leaf

class StringNode(Node):
   def evaluate(self, symbols):
      return self.leaf

class IdentifierNode(Node):
   def __init__(self, kind, lineno, children, leaf, fn, scriptId):
      Node.__init__(self, kind, lineno, children, leaf)

      self.fn = fn
      self.scriptId = scriptId
   
   def evaluate(self, symbols):
      return symbols.getVar(self)

class BinopNode(Node):
   def evaluate(self, symbols):
      lhs = self.children[0].evaluate(symbols)
      rhs = self.children[1].evaluate(symbols)
      try:
         if self.leaf == "+":
            return lhs + rhs
         elif self.leaf == "-":
            return lhs - rhs
         elif self.leaf == "*":
           return lhs * rhs
         elif self.leaf == "/":
            return lhs / rhs
         elif self.leaf == "==":
            return (lhs == rhs)
         elif self.leaf == ">":
            return (lhs > rhs)
         elif self.leaf == "<":
            return (lhs < rhs)
         elif self.leaf == ">=":
            return (lhs >= rhs)
         elif self.leaf == "<=":
            return (lhs <= rhs)
      except TypeError:
         if self.leaf == "+":
            return str(lhs) + str(rhs)
         raise script_error.DOperatorError(CURRENTFILE, CURRENTSCRIPT, self.lineno, self.leaf, lhs, rhs)

class ParensNode(Node):
   def evaluate(self, symbols):
      return self.children[0].evaluate(symbols)

def parse(s, fn, scriptId):
   global CURRENTFILE
   global CURRENTSCRIPT
   CURRENTFILE = fn
   CURRENTSCRIPT = scriptId
   return parser.parse(s)

parser = yacc.yacc()


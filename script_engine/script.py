import os

import script_yacc
import script_compiler

import settings
import data
import events

OUT_AST = ".\\ast.txt"
OUT_CMDS = ".\\cmds.txt"

SCRIPTSEP = "###"

def getSource(fn, scriptId):
   f = open(fn, "r")
   lines = f.readlines()
   f.close()

   title = "%s%s%s" % (SCRIPTSEP, scriptId, SCRIPTSEP)

   code = []
   inCode = False
   for i in range(0, len(lines)):
      line = lines[i]
      if not inCode:
         if line.startswith(title):
            inCode = True
      else:
         if line.startswith(SCRIPTSEP):
            inCode = False
            break
         else:
            code.append(line)

   return "".join(code)        
   

class Script():
   def __init__(self, node, triggered=True):
      if triggered:
         trig = data.getAttr(node, "trigger", data.D_STRING)
         if trig == "investigate":
            self.trigger = events.EV_INVESTIGATE
         elif trig == "walkonto":
            self.trigger = events.EV_WALKONTO
         elif trig == "load":
            self.trigger = events.EV_LOAD
         elif trig == "newgame":
            self.trigger = events.EV_NEWGAME

      fn = os.path.join(settings.path, "data", data.getAttr(node, "source", data.D_STRING))
      scriptId = data.getAttr(node, "id", data.D_STRING)

      source = getSource(fn, scriptId)
      ast = script_yacc.parse(source, fn, scriptId)

      f = open(OUT_AST, "w")
      ast.pprint(f)
      f.close()
      
      self.commands = script_compiler.toCommands(ast)

   def __getitem__(self, i):
      return self.commands[i]

def writeAST(ast, fn):
   f = open(fn, "w")
   ast.pprint(f)
   f.close()

def writeCommands(commands, fn):
   f = open(fn, "w")
   for cmd in commands:
      f.write(str(cmd))
      f.write("\n")
   f.close()
      
      
      

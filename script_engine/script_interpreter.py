import sys, traceback

import script_yacc
import script_compiler
import symbols
import script
from commands import *

import globs
import data

class ScriptEngine():
   __shared_state = {}
   
   def __init__(self):
      self.__dict__ = self.__shared_state

   def setup(self, game):
      self.symbols = symbols.Symbols(game, self)

      self.script = None
      self.result = False
      self.currentCmd = 0

      self.caller = None

      self.waitingFor = None

      #determine behaviour scripts
      root = data.getTreeRoot(globs.BEHAVIOURS)
      self.behaviours = {}
      for behaviourNode in data.getChildren(root, "behaviour"):
         i = data.getAttr(behaviourNode, "index", data.D_INT)
         s = data.getChild(behaviourNode, "script")
         self.behaviours[i] = script.Script(s, False)
      
   def run(self, script, caller=None):
      self.script = script
      self.currentCmd = 0

      self.caller = caller

      self.waitingFor = None

      self.executeScript()

   def executeScript(self):
      while self.waitingFor is None:
         try:
            cmd = self.script[self.currentCmd]
            self.handleCommand(cmd)
            self.currentCmd += 1
         except IndexError:
            self.script = None
            break

   def handleCommand(self, cmd):
      if cmd[0] == CMD_PRINT:
         print cmd[1].evaluate(self.symbols)
      elif cmd[0] == CMD_ASSIGN:
         idChainNode = cmd[1]
         exprNode = cmd[2]
         self.symbols.setVar(idChainNode, exprNode.evaluate(self.symbols))
      elif cmd[0] == CMD_COMMANDASSIGN:
         idChainNode = cmd[1]
         commandNode = cmd[2]
         commandIdChainNode, argListNode = commandNode.children
         argNodeList = argListNode.children
         args = [argNode.evaluate(self.symbols) for argNode in argNodeList]
         result = self.symbols.doCommand(commandIdChainNode, args)
         self.symbols.setVar(idChainNode, result)
      elif cmd[0] == CMD_EVAL:
         exprNode = cmd[1]
         self.result = exprNode.evaluate(self.symbols)
      elif cmd[0] == CMD_GOTOREL:
         self.currentCmd += cmd[1]
      elif cmd[0] == CMD_IFFALSEGOTOREL:
         if not self.result:
            self.currentCmd += cmd[1]
      elif cmd[0] == CMD_COMMANDCALL:
         commandNode = cmd[1]
         idChainNode, argListNode = commandNode.children
         argNodeList = argListNode.children
         args = [argNode.evaluate(self.symbols) for argNode in argNodeList]
         self.symbols.doCommand(idChainNode, args)
      else:
         print "Unknown command"

   def processBehaviour(self, b):
      try:
         s = self.behaviours[b]
         self.run(s)
      except KeyError:
         pass

   def tick(self):
      if (self.script is not None):
         if self.waitingFor is None:
            self.executeScript()
         else:
            if not self.waitingFor.busy:
               self.waitingFor = None
               self.executeScript()

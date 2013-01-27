import script_error

import pokemon
import dialog
import sprite

class Symbols():
   def __init__(self, game, scriptEngine):
      self.game = game
      self.scriptEngine = scriptEngine
      
      self.locals = {}
      self.commands = {"foo": self.command_foo,
                       "lock": self.command_lock,
                       "unlock": self.command_unlock,
                       "facePlayer": self.command_facePlayer,
                       "dialog": self.command_dialog,
                       "generatePokemon": self.command_generatePokemon}

   def getObject(self, objName):
      if objName == "PLAYER":
         return self.game.player
      elif objName == "CALLER":
         return self.scriptEngine.caller
      elif objName == "MAP":
         return self.game.player.map
      elif objName == "SAVE":
         return self.game.savegame
      else:
         raise script_error.DNameError("FILE", "SCRIPT", 0, objName)

   def getVar(self, idChainNode):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         try:
            obj = self.getObject(idChainNode.leaf)
         except script_error.DLookupError as e:
            raise script_error.DNameError(idChainNode.fn, idChainNode.scriptId, idChainNode.lineno, e.name)
         try:
            return obj.getVarFromNode(nextNode)
         except script_error.DLookupError as e:
            raise script_error.DNameError(idChainNode.fn, idChainNode.scriptId, idChainNode.lineno, e.name)
      else:
         try:
            return self.locals[idChainNode.leaf]
         except KeyError:
            raise script_error.DNameError("FILE", "SCRIPT", 0, idChainNode.leaf)

   def setVar(self, idChainNode, val):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         obj = self.getObject(idChainNode.leaf)
         obj.setVarFromNode(nextNode, val)
      else:
         self.locals[idChainNode.leaf] = val

   def doCommand(self, idChainNode, args=[]):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         try:
            obj = self.getObject(idChainNode.leaf)
         except script_error.DLookupError as e:
            raise script_error.DNameError(idChainNode.fn, idChainNode.scriptId, idChainNode.lineno, e.name)
         try:
            return obj.doCommand(nextNode, args)
         except script_error.DLookupError as e:
            raise script_error.DNameError(idChainNode.fn, idChainNode.scriptId, idChainNode.lineno, e.name)            
      else:
         try:
            command = self.commands[idChainNode.leaf]
         except KeyError:
            raise script_error.DNameError("FILE", "SCRIPT", 0, idChainNode.leaf)
         return command(*args)

   def command_foo(self, *args):
      if args:
         print "Called foo with args: %s" % str(args)
      else:
         print "Called foo with no arg"

   def command_lock(self):
      self.game.player.lock()
      try:
         self.scriptEngine.caller.lock()
      except AttributeError:
         pass

   def command_unlock(self):
      self.game.player.unlock()
      try:
         self.scriptEngine.caller.unlock()
      except AttributeError:
         pass

   def command_facePlayer(self):
      difference = (self.game.player.position[0]-self.scriptEngine.caller.position[0],
                    self.game.player.position[1]-self.scriptEngine.caller.position[1])
      if difference == (0, -1): #if player is above caller
         self.scriptEngine.caller.direction = sprite.DIR_UP
      elif difference == (0, 1): #if player is below caller
         self.scriptEngine.caller.direction = sprite.DIR_DOWN
      elif difference == (-1, 0): #if player is to left of caller
         self.scriptEngine.caller.direction = sprite.DIR_LEFT
      elif difference == (1, 0): #if player is to right of caller
         self.scriptEngine.caller.direction = sprite.DIR_RIGHT

   def command_dialog(self, text, last=False):
      d = dialog.Dialog(text, self.game.screen, not last)
      self.game.foregroundObject = d
      self.scriptEngine.waitingFor = d      

   def command_generatePokemon(self, species, level):
      return pokemon.Pokemon(species, level)

   def flushLocals(self):
      self.locals = {}

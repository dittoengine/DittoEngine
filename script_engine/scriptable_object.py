import script_error

class ScriptableObject():
   def __init__(self):
      self.scriptCommands = {}

   def getObject(self, name):
      raise script_error.DLookupError(name)

   def getVarFromNode(self, idChainNode):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         obj = self.getObject(idChainNode.leaf)
         return obj.getVarFromNode(nextNode)
      else:
         return self.getVar(idChainNode.leaf)

   def getVar(self, name):
      raise script_error.DLookupError(name)

   def setVarFromNode(self, idChainNode, val):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         obj = self.getObject(idChainNode.leaf)
         obj.setVarFromNode(nextNode, val)
      else:
         self.setVar(idChainNode.leaf, val)

   def setVar(self, name, val):
      raise script_error.DLookupError(name)

   def doCommand(self, idChainNode, args=[]):
      if idChainNode.children:
         nextNode = idChainNode.children[0]
         obj = self.getObject(idChainNode.leaf)
         return obj.doCommand(nextNode, args)
      else:
         try:
            command = self.scriptCommands[idChainNode.leaf]
         except KeyError:
            raise script_error.DLookupError(idChainNode.leaf)
         return command(*args)

import globs
import xml.etree.ElementTree as ET
import os
import data
import error
import settings

class Move():
   def __init__(self, moveId):
      self.moveId = moveId
      
      fn = os.path.join(settings.path, "data", globs.MOVES)
      root = data.getTreeRoot(fn)

      self.moveNode = None
      for m in data.getChildren(root, "move"):
         if data.getAttr(m, "id", data.D_STRING) == moveId:
            self.moveNode = m
            break
      if self.moveNode is None:
         raise error.DittoInvalidResourceException(fn, "MOVE %s" % self.moveId)

      self.name = data.getAttr(self.moveNode, "name", data.D_STRING)
      self.maxPP = data.getAttr(self.moveNode, "pp", data.D_INT)
      self.currPP = self.maxPP

import os

import objects
import script_engine
import settings
import data

EV_INVESTIGATE = 0
EV_WALKONTO = 1
EV_LOAD = 2
EV_NEWGAME = 3

class ScriptEvent():
   """Class to allow placing a script onto a map."""
   
   def __init__(self, node, mMap):
      """
      Set up the event and create the script.

      node - the <script> node to get data from.
      mMap - the map the script belongs to.
      """

      #store the map for later
      self.map = mMap

      #parse the node
      self.position = tuple(data.getAttr(node, "position", data.D_INT2LIST))
      trigger = data.getAttr(node, "trigger", data.D_STRING)
      if trigger == "investigate":
         self.trigger = EV_INVESTIGATE
      elif trigger == "walkonto":
         self.trigger = EV_WALKONTO

      #event levels aren't currently checked
      self.level = 0

      #create the script object
      self.script = script_engine.Script(node)

   def activate(self):
      """Activate the script event."""

      #call the script engine to run the script
      self.map.scriptEngine.run(self.script)

class Warp():
   """
   Class to place warps onto the map.

   Note - possible to do this longhand with a <script> object.
   """
   
   def __init__(self, node, mMap):
      """
      Set up the warp and create the script.

      node - the <warp> node to get data from.
      mMap - the map the warp belongs to.
      """

      #store the map for later
      self.map = mMap

      #parse the node
      self.position = tuple(data.getAttr(node, "position", data.D_INT2LIST))
      self.targetMap = os.path.join(settings.path, "data", data.getAttr(node, "targetmap", data.D_STRING))
      self.targetPosition = tuple(data.getAttr(node, "targetposition", data.D_INT2LIST))

      #triggered by walkonto
      self.trigger = EV_WALKONTO

      #event levels aren't currently checked
      self.level = 0
      self.targetLevel = 0

      #we're going to duck-type ourselves as a script.Script object, so set the commands attribute                                    
      #self.commands = [[script.CMD_LOCK],
      #                 [script.CMD_FADEOUTANDIN, 8],
      #                 [script.CMD_WAIT, 4],
      #                 [script.CMD_WARP, self.targetMap, self.targetPosition, self.targetLevel],
      #                 [script.CMD_UNLOCK]]

   def activate(self):
      """Activate the warp event"""

      #class the script engine to run the script
      self.map.scriptEngine.run(self, self.map)

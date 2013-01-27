import random

import sprite
import events
import data
import error
import script_engine

#define movement constants
MT_NONE = 0
MT_WANDER = 1
MT_TRACK = 2

#used to input steps for tracking NPCs
INSTRUCTIONS = {"u": sprite.DIR_UP,
                "d": sprite.DIR_DOWN,
                "l": sprite.DIR_LEFT,
                "r": sprite.DIR_RIGHT}

#wandering NPCs have a 1 in 20 chance to move per frame
WANDERCHANCE = 0.05

def taxicab(position1, position2):
   """Return the taxicab distance between two points."""
   
   return abs(position1[0]-position2[0])+abs(position1[1]-position2[1])

class NPC(sprite.Sprite):
   """NPC class extending Sprite with auto movements and event scripts."""
   
   def __init__(self, node, mMap, position=None, level=None):
      """
      Initialise the sprite, and set up movement and scripts.

      node - the <npc> node.
      mMap - the map to start on.
      position - the position to start in. If unspecified gets taken from the <npc> node.
      level - the level to start on. If unspecified gets taken from the <npc> node.
      """

      #initialize the sprite
      sprite.Sprite.__init__(self, node, mMap, position, level)

      self.initialPosition = self.position #store initial position anchor

      #determine what auto movements to do
      #use the first <movement> node if one exists, otherwise no movement
      self.move = MT_NONE
      movements = data.getChildren(node, "movement")
      if movements:
         movementNode = movements[0]
         movementType = data.getAttr(movementNode, "type", data.D_STRING)

         #if asked to wander, set movement and get wander radius
         #note this uses taxicab distance, and a taxicab circle is a diamond like this:
         #  X
         # XXX
         #XX.XX
         # XXX
         #  X
         #maybe change this due to the possibility to easily block an npc on the diamond points
         if movementType == "wander":
            self.move = MT_WANDER
            self.wanderRadius = data.getAttr(movementNode, "radius", data.D_INT)

         #if asked to follow a track , set the movement and parse for the course  
         elif movementType == "track":
            self.move = MT_TRACK
            self.course = []
            self.stepCycle = 0
            for op in data.getAttr(movementNode, "course", data.D_STRING).split(","):
               try:
                  self.course.append(INSTRUCTIONS[op])
               except KeyError:
                  raise error.DUnsupportedError("Unknown NPC file", "NPC movement step", op)

      #create any event scripts
      self.scripts = {}
      for s in data.getChildren(node, "script"):
         if data.getAttr(s, "trigger", data.D_STRING) == "investigate":
            self.scripts[events.EV_INVESTIGATE] = script_engine.Script(s)

   def onInvestigate(self):
      """Called when the NPC is investigated. Run the investigate event if the is one."""

      #if there is an investigate script, and we're not currently busy, run the script
      if self.scripts.has_key(events.EV_INVESTIGATE) and not self.busy:
         s = self.scripts[events.EV_INVESTIGATE]
         self.scriptEngine.run(s, self)

   def tick(self):
      """Tick the NPC one frame."""

      #if we're about to finish a step and we're on a track movement, advance the step counter
      #if we've finished going round the track, go back to the beginning
      if self.walkCycle+self.speed >= 8 and self.move == MT_TRACK:
         self.stepCycle += 1
         if self.stepCycle >= len(self.course):
            self.stepCycle = 0

      #tick the sprite
      sprite.Sprite.tick(self)

      #if we're not currently busy (ie not in the middle of a step) then check whether to start a new step
      if not self.busy:

         #if we're wandering, see whether we should take a step
         #if so, then determine which directions are allowed by the wander radius
         #if we have at least one option, pick a random option and walk in that direction
         if self.move == MT_WANDER:
            if random.random() < WANDERCHANCE:
               options = []
               if taxicab((self.position[0],self.position[1]-1), self.initialPosition) <= self.wanderRadius:
                  options.append(sprite.DIR_UP)
               if taxicab((self.position[0],self.position[1]+1), self.initialPosition) <= self.wanderRadius:
                  options.append(sprite.DIR_DOWN)
               if taxicab((self.position[0]-1,self.position[1]), self.initialPosition) <= self.wanderRadius:
                  options.append(sprite.DIR_LEFT)
               if taxicab((self.position[0]+1,self.position[1]), self.initialPosition) <= self.wanderRadius:
                  options.append(sprite.DIR_RIGHT)

               if options:
                  self.walk(random.choice(options))

         #if we're moving on a track, get the new step (which was advanced before the sprite tick) and perform it         
         elif self.move == MT_TRACK:
            step = self.course[self.stepCycle]
            self.walk(step)

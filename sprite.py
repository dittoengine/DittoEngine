import os

import objects
import settings
import tileset
import globs
import animation
import sound
import data
import script_engine

#define direction constants
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

#define sprite status constants
S_WALK = 0
S_RUN = 1
S_BIKE = 2
S_TERRAIN = 3

#define move permission constants
#move permission is taken mod 8 to see what style it is
SWITCH = 0
BLOCK = 1
CLEAR = 2
BRIDGE = 3
TERRAIN = 4

class Sprite(objects.VisibleObject):
   """Class for moving, animated sprites."""
   
   def __init__(self, node, mMap, position=None, level=None):
      """
      aa

      node - the <sprite> node.
      mMap - the map to put the sprite on.
      position - the position to start at. If None it gets taken from the node.
      level - the level to start on. If None it gets taken from the node.
      """

      #init the VisibleObject
      objects.VisibleObject.__init__(self)

      #store the map for later
      self.map = mMap

      #create the tileset
      #determine the tile offset, so that the sprite is drawn at the centre bottom of a map tile
      tilesetPath = os.path.join(settings.path, "data", data.getAttr(node, "tileset", data.D_STRING))
      self.tileset = tileset.Tileset(tilesetPath)

      #determine position, and initialise destination to position
      if position is None:
         self.position = tuple(data.getAttr(node, "position", data.D_INT2LIST))
      else:
         self.position = position
      self.destination = self.position

      #determine the level
      if level is None:
         self.level = data.getAttr(node, "level", data.D_INT)
      else:
         self.level = level

      #find out the id, if there is one
      self.id = data.getOptionalAttr(node, "id", data.D_STRING, None)

      #initialise variables
      self.direction = DIR_DOWN
      self.status = S_WALK
      self.speed = 1 #walking
      self.walkCycle = 0
      self.busy = False
      self.switch = False
      self.locked = False
      self.hasBumped = False

      #no script engine given yet
      self.scriptEngine = script_engine.ScriptEngine()

      #for scripting
      self.scriptCommands["foo"] = self.command_foo

      #create the basic walk animations
      #set the current animation but don't play it (so it can be ticked without errors)
      self.animations[DIR_UP] = animation.Animation([12,12,13,13,14,14,15,15])
      self.animations[DIR_DOWN] = animation.Animation([0,0,1,1,2,2,3,3])
      self.animations[DIR_LEFT] = animation.Animation([4,4,5,5,6,6,7,7])
      self.animations[DIR_RIGHT] = animation.Animation([8,8,9,9,10,10,11,11])
      self.animation = self.animations[0]

   def tick(self):
      """Tick the sprite one frame."""

      #if we're performing a step, advance the walk cycle
      #if this finishes a step, set the new position and reset walk cycle
      #check for if we're on a switch and unreserve our position
      if self.busy:
         self.walkCycle += self.speed
         if self.walkCycle >= 8:
            self.position = self.destination
            self.walkCycle = 0

            #check for a switch move permission
            #action is got by taking the permission mod 8
            col = self.map.getCollisionData(self.position)
            action = col%8 
            if action == SWITCH:
               self.switch = True
            else:
               #if we just walked off a switch tile, set the level to that of the switch tile
               #level is got as 1 less than the permission divided by 8 rounded down
               if self.switch:
                  self.level = (col/8)-1
               self.switch = False

            #unreserve our position, now we've actually reached it
            if self.map.reservedPositions.has_key(self.position):
               self.map.reservedPositions.pop(self.position)

            #no longer busy
            self.busy = False

      #tick the Visible Object (deals with animations)      
      objects.VisibleObject.tick(self)

   def getTile(self):
      """Get the current tile of the sprite."""

      #if we're animated, used the animation to get the tile index
      #else just return the correct standard tile
      if self.animation.active:
         i = self.animation.getFrame()
      elif self.direction == DIR_UP:
         i = 12
      elif self.direction == DIR_DOWN:
         i = 0
      elif self.direction == DIR_LEFT:
         i = 4
      elif self.direction == DIR_RIGHT:
         i = 8

      #return the actual tile
      return self.tileset[i]

   def getMoveOffset(self):
      """Find the offset of the sprite due to movement."""

      #steps take 8 frames to complete, so divide the tile into 8 and use walk cycle to determine position
      if self.direction == DIR_UP:
         return 0, (-1*self.walkCycle*globs.TILESIZE[1])/8
      elif self.direction == DIR_DOWN:
         return 0, (self.walkCycle*globs.TILESIZE[1])/8
      elif self.direction == DIR_LEFT:
         return (-1*self.walkCycle*globs.TILESIZE[0])/8, 0
      elif self.direction == DIR_RIGHT:
         return (self.walkCycle*globs.TILESIZE[0])/8, 0

   def getOffset(self):
      """Get the combined offset from tile size and movement."""

      #combine the two offsets and return
      moveOffset = self.getMoveOffset()
      return self.tileset.tileOffset[0]+moveOffset[0], self.tileset.tileOffset[1]+moveOffset[1]

   def canMoveTo(self, col):
      """
      Determine whether the sprite can move to a specific movement permission.

      col - the movement permission.
      """

      #determine level and action
      level = (col/8)-1
      action = col%8

      #if it's a switch, then if it's on our level, or universal (most likely), we can move to it
      #otherwise not
      if action == SWITCH:
         if level == self.level or level == -1:
            return True
         else:
            return False

      #if it's a block, we can't move to it   
      elif action == BLOCK:
         return False

      #if it's clear, then if it's on our level or universal, or we're currently on a switch, we can move to it
      #otherwise not
      elif action == CLEAR:
         if level == self.level or level == -1 or self.switch:
            return True
         else:
            return False

      #if it's a bridge, we can move to it on any level
      #MAYBE CHANGE - so it requires that you must be on the block's level or higher??
      elif action == BRIDGE:
         return True

      #for Surf-style HMs
      elif action == TERRAIN:
         if self.status == S_TERRAIN:
            return True
         else:
            return False

      #else it's undefined as yet, so we can't go there
      #maybe raise an error instead??
      else:
         return False

   def walk(self, direction, force=False, isPlayer=False):
      """
      Walk (or run etc.) to a new position.

      direction - the direction to move.
      force - if True, bypass checks for being locked or busy.
      isPlayer - True when called by the player.
      """

      #check whether we are able to move
      if (not (self.busy or self.locked) or force) and self.visible:

         #set our direction as given, and calculate the destination position
         self.direction = direction
         if direction == DIR_UP:
            self.destination = self.position[0], self.position[1]-1
         elif direction == DIR_DOWN:
            self.destination = self.position[0], self.position[1]+1
         elif direction == DIR_LEFT:
            self.destination = self.position[0]-1, self.position[1]
         elif direction == DIR_RIGHT:
            self.destination = self.position[0]+1, self.position[1]

         #if we can move to the movement permission, and the mpa is empty, then start the step
         #set ourselves as busy to start moving when next ticked, and play the correct animation
         #notify the map that we are coming to the destination position
         col = self.map.getCollisionData(self.destination)
         if (self.canMoveTo(col) and self.map.emptyAt(self.destination)):
            self.busy = True
            self.animation = self.animations[direction]
            self.animation.play(False)
            self.hasBumped = False
            if self.status == S_TERRAIN:
               action = col%8
               if action != TERRAIN:
                  self.setStatus(S_WALK)
            self.map.walkonto(self, self.destination, isPlayer)

         #if we can't move to the destination, then if we're the player and we haven't bumped yet, play the sound effect
         else:
            if isPlayer and not self.hasBumped:
               sound.playEffect(sound.SD_BUMP)
               self.hasBumped = True

   def walkForward(self, force=False, isPlayer=False):
      self.walk(self.direction, force, isPlayer)

   def setStatus(self, status):
      self.status = status
      self.tileset = self.statusTilesets[status]

   def getVar(self, name):
      if name == "level":
         return self.level
      else:
         raise script_engine.DLookupError(name)

   def setVar(self, name, val):
      if name == "level":
         self.level = val
      else:
         raise script_engine.DLookupError(name)

   def command_foo(self, arg=None):
      if arg:
         print "Called sprite foo with arg: %s" % arg
      else:
         print "Called sprite foo with no arg"
      return "RETURN"

   def lock(self):
      """Lock the sprite."""
      
      self.locked = True

   def unlock(self):
      """Unlock the sprite."""
      
      self.locked = False

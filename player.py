import os

import tileset
import settings
import animation
import sprite
import pokemon
import sound
import data
import error

STATUSNAMES = {"surf": sprite.S_TERRAIN}

class Player(sprite.Sprite):
   """Class representing the player."""
   
   def __init__(self, node, mMap, position, level):
      """
      Set up the player.

      node - the <player> node.
      mMap - the map to start on.
      position - the position to start at.
      level - the level to start on.
      """

      #init the sprite
      sprite.Sprite.__init__(self, node, mMap, position, level)

      #create status tilesets
      self.statusTilesets = {}
      self.statusTilesets[sprite.S_WALK] = self.tileset
      for statusNode in data.getChildren(node, "status"):
         try:
            status = STATUSNAMES[data.getAttr(statusNode, "name", data.D_STRING)]
         except KeyError:
            raise data.DInvalidAttributeError(statusNode, "name")
         tsPath = os.path.join(settings.path, "data", data.getAttr(statusNode, "tileset", data.D_STRING))
         ts = tileset.Tileset(tsPath)
         self.statusTilesets[status] = ts

      #create an empty party
      #overridden with unpickled party if restoring from a save
      self.party = pokemon.Party()

      #set up scripting
      self.scriptCommands["addToParty"] = self.command_addToParty

   def walk(self, direction, force=False, isPlayer=True):
      sprite.Sprite.walk(self, direction, force, True)

      if (self.destination[0] < 0) and self.busy:
            hold = self.map
            con = self.map.connectedMaps[sprite.DIR_LEFT][0]
            offset = self.map.connectedMaps[sprite.DIR_LEFT][1]
            self.position = self.position[0]+con.size[0], self.position[1]-offset
            self.destination = self.position[0]-1, self.position[1]
            self.map = con
            hold.connectedMaps = {}
            self.map.loadConnections()
            self.map.connectedMaps[sprite.DIR_RIGHT] = (hold, -1*offset)
            del(hold.sprites["PLAYER"])
            self.map.sprites["PLAYER"] = self
            sound.playMusic(self.map.music)
      elif (self.destination[0] >= self.map.size[0]) and self.busy:
            hold = self.map
            con = self.map.connectedMaps[sprite.DIR_RIGHT][0]
            offset = self.map.connectedMaps[sprite.DIR_RIGHT][1]
            self.position = self.position[0]-self.map.size[0], self.position[1]-offset
            self.destination = self.position[0]+1, self.position[1]
            self.map = con
            hold.connectedMaps = {}
            self.map.loadConnections()
            self.map.connectedMaps[sprite.DIR_LEFT] = (hold, -1*offset)
            del(hold.sprites["PLAYER"])
            self.map.sprites["PLAYER"] = self
            sound.playMusic(self.map.music)
      elif (self.destination[1] < 0) and self.busy:
            hold = self.map
            con = self.map.connectedMaps[sprite.DIR_UP][0]
            offset = self.map.connectedMaps[sprite.DIR_UP][1]
            self.position = self.position[0]-offset, self.position[1]+con.size[1]
            self.destination = self.position[0], self.position[1]-1
            self.map = con
            hold.connectedMaps = {}
            self.map.loadConnections()
            self.map.connectedMaps[sprite.DIR_DOWN] = (hold, -1*offset)
            del(hold.sprites["PLAYER"])
            self.map.sprites["PLAYER"] = self
            sound.playMusic(self.map.music)
      elif (self.destination[1] >= self.map.size[1]) and self.busy:
            hold = self.map
            con = self.map.connectedMaps[sprite.DIR_DOWN][0]
            offset = self.map.connectedMaps[sprite.DIR_DOWN][1]
            self.position = self.position[0]-offset, self.position[1]-self.map.size[1]
            self.destination = self.position[0], self.position[1]+1
            self.map = con
            hold.connectedMaps = {}
            self.map.loadConnections()
            self.map.connectedMaps[sprite.DIR_UP] = (hold, -1*offset)
            del(hold.sprites["PLAYER"])
            self.map.sprites["PLAYER"] = self
            sound.playMusic(self.map.music)

   def transferTo(self, mMap, position):
      del(self.map.sprites["PLAYER"])
      self.map.connectedMaps = {}
      
      self.map = mMap
      self.position = position

      self.map.sprites["PLAYER"] = self
      self.map.loadConnections()

      sound.playMusic(self.map.music)

   def getPositionInFront(self):
      if self.direction == sprite.DIR_UP:
         return self.position[0], self.position[1]-1
      elif self.direction == sprite.DIR_DOWN:
         return self.position[0], self.position[1]+1
      elif self.direction == sprite.DIR_LEFT:
         return self.positon[0]-1, self.position[1]
      elif self.direction == sprite.DIR_RIGHT:
         return self.position[0]+1, self.position[1]

   def surf(self):
      self.setStatus(sprite.S_TERRAIN)
      self.walkForward(True, True)

   def investigate(self):
      """Investigate the position in front of the player."""

      #find the target position, and have the map investigate it
      if self.direction == sprite.DIR_UP:
         target = self.position[0], self.position[1]-1
      elif self.direction == sprite.DIR_DOWN:
         target = self.position[0], self.position[1]+1
      elif self.direction == sprite.DIR_LEFT:
         target = self.position[0]-1, self.position[1]
      elif self.direction == sprite.DIR_RIGHT:
         target = self.position[0]+1, self.position[1]  
      self.map.investigate(target, self.level)

   def command_addToParty(self, poke):
      self.party.add(poke)

import os
import xml.etree.ElementTree as ET

import settings
import tileset
import sprite
import npc
import script_engine
import events
import error
import data
import globs
import sound

#initialise constants
BD_NW = 0
BD_NE = 1
BD_SW = 2
BD_SE = 3

class Layer():
   """Class to represent a single layer of a map."""
   
   def __init__(self):
      """
      Create a blank layer, which must be populated by calling some kind of opening function.
      """

      #create initial tile array and animation dictionary for walkonto animations 
      self.array = []
      self.animations = {}

   def openTMXNode(self, layerNode):
      """
      Use a <layer> node from a TMX file to create the layer data.

      layerNode - the TMX <layer> node
      """
      
      #find the level
      self.level = None
      props = layerNode.find("properties")
      if props is None:
         raise error.DittoInvalidResourceException("Unknown TMX file", "No layer properties defined.")
      for p in props.getchildren():
         if p.attrib["name"] == "level":
            try:
               self.level = int(p.attrib["value"])
            except ValueError:
               raise error.DittoInvalidResourceException("Unknown TMX file", "Level is not an integer.")
            break
      if self.level is None:
         raise error.DittoInvalidResourceException("Unknown TMX file", "Layer property \"level\" is not defined.")

      #get hold of the data
      data = layerNode.find("data")

      #if it's csv encoded, simply split into lines,
      #and split each line into tiles which can be added to the array
      if data.attrib["encoding"] == "csv":
         lines = data.text.split("\n")
         for line in lines:
            if line != "":
               listed = line.split(",")
               listed = filter(lambda a: a != "", listed) #remove any blank elements
               row = map(lambda a: int(a)-1, listed) #TMX indexes start at 1, we start at 0
               self.array.append(row)
      else:
         raise error.DittoUnsupportedException("Unknown TMX file", "TMX layer encoding", data.attrib["encoding"])

   def offsetElements(self, i):
      """
      Subtract an amount from each element in the tile array.

      Used to correct for multiple tilesets being offset by TMX format.

      i - the amount to subtract
      """

      #iterate over each tile and subtract
      #if the value is -1, indicating a blank tile, leave it as that
      for y in range(0, len(self.array)):
         for x in range(0, len(self.array[0])):
            if self.array[y][x] != -1:
               self.array[y][x] -= i

   def tick(self):
      """
      Update the map by one frame.

      Updates all the animations currently active on the map.
      """

      #tick each animation, and remember any animations which have finished
      #remove any finished ones from the dictionary
      finished = []
      for key, anim in self.animations.items():
         anim.tick()
         if not anim.active:
            finished.append(key)      
      for key in finished:
         self.animations.pop(key)

   def __getitem__(self, position):
      """
      Returns the tile at the position given.

      If the tile is animated, returns the correct animation frame.

      position - the x,y position coordinate to get.
      """

      #if the tile is animated, get the animation frame
      #otherwise just grab the required tile from the array
      if self.animations.has_key(position):
         t = self.animations[position].getFrame()
      else:
         t = self.array[position[1]][position[0]]
      return t

class Tilemap(script_engine.ScriptableObject):
   """
   Class representing a map object.
   """
   
   def __init__(self, fn):
      """
      Open the map data file, set border tiles and connections, and add NPCs and other events.

      fn - the filename of the map XML file.
      """

      #for the scripting engine
      script_engine.ScriptableObject.__init__(self)

      #store variables we'll need later
      self.fn = fn

      #get a script engine (singleton)
      self.scriptEngine = script_engine.ScriptEngine()

      #parse the XML file
      root = data.getTreeRoot(fn)
      self.music = os.path.join(settings.path, "data", data.getAttr(root, "music", data.D_STRING))

      #open the actual map data file to create the map tile data
      mapPath = os.path.join(settings.path, "data", data.getAttr(root, "file", data.D_STRING))
      self.openMap(mapPath)

      #create the tileset
      tilesetPath = os.path.join(settings.path, "data", data.getAttr(root, "tileset", data.D_STRING))
      self.tileset = tileset.Tileset(tilesetPath)

      #set the border tiles
      self.borderTiles = {}
      borderNode = data.getChild(root, "border")

      #set each border node with the correct tile indexes, subtracting 1 because the tileset starts at 1 not 0
      self.borderTiles[BD_NW] = data.getAttr(borderNode, "nw", data.D_INT)-1
      self.borderTiles[BD_NE] = data.getAttr(borderNode, "ne", data.D_INT)-1
      self.borderTiles[BD_SW] = data.getAttr(borderNode, "sw", data.D_INT)-1
      self.borderTiles[BD_SE] = data.getAttr(borderNode, "se", data.D_INT)-1
      
      #create any connections from the map
      #connected maps will not be loaded until the map becomes the main game map
      #connections are stored as {direction: (filename, offset)}
      self.connections = {}
      self.connectedMaps = {}
      for c in data.getChildren(root, "connection"):
         side = data.getAttr(c, "side", data.D_STRING)
         fp = os.path.join(settings.path, "data", data.getAttr(c, "map", data.D_STRING))
         offset = data.getAttr(c, "offset", data.D_INT)
         
         if side == "left":
            self.connections[sprite.DIR_LEFT] = (fp, offset)
         elif side == "right":
            self.connections[sprite.DIR_RIGHT] = (fp, offset)
         elif side == "up":
            self.connections[sprite.DIR_UP] = (fp, offset)
         elif side == "down":
            self.connections[sprite.DIR_DOWN] = (fp, offset)

      #create any NPCs, adding them to the sprite dictionary
      self.sprites = {}
      for n in data.getChildren(root, "npc"):
         spr = npc.NPC(n, self)
         self.sprites[spr.id] = spr

      #create a dictionary to hold positions reserved by moving sprites
      self.reservedPositions = {}

      #create script and warp events, adding them to the events dictionary
      #if a load script is defined, create it
      self.events = {}
      loadScript = None
      for s in data.getChildren(root, "script"):
         trigger = data.getAttr(s, "trigger", data.D_STRING)
         if trigger == "load":
            loadScript = script_engine.Script(s)   
         else:
            position = tuple(data.getAttr(s, "position", data.D_INT2LIST)) 
            self.events[position] = events.ScriptEvent(s, self)
            
      for w in root.findall("warp"):
         position = tuple(data.getAttr(w, "position", data.D_INT2LIST))
         self.events[position] = events.Warp(w, self)

      #if there is a load script, run it
      if loadScript is not None:
         self.scriptEngine.run(loadScript, self)

   def openMap(self, fn):
      ext = os.path.splitext(fn)[1]
      if ext == ".tmx":
         self.openTMX(fn)
      else:
         raise error.DittoUnsupportedException("map data extension", ext)

   def openTMX(self, fn):
      """
      Open a TMX file and use it to set map size and create tile layers and a collision layer.

      fn - the filename of the TMX file.
      """

      #parse the TMX XML markup
      tree = ET.parse(fn)
      root = tree.getroot()
      self.size = int(root.attrib["width"]), int(root.attrib["height"])

      #find the offset at which the collision and behaviour layers tile data is stored
      collisionTilesetOffset = None
      behaviourTilesetOffset = None
      for ts in root.findall("tileset"):
         if ts.attrib["name"] == "collision":
            collisionTilesetOffset = int(ts.attrib["firstgid"])-1
         elif ts.attrib["name"] == "behaviour":
            behaviourTilesetOffset = int(ts.attrib["firstgid"])-1
      if collisionTilesetOffset is None:
         raise error.DittoInvalidResourceException(fn, "Collision tileset")
      if behaviourTilesetOffset is None:
         raise error.DittoInvalidResourceException(fn, "Behaviour tileset")

      #create each layer, separating the collision and behaviour data
      self.layers = []
      self.collisionLayer = None
      self.behaviourLayer = None
      for layer in root.findall("layer"):
         l = Layer()
         l.openTMXNode(layer)
         if l.level == -1: #collision layer indicated by level == -1
            self.collisionLayer = l
         elif l.level == -2:
            self.behaviourLayer = l
         else:
            self.layers.append(l)
      if self.collisionLayer is None:
         raise error.DittoInvalidResourceException(fn, "Collision data layer")
      if self.behaviourLayer is None:
         raise error.DittoInvalidResourceException(fn, "Behaviour data layer")

      #compensate for tilesets not starting at 1
      self.collisionLayer.offsetElements(collisionTilesetOffset)
      self.behaviourLayer.offsetElements(behaviourTilesetOffset)

   def getLayersOnLevel(self, i):
      """
      Return a list of layers on this map on a given level.

      i - the level to look on.
      """

      #return a filtered copy of the map's layers
      return filter(lambda a: a.level == i, self.layers)

   def getBorderTile(self, position):
      """
      Return the index of the border tile at a position.

      position - the position of the tile on the map
      """

      #determine the tiles position in the border, and return the relevant tile index
      borderPosition = (position[0]%2, position[1]%2)
      if borderPosition == (0,0):
         return self.borderTiles[BD_NW]
      elif borderPosition == (1,0):
         return self.borderTiles[BD_NE]
      elif borderPosition == (0,1):
         return self.borderTiles[BD_SW]
      elif borderPosition == (1,1):
         return self.borderTiles[BD_SE]

   def walkonto(self, sprite, destination, isPlayer=False):
      """
      Deal with a sprite walking onto a tile, by animating if required and reserving the position.

      sprite - the sprite which is walking onto the tile.
      destination - the tile they're walking onto.
      """

      #if the destination is on the map, check the sprite's layer for walkonto animations
      #if there are any, play them
      #then reserve the position
      if (0 <= destination[0] < self.size[0]) and (0 <= destination[1] < self.size[1]):
         layers = self.getLayersOnLevel(sprite.level)
         for l in layers:
            tile = l[destination]
            if self.tileset.walkontoAnimations.has_key(tile):
               l.animations[destination] = self.tileset.walkontoAnimations[tile]
               l.animations[destination].play(False)
         self.reservedPositions[destination] = sprite      

      #if it's a player, check for events and deal with any
      if isPlayer:
         if self.events.has_key(destination):
            s = self.events[destination]
            if s.trigger == events.EV_WALKONTO:
               s.activate()

   def loadConnections(self):
      """
      Load all the connecting maps.

      Called when the map becomes the main game map.
      """

      #create each connecting map
      for direction, (fn, offset) in self.connections.items():
         self.connectedMaps[direction] = (Tilemap(fn), offset)

   def getCollisionData(self, position):
      """
      Get the collision tile index at a given position.

      position - the position to use.
      """
      
      #if it's on the map, simply return the collision data
      if (0 <= position[0] < self.size[0]) and (0 <= position[1] < self.size[1]):
         return self.collisionLayer.array[position[1]][position[0]] #direct indexing prevents checking for animations

      #otherwise see if it's on a connecting map
      #if it is, get it
      else:
         for key in self.connectedMaps:
            con = self.connectedMaps[key][0]
            offset = self.connectedMaps[key][1]
            if key == sprite.DIR_LEFT: 
               rel = position[0]+con.size[0], position[1]-offset
            elif key == sprite.DIR_RIGHT:
               rel = position[0]-self.size[0], position[1]-offset
            elif key == sprite.DIR_UP:
               rel = position[0]-offset, position[1]+con.size[1]
            elif key == sprite.DIR_DOWN:
               rel = position[0]-offset, position[1]-self.size[1]
            if (0 <= rel[0] < con.size[0]) and (0 <= rel[1] < con.size[1]):
               return con.getCollisionData(rel)

      #else it must be a border tile, return 1 (block)      
      return 1

   def getBehaviourData(self, position):
      """
      Get the behaviour value ata given position.

      position - the position to use.
      """

      if (0 <= position[0] < self.size[0]) and (0 <= position[1] < self.size[1]):
         return self.behaviourLayer.array[position[1]][position[0]] #direct indexing prevents checking for animations

      #otherwise see if it's on a connecting map
      #if it is, get it
      else:
         for key in self.connectedMaps:
            con = self.connectedMaps[key][0]
            offset = self.connectedMaps[key][1]
            if key == sprite.DIR_LEFT: 
               rel = position[0]+con.size[0], position[1]-offset
            elif key == sprite.DIR_RIGHT:
               rel = position[0]-self.size[0], position[1]-offset
            elif key == sprite.DIR_UP:
               rel = position[0]-offset, position[1]+con.size[1]
            elif key == sprite.DIR_DOWN:
               rel = position[0]-offset, position[1]-self.size[1]
            if (0 <= rel[0] < con.size[0]) and (0 <= rel[1] < con.size[1]):
               return con.getBehaviourData(rel)

      #else it must be a border tile, return -1 (no behaviour)      
      return -1

   def emptyAt(self, position):
      """
      Find out whether a given position is empty and available.

      position - the position to use.
      """

      #check for any sprites at the position
      for key in self.sprites:
         s = self.sprites[key]
         if s.position == position and s.visible: #not visible means it isn't taking up the tile
            return False

      #check whether the position is reserved   
      for pos in self.reservedPositions:
         if pos == position:
            return False

      #if nothing found, it must be empty   
      return True

   def getSpriteById(self, spriteId):
      """
      Get a given sprite by it's id.

      spriteId - the id of the sprite to find.
      """

      #find the required sprite
      return self.sprites[spriteId]

   def getObject(self, name):
      if name == "tileset":
         return self.tileset
      else:
         return self.getSpriteById(name)

   def getVar(self, name):
      raise KeyError

   def setVar(self, name, value):
      raise KeyError

   def investigate(self, target, level):
      """
      Called by a player to investigate a map for events.

      target - the position to look at
      level - the level to look on
      """

      #we haven't found anything yet
      found = False

      #check for sprites on the position and level
      #if one is found, call its onInvestigate method
      spriteIds = filter(lambda a: self.sprites[a].level == level, self.sprites)
      sprites = [self.sprites[x] for x in spriteIds]
      for s in sprites:
         if s.position == target and s.visible:
            s.onInvestigate()
            found = True
            break

      #if there was no sprite, check for any events triggered on investigate   
      if not found:
         if self.events.has_key(target):
            if self.events[target].trigger == events.EV_INVESTIGATE:
               self.events[target].activate()
               found = True

      #finally, check for a behaviour byte and process that
      if not found:
         b = self.getBehaviourData(target)
         self.scriptEngine.processBehaviour(b)
      
   def tick(self):
      """Update the map one frame"""

      #we don't need to do anything, just tick our components
      self.tileset.tick()
      for l in self.layers:
         l.tick()
      for key in self.sprites:
         self.sprites[key].tick()
      for key in self.connectedMaps:
         self.connectedMaps[key][0].tick()


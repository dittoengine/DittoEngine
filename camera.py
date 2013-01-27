import settings

import pygame

import sprite
import globs

class Camera():
   """Class to draw the world onto the screen"""
   
   def __init__(self, screen):
      """
      Store the screen and determine the centre tile.
      """

      #store the screen to draw onto later
      self.screen = screen

      #find the tile dimensions of the screen, and identify the centre tile
      self.size = settings.screenSize
      self.centre = ((self.size[0]+1)/2)-1,((self.size[1]+1)/2)-1

   def setPosition(self, mMap, position):
      """
      Place the camera in a static position.

      mMap - the map to put it on.
      position - the position to put it on.
      """

      #not attached to any object
      self.attach = None

      #set our map and position
      self.map = mMap
      self.position = position

   def attachTo(self, mObject):
      """
      Attach the camera to an object, usually the player.

      The object must have map and position attributes, and a getMoveOffset() method.
      It should also be local to the player, as the player's location determines what maps are loaded.

      mObject - the object to attach to.
      """

      #set the object we're attached to
      self.attach = mObject

   def drawFrame(self):
      """Draw a frame to the screen"""

      #find the map, position and offset to use
      #if we're attached, use the map, position and offset of the object
      #if we're not attached, use our own map and position, with no offset
      if self.attach != None:
         mMap = self.attach.map
         position = self.attach.position
         cameraOffset = self.attach.getMoveOffset()
      else:
         mMap = self.map
         position = self.position
         cameraOffset = (0,0)

      #draw in all the tiles
      #iterate over each level, going over each coordinate and drawing in the required tiles
      #only draw the border tiles in once, on the first pass
      bordersDrawn = False
      for level in range(0, 3):
            for x in range(-1, self.size[0]+1): #1 tile either side for when the object is moving halfway between tiles
               for y in range(-1, self.size[1]+1):

                  #convert the screen coordinates x, y into map coordinates
                  #if it's on the map, go through the map layers on the current level
                  #if they specify a tile in the current position, add it to our list of tiles to draw
                  reqTileLoc = position[0]-self.centre[0]+x, position[1]-self.centre[1]+y
                  reqTiles = []
                  if (reqTileLoc[0] >= 0) and (reqTileLoc[1] >= 0) and (reqTileLoc[0] < mMap.size[0]) and (reqTileLoc[1] < mMap.size[1]):
                     for layer in mMap.getLayersOnLevel(level):
                        i = layer[reqTileLoc]
                        if i >= 0: #if no tile is specified, this should be -1
                           reqTiles.append(mMap.tileset[i])

                  #otherwise start checking connected maps
                  #for each map, work out what the map coordinate would be on the map
                  #if it would be on that map, go through the layers on the current level
                  #if they specify a tile in the current position, add it to our list of tiles to draw
                  #if we did find one, stop looking for any more                  
                  else:
                     for direction, (con, offset) in mMap.connectedMaps.items():
                        if direction == sprite.DIR_LEFT: 
                           rel = reqTileLoc[0]+con.size[0], reqTileLoc[1]-offset
                        elif direction == sprite.DIR_RIGHT:
                           rel = reqTileLoc[0]-mMap.size[0], reqTileLoc[1]-offset
                        elif direction == sprite.DIR_UP:
                           rel = reqTileLoc[0]-offset, reqTileLoc[1]+con.size[1]
                        elif direction == sprite.DIR_DOWN:
                           rel = reqTileLoc[0]-offset, reqTileLoc[1]-mMap.size[1]
                        if (0 <= rel[0] < con.size[0]) and (0 <= rel[1] < con.size[1]):
                           for layer in con.getLayersOnLevel(level):
                              i = layer[rel]
                              if i >= 0:
                                 reqTiles.append(con.tileset[i])
                           break

                  #if we've still not found a tile yet for this position, and borders haven't been drawn in yet,
                  #then get the border tile for the current position.
                  if (len(reqTiles) == 0) and not bordersDrawn:
                     reqTiles.append(mMap.tileset[mMap.getBorderTile(reqTileLoc)])

                  #blit the required tiles to the correct position
                  for t in reqTiles:
                     self.screen.blit(t, ((x*globs.TILESIZE[0])-cameraOffset[0], (y*globs.TILESIZE[1])-cameraOffset[1]))

            #having finished the first pass, any borders needed shold have been drawn by now
            bordersDrawn = True

            #draw the map's sprites
            #filtering them by level gives the ids, so use this to build a list of sprites
            #sort by y value so higher sprites are drawn first
            #for each sprite, find its screen coordinates and offset, and use these to draw it
            spriteIds = filter(lambda a: mMap.sprites[a].level == level, mMap.sprites)
            sprites = [mMap.sprites[key] for key in spriteIds]
            sprites = sorted(sprites, key=lambda s: s.position[1])
            for s in sprites:
               if s.visible:
                  reqLoc = (s.position[0] - position[0] + self.centre[0]), (s.position[1] - position[1] + self.centre[1])
                  offset = s.getOffset()
                  self.screen.blit(s.getTile(), ((reqLoc[0]*globs.TILESIZE[0])+offset[0]-cameraOffset[0],
                                                 (reqLoc[1]*globs.TILESIZE[1])+offset[1]-cameraOffset[1]))

            #draw the sprites from connecting maps
            #use the same process as before
            for direction, (con, offset) in mMap.connectedMaps.items():
               spriteIds = filter(lambda a: con.sprites[a].level == level, con.sprites)
               sprites = [con.sprites[x] for x in spriteIds]
               sprites = sorted(sprites, key=lambda s: s.position[1])
               for s in sprites:
                  if s.visible:
                     if direction == sprite.DIR_LEFT: 
                        rel = s.position[0]-con.size[0], s.position[1]+offset
                     elif direction == sprite.DIR_RIGHT:
                        rel = s.position[0]+mMap.size[0], s.position[1]+offset
                     elif direction == sprite.DIR_UP:
                        rel = s.position[0]+offset, s.position[1]-con.size[1]
                     elif direction == sprite.DIR_DOWN:
                        rel = s.position[0]+offset, s.position[1]+mMap.size[1]
                     reqLoc = (rel[0] - position[0] + self.centre[0]), (rel[1] - position[1] + self.centre[1])
                     spriteOffset = s.getOffset()
                     self.screen.blit(s.getTile(), ((reqLoc[0]*globs.TILESIZE[0])+spriteOffset[0]-cameraOffset[0],
                                                    (reqLoc[1]*globs.TILESIZE[1])+spriteOffset[1]-cameraOffset[1]))

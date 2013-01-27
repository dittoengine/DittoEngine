import os
import xml.etree.ElementTree as ET

import pygame

import globs
import settings
import data

class Box(pygame.Surface):
   """
   Class to provide sized boxes from a tileset.
   """
   
   def __init__(self, size, fn=None):
      """
      Initialize a surface and draw the box onto it.

      size - the size of the box.
      fn - the path to a box xml config file.
      """

      #initialize the pygame Surface
      pygame.Surface.__init__(self, size)

      #if no filename given, use the game default box
      if fn == None:
         fn = os.path.join(settings.path, "data", globs.DIALOG)

      #parse the box xml file
      root = data.getTreeRoot(fn)
      tilesetPath = os.path.join(settings.path, "data", data.getAttr(root, "file", data.D_STRING))
      tileset = data.getImage(tilesetPath)
      transparency = data.getAttr(root, "transparency", data.D_INT3LIST)
      tileset.set_colorkey(transparency)
      tileSize = data.getAttr(root, "tilesize", data.D_INT2LIST)
      data.check((tileSize[0]+1)*3==tileset.get_width()+1, tilesetPath)
      data.check((tileSize[1]+1)*3==tileset.get_height()+1, tilesetPath)

      #fill transparent
      self.fill((255,0,255))
      self.set_colorkey((255,0,255))

      #cut each of the nine tiles out from the tileset
      tileNW = tileset.subsurface((0,0), tileSize)
      tileN = tileset.subsurface((tileSize[0]+1,0), tileSize)
      tileNE = tileset.subsurface(((tileSize[0]+1)*2,0), tileSize)
      tileW = tileset.subsurface((0,tileSize[1]+1), tileSize)
      tileC = tileset.subsurface((tileSize[0]+1,tileSize[1]+1), tileSize)
      tileE = tileset.subsurface(((tileSize[0]+1)*2,tileSize[1]+1), tileSize)
      tileSW = tileset.subsurface((0,(tileSize[1]+1)*2), tileSize)
      tileS = tileset.subsurface((tileSize[0]+1,(tileSize[1]+1)*2), tileSize)
      tileSE = tileset.subsurface(((tileSize[0]+1)*2,(tileSize[1]+1)*2), tileSize)

      #calculate how much of the box is not covered by edge tiles - all this middle must be covered by the centre tile
      #work out how many tiles it will take to cover that, and where to start drawing from
      middleSize = size[0]-(2*tileSize[0]), size[1]-(2*tileSize[1])
      dimensions = (middleSize[0]/tileSize[0])+1, (middleSize[1]/tileSize[1])+1
      origin = (size[0]-(dimensions[0]*tileSize[0]))/2, (size[1]-(dimensions[1]*tileSize[1]))/2

      #iterate over the required dimensions, drawing in the centre tiles
      #as we go down the first column only, draw in the left and right side tiles on the edge of the box
      #after we finish each column, draw the top and bottom tiles on the edge
      for x in range(0, dimensions[0]):
         for y in range(0, dimensions[1]):
            self.blit(tileC, (origin[0]+(x*tileSize[0]), origin[1]+(y*tileSize[1])))
            if x == 0:
               self.blit(tileW, (0, origin[1]+(y*tileSize[1])))
               self.blit(tileE, (size[0]-tileSize[0], origin[1]+(y*tileSize[1])))
         self.blit(tileN, (origin[0]+(x*tileSize[0]), 0))
         self.blit(tileS, (origin[0]+(x*tileSize[0]), size[1]-tileSize[1]))

      #draw the corner tiles in the corners
      self.blit(tileNW, (0, 0))
      self.blit(tileNE, (size[0]-tileSize[0], 0))
      self.blit(tileSW, (0, size[1]-tileSize[1]))
      self.blit(tileSE, (size[0]-tileSize[0], size[1]-tileSize[1]))
      

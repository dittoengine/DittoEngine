import os
import xml.etree.ElementTree as ET

import pygame

import settings
import data
import globs
import error

class Font():
   """Class to load fonts and write with them."""
   
   def __init__(self, fn):
      """
      Load the image and cut out the individual characters.

      fn - the font XML file.
      """

      #parse the XML file
      root = data.getTreeRoot(fn)
      path = os.path.join(settings.path, "data", data.getAttr(root, "file", data.D_STRING))
      self.height = data.getAttr(root, "height", data.D_INT)
      transparency = data.getAttr(root, "transparency", data.D_INT3LIST)

      #load the image
      image = data.getImage(path, fn)
      image.set_colorkey(transparency)

      #cut out the tiles and store them in a dictionary
      self.characters = {}
      for c in data.getChildren(root, "character"):
         char = data.getAttr(c, "char", data.D_STRING)
         width = data.getAttr(c, "width", data.D_INT)
         location = data.getAttr(c, "location", data.D_INT2LIST)
         self.characters[char] = image.subsurface(location[0], location[1], width, self.height)

   def writeText(self, text, surface, location):
      """
      Write text to a given surface at a given location

      text - the string to write
      surface - the surface to write onto
      location - the coordinates on the surface to start drawing at
      """

      #interpret the location as two separate variables
      pointerX, pointerY = location

      #for each character, make sure it exists
      #blit it to the current position, then advance the pointer
      for char in text:
         try:
            image = self.characters[char]
         except KeyError:
            raise error.DittoInvalidResourceException("Font file", "Character %s" % char)
         surface.blit(image, (pointerX, pointerY))
         pointerX += image.get_width()

   def calcWidth(self, text):
      """Calculate how wide text would be if written in this font."""

      #return the sum of the widths of the characters
      return sum([self.characters[char].get_width() for char in text])    

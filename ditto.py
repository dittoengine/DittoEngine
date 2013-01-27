import sys, os
import xml.etree.ElementTree as ET

import pygame

import settings
import game
import debug
import error
import error_handling
import globs
import intro
import game_input
import sound
import data

class Ditto():
   """Main entry class to create a Ditto game."""
   
   def setup(self):
      """Initialize pygame, find the main game file and parse it."""

      #initialise pygame
      pygame.init()

      #find the main game file and parse it
      if settings.path is not None:
         fn = os.path.join(settings.path, "data", "game.xml")
      else:
         raise error.DittoInvalidResourceException("settings.py", "path")
      root = data.getTreeRoot(fn, "Ditto Main")
      for p in data.getChildren(root, "property"):
         if data.getAttr(p, "name", data.D_STRING) == "tilesize":
            globs.TILESIZE = data.getAttr(p, "value", data.D_INT2LIST)
         elif data.getAttr(p, "name", data.D_STRING) == "font":
            globs.FONT = data.getAttr(p, "value", data.D_STRING)
         elif data.getAttr(p, "name", data.D_STRING) == "dialog":
            globs.DIALOG = data.getAttr(p, "value", data.D_STRING)
         elif data.getAttr(p, "name", data.D_STRING) == "pokemon":
            globs.POKEMON = data.getAttr(p, "value", data.D_STRING)
         elif data.getAttr(p, "name", data.D_STRING) == "soundeffects":
            soundPath = os.path.join(settings.path, "data", data.getAttr(p, "value", data.D_STRING))
         elif data.getAttr(p, "name", data.D_STRING) == "moves":
            globs.MOVES = os.path.join(settings.path, "data", data.getAttr(p, "value", data.D_STRING))
         elif data.getAttr(p, "name", data.D_STRING) == "behaviours":
            globs.BEHAVIOURS = os.path.join(settings.path, "data", data.getAttr(p, "value", data.D_STRING))

      #if there's an icon specified, use it      
      if len(data.getChildren(root, "icon")) > 0:
         node = data.getChild(root, "icon")
         iconPath = os.path.join(settings.path, "data", data.getAttr(node, "file", data.D_STRING))
         icon = data.getImage(iconPath, fn)
         pygame.display.set_icon(icon)

      #set up the main window
      windowSize = settings.screenSize[0]*globs.TILESIZE[0], settings.screenSize[1]*globs.TILESIZE[1]   
      self.screen = pygame.display.set_mode(windowSize)
      pygame.display.set_caption("%s --- Ditto Engine" % data.getAttr(root, "title", data.D_STRING))

      #create a clock object
      self.clock = pygame.time.Clock()

      #initialise sound
      sound.init(soundPath)

      #set up the initial scene, the intro
      self.activeScene = intro.Intro(self.screen)

   def mainloop(self):
      """Set Ditto's main loop going."""

      #until either we're done, or told to quit keep looping
      done = False
      quitEvent = False
      while not (done or quitEvent):
         #process any events, and give any input to the active scene
         quitEvent = game_input.processEvents()
         self.activeScene.giveInput(game_input.get())

         #tick the active scene
         done = self.activeScene.tick()

         #if the active scene is done, get the next one
         #if there is one, then we're not done yet
         if done:
            self.activeScene = self.activeScene.getNext()
            if self.activeScene is not None:
               done = False

         #draw the frame, and update the display
         self.activeScene.drawFrame()
         pygame.display.flip()
         
         #wait for the next frame
         self.clock.tick(settings.framerate)

   def clearup(self):
      "Exit the game."""

      #quit pygame
      pygame.quit()
         

   def go(self):
      """Run the engine"""

      #try to run
      try:
         self.setup()
         self.mainloop()
         self.clearup()

      #if there's a Ditto exception raised, handle it specially   
      except error.DittoError as e:
         error_handling.handleDittoError(e, self.screen)

      #otherwise process it as a generic exception
      except Exception as e:
         if self.__dict__.has_key("screen"):
            error_handling.handleError(e, self.screen)
         else:
            error_handling.handleError(e)

#if we're being used as the entry point, create a Ditto object and run it
if __name__ == "__main__":
   d = Ditto()
   d.go()

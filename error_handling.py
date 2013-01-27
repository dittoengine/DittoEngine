import sys, traceback
import os

import pygame

import font
import globs
import settings

def handleError(e, screen=None):
   """Deal with a coding error."""

   #if the screen has been created, fill it blue
   if screen is not None:
      screen.fill((0,0,255))
      pygame.display.flip()

   #print out what went wrong   
   print "Python exception generated!"
   print "-"*20
   traceback.print_exc(file=sys.stdout)
   print "-"*20
   raw_input()

def handleDittoError(e, screen):
   """Deal with a problem with the files supplied to Ditto"""

   #fill the screen white
   screen.fill((255,255,255))
   pygame.display.flip()

   #try to use the game font to write the problem on the screen
   try:
      f = font.Font(os.path.join(settings.path, "data", globs.FONT))
      lines = e.describe()
      
      i = 0
      for line in lines:
         f.writeText(line, screen, (10, 10+(i*(f.height+2))))
         i += 1

      pygame.display.flip()
      raw_input()

   #if that doesn't work, just print out to the console      
   except:
      print "Ditto ran into a problem!"
      print "-"*20
      lines = e.describe()
      for line in lines:
         print line
      print "-"*20
      raw_input("Press enter to exit")

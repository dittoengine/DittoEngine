import os
import xml.etree.ElementTree as ET

import pygame

import scene
import debug
import game
import settings
import dialog
import font
import globs
import box
import sound
import game_input

#!!!!!!!!!!!!
#TODO
#currently only supports one save file
#will show more, but always opens the last one
#also doesn't get data preview from save file, as a lot of that data doesn't exist yet

#define formatting constants
OBJECTBUFFER = 5
BORDER = 10
LINEBUFFER = 5

class GameSelect(scene.Scene):
   """Class representing the game select screen."""
   
   def __init__(self, screen):
      """
      Create the continue and new game boxes, and a shadow to darken non-selected boxes.

      screen - the screen to draw to.
      """

      #store the screen for blitting to later
      self.screen = screen

      #create the font
      fFont = font.Font(os.path.join(settings.path, "data", globs.FONT))

      #initialise list of boxes
      self.boxes = []

      #get a list of save files
      #if any exist, get info from them and create a box for them
      savefiles = os.listdir(os.path.join(settings.path, "saves")) #get list of save files
      if savefiles:
         info = {"PLAYER": "BOB",
                 "TIME": "06:01",
                 "POKEDEX": "42",
                 "BADGES": "1"}
         order = ["PLAYER", "TIME", "POKEDEX", "BADGES"]
         continueBox = Infobox(self.screen, fFont, "CONTINUE", info, order)
         self.savegame = os.path.join(settings.path, "saves", savefiles[0])
         self.boxes.append(continueBox)

      #create the box for a new game   
      newgameBox = Infobox(self.screen, fFont, "NEW GAME")
      self.boxes.append(newgameBox)

      #create the shadow used to darken non-selected boxes
      self.shadow = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
      self.shadow.fill((10,10,10))
      self.shadow.set_alpha(100)

      #start with the topmost box selected
      self.current = 0

   def giveInput(self, inputData):
      """
      Recieve input and store it to be processed by tick().

      inputData - the input 3-tuple.
      """

      #only interested in keydowns
      self.keysJustPressed = inputData[1]

   def drawFrame(self):
      """Draw a frame to the screen."""

      #fill with a background colour
      self.screen.fill((0,0,50))

      #blit each box in turn down the screen
      #miss out the selected box to be drawn after the shadow
      pointerY = OBJECTBUFFER
      for i in range(0, len(self.boxes)):
         if i != self.current:
            location = (self.screen.get_width()-self.boxes[i].width)/2, pointerY
            self.screen.blit(self.boxes[i].box, location)
         else:
            locationY = pointerY
         pointerY += self.boxes[i].height + OBJECTBUFFER

      #draw in the shadow to darken non-selected boxes   
      self.screen.blit(self.shadow, (0,0))

      #draw in the selected box finally
      location = (self.screen.get_width()-self.boxes[i].width)/2, locationY
      self.screen.blit(self.boxes[self.current].box, location)

   def tick(self):
      """Update the screen one tick - ie process input."""

      #use input to update the screen
      for key in self.keysJustPressed:
         
         #if it's we've selected the current option, return True to say we're done
         if key == game_input.BT_A:
            sound.playEffect(sound.SD_SELECT)
            return True

         #if we've moved up or down, make sure it's possible and then update
         elif key == game_input.BT_UP:
            if self.current > 0:
               self.current -= 1
               sound.playEffect(sound.SD_CHOOSE)
         elif key == game_input.BT_DOWN:
            if self.current < len(self.boxes)-1:
               self.current += 1
               sound.playEffect(sound.SD_CHOOSE)

      #we've not done yet
      return False

   def getNext(self):
      """Get the next game scene"""

      #if we've selected a new game, then no save file
      #otherwise, use the save file
      #NOTE if there's more than one save file this doesn't work correctly yet
      if self.current == len(self.boxes)-1:
         save = None
      else:
         save = self.savegame
      
      #if we're in debug mode, create a debug game
      #else create a normal game
      if settings.DEBUG:
         return debug.debugGame(self.screen, save)
      else:
         return game.Game(self.screen, save)

class Infobox():
   """Class used to show information on the game select screen."""
   
   def __init__(self, screen, fFont, title=None, info={}, order=[]):
      """
      Create the box and get it ready.

      screen - the screen to draw to.
      fFont - the font to use.
      title - the title at the top of the box.
      info - dictionary of {parameter: value} pairs to display.
      order - the order in which to display the pairs.
      """

      #determine the size of the box
      #work out how many lines of text there will be, and use that to determine height
      #width is half the screen size
      numLines = len(info)
      if title is not None:
         numLines += 1
      self.height = ((fFont.height+LINEBUFFER)*numLines)-LINEBUFFER+(BORDER*2)

      self.width = screen.get_width()/2

      #create the box
      self.box = box.Box((self.width, self.height)).convert(screen)

      #track line numbers as we write text onto the box
      #if there's a title, indent it a bit as we write it
      i = 0
      if title is not None:
         location = BORDER*3, BORDER
         fFont.writeText(title, self.box, location)
         i += 1

      #for each parameter, work out where it needs to go
      #write the parameter on the left, and its value halfway across
      for param in order:
         location = BORDER, (i*(fFont.height+LINEBUFFER))+BORDER
         fFont.writeText(param, self.box, location)
         location = self.width/2, (i*(fFont.height+LINEBUFFER))+BORDER
         fFont.writeText(info[param], self.box, location)
         i += 1

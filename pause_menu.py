import foreground_object
import box
import globs
import font
import settings
import os
import pygame
import party_screen
import game_input
import xml.etree.ElementTree as ET
import data

class PauseMenu(foreground_object.ForegroundObject):
   def __init__(self, screen, game, fn):      
      self.screen = screen
      self.game = game
      self.font = font.Font(os.path.join(settings.path, "data", globs.FONT)) #create the font

      self.menuNode = data.getTreeRoot(fn)

      self.foregroundObject = None

      self.objectBuffer = 2
      self.border = 10
      self.lineBuffer = 3

      self.choices = ["POKEDEX", "POKEMON", "BAG", "OPTIONS", "SAVE", "EXIT"]

      self.current = 0

      fn = os.path.join(settings.path, "data", globs.DIALOG)
      root = ET.parse(fn).getroot()
      self.transparency = map(int, root.attrib["transparency"].split(","))
      self.sideCursor = pygame.image.load(os.path.join(settings.path, "data", root.attrib["sidecursor"])).convert(self.screen) ##load the side cursor image, and convert
      self.sideCursor.set_colorkey(self.transparency) ##set the transparency

      width = max(map(self.font.calcWidth, self.choices)) + self.border*2 + self.sideCursor.get_width()
      self.size = (width, (self.border*2)+(self.font.height*len(self.choices))+(self.lineBuffer*(len(self.choices)-1)))
      self.location = (self.screen.get_width()-self.size[0]-self.objectBuffer, self.objectBuffer)

      self.box = box.Box(self.size)

      i = 0
      for choice in self.choices:
         location = self.border+self.sideCursor.get_width(), (i*(self.font.height+self.lineBuffer))+self.border
         self.font.writeText(choice, self.box, location)
         i += 1
      
      self.busy = True

   def inputButton(self, button):
      if self.foregroundObject is None:
         if button == game_input.BT_A:
            self.choose(self.choices[self.current])
         elif button == game_input.BT_B:
            self.busy = False
         elif button == game_input.BT_UP:
            if self.current > 0:
               self.current -= 1
         elif button == game_input.BT_DOWN:
            if self.current < len(self.choices)-1:
               self.current += 1
      else:
         self.foregroundObject.inputButton(button)

   def draw(self):
      if self.foregroundObject is None:
         self.screen.blit(self.box, self.location)
         self.screen.blit(self.sideCursor, (self.location[0]+self.border, self.location[1]+self.border+(self.current*(self.font.height+self.lineBuffer))))
      else:
         self.foregroundObject.draw()

   def tick(self):
      if self.foregroundObject is not None:
         self.foregroundObject.tick()
         if not self.foregroundObject.busy:
            self.foregroundObject = None

   def choose(self, choice):
      if choice == "POKEMON":
         node = data.getChild(self.menuNode, "party")
         self.foregroundObject = party_screen.PartyScreen(self.screen, node, self.game.player.party)
      elif choice == "EXIT":
         self.busy = False
      else:
         print choice

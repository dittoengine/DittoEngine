import foreground_object
import box
import globs
import os
import settings
import xml.etree.ElementTree as ET
import pygame
import font
import pokemon
import game_input
import pokemon_screen
import data

class PartyScreen(foreground_object.ForegroundObject):
   def __init__(self, screen, partyNode, party):
      self.screen = screen
      self.partyNode = partyNode
      self.font = font.Font(os.path.join(settings.path, "data", data.getAttr(partyNode, "font", data.D_STRING)))
      self.party = party

      self.foregroundObject = None

      fn = os.path.join(settings.path, "data", data.getAttr(partyNode, "hpbar", data.D_STRING))
      hpBar = pygame.image.load(fn).convert(self.screen)
      hpBar.set_colorkey(data.getAttr(partyNode, "transparency", data.D_INT3LIST))

      self.border = 5
      self.lineBuffer = 2

      self.shadow = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
      self.shadow.fill((10,10,10))
      self.shadow.set_alpha(100)

      self.boxes = []
      self.current = 0

      main = MainBox(self.screen, partyNode, self.font, hpBar, (self.border, self.border+25), self.party[0])
      self.boxes.append(main)

      pointerX = (self.border*2)+main.box.get_width()
      pointerY = self.border
      for i in range(1, len(self.party)):
         b = SideBox(self.screen, partyNode, self.font, hpBar, (pointerX,pointerY), self.party[i])
         self.boxes.append(b)
         pointerY += b.box.get_height()+self.border

      for i in range(len(self.party), 6):
         b = EmptyBox(self.screen, partyNode, (pointerX,pointerY))
         self.boxes.append(b)
         pointerY += b.box.get_height()+self.border

      self.busy = True

   def inputButton(self, button):
      if self.foregroundObject is None:
         if button == game_input.BT_A:
            self.foregroundObject = pokemon_screen.PokemonScreen(self.screen, data.getChild(self.partyNode, "pokemon"), self.party, self.current)
         elif button == game_input.BT_B:
            self.busy = False
         elif button == game_input.BT_UP:
            if self.current > 1:
               self.current -= 1
         elif button == game_input.BT_DOWN:
            if self.current < len(self.party)-1:
               self.current += 1
         elif button == game_input.BT_LEFT:
            self.current = 0
         elif button == game_input.BT_RIGHT:
            if self.current == 0:
               self.current = 1
      else:
         self.foregroundObject.inputButton(button)

   def draw(self):
      self.screen.fill((30,200,255))

      for i in range(0, len(self.boxes)):
         if i != self.current:
            self.boxes[i].draw()

      self.screen.blit(self.shadow, (0,0))

      self.boxes[self.current].draw()

      if self.foregroundObject is not None:
         self.foregroundObject.draw()

   def tick(self):
      if self.foregroundObject is not None:
         self.foregroundObject.tick()
         if not self.foregroundObject.busy:
            self.foregroundObject = None

class PartyBox():
   def __init__(self, screen, partyNode, font, location, poke):
      self.screen = screen
      self.font = font
      self.location = location
      self.poke = poke

      self.speciesNode = poke.speciesNode

      graphicsNode = data.getChild(self.speciesNode, "graphics")
      iconNode = data.getChild(graphicsNode, "icon")
      fn = os.path.join(settings.path, "data", data.getAttr(iconNode, "file", data.D_STRING))
      image = data.getImage(fn, iconNode.ditto_fn)
      self.iconSize = data.getAttr(iconNode, "size", data.D_INT2LIST)
      self.icon = image.subsurface((0,0), self.iconSize)
      self.icon.set_colorkey(data.getAttr(iconNode, "transparency", data.D_INT3LIST))

   def draw(self):
      self.screen.blit(self.box, self.location)

class EmptyBox():
   def __init__(self, screen, partyNode, location):
      self.screen = screen
      self.location = location

      emptyNode = data.getChild(partyNode, "empty")
      fn = os.path.join(settings.path, "data", data.getAttr(emptyNode, "file", data.D_STRING))
      self.box = pygame.image.load(fn).convert(self.screen)
      self.box.set_colorkey(data.getAttr(partyNode, "transparency", data.D_INT3LIST))
      
   def draw(self):
      self.screen.blit(self.box, self.location)

class MainBox(PartyBox):
   def __init__(self, screen, partyNode, font, hpBar, location, poke):
      PartyBox.__init__(self, screen, partyNode, font, location, poke)

      self.border = 3
      self.lineBuffer = 0

      mainNode = data.getChild(partyNode, "main")
      fn = os.path.join(settings.path, "data", data.getAttr(mainNode, "file", data.D_STRING))
      self.box = pygame.image.load(fn).convert(self.screen)
      self.box.set_colorkey(data.getAttr(partyNode, "transparency", data.D_INT3LIST))
      
      self.box.blit(hpBar, (self.box.get_width()-hpBar.get_width()-self.border, self.border+(self.font.height+self.lineBuffer)*2))
      self.font.writeText(poke.getName(), self.box, (self.iconSize[0]+self.border, self.border))
      self.font.writeText("Lv%s" % poke.level, self.box, (self.iconSize[0]+self.border, self.border+self.font.height+self.lineBuffer))
      text = "%s/%s" % (poke.currentHP, poke.stats[pokemon.ST_HP])
      self.font.writeText(text, self.box, (self.box.get_width()-self.font.calcWidth(text)-self.border, self.border+(self.font.height+self.lineBuffer)*2+hpBar.get_height()))

   def draw(self):
      PartyBox.draw(self)
      
      self.screen.blit(self.icon, (self.location[0], self.location[1]))

class SideBox(PartyBox):
   def __init__(self, screen, partyNode, font, hpBar, location, poke):
      PartyBox.__init__(self, screen, partyNode, font, location, poke)

      self.border = 3
      self.lineBuffer = 0

      sideNode = data.getChild(partyNode, "side")
      fn = os.path.join(settings.path, "data", data.getAttr(sideNode, "file", data.D_STRING))
      self.box = pygame.image.load(fn).convert(self.screen)
      self.box.set_colorkey(data.getAttr(partyNode, "transparency", data.D_INT3LIST))

      self.box.blit(hpBar, (self.box.get_width()-hpBar.get_width()-self.border, self.border))
      self.font.writeText(poke.getName(), self.box, (self.iconSize[0]+self.border, self.border))
      self.font.writeText("Lv%s" % poke.level, self.box, (self.iconSize[0]+self.border, self.border+self.font.height+self.lineBuffer))
      text = "%s/%s" % (poke.currentHP, poke.stats[pokemon.ST_HP])
      self.font.writeText(text, self.box, (self.box.get_width()-self.font.calcWidth(text)-self.border, self.border+hpBar.get_height()))

   def draw(self):
      PartyBox.draw(self)

      self.screen.blit(self.icon, self.location)
      

import os

import pygame

import foreground_object
import settings
import font
import box
import pokemon
import game_input
import data

#define formatting constants
OBJECTBUFFER = 5
BORDER = 10
LINEBUFFER = 2

class PokemonScreen(foreground_object.ForegroundObject):
   """The pokemon summary screen object."""
   
   def __init__(self, screen, pokemonMenuNode, party, startPoke):
      """
      Create the summary screen, starting on the info page of the requested pokemon.

      screen - the surface to blit to.
      pokemonMenuNode - the <pokemon> menu node.
      party - the party to summarize.
      currentPoke - the index of the pokemon to show first.
      """

      #store variables for later
      self.screen = screen
      self.menuNode = pokemonMenuNode
      self.party = party

      #set what to show first - the summary page of the requested pokemon
      self.currentPoke = startPoke
      self.currentPage = 0

      #load the pokemon and then the page
      #based off the currentPoke and currentPage attributes
      self.loadPokemon()
      self.loadPage()

      #we're busy
      self.busy = True

   def loadPokemon(self):
      """
      Load the pokemon, and create the main pokemon box common to all pages.

      Uses the currentPoke attribute to search party for correct pokemon.
      """

      #get the required pokemon
      self.poke = self.party[self.currentPoke]
      speciesNode = self.poke.speciesNode

      #get the <main> child of the <pokemon> node
      mainNode = data.getChild(self.menuNode, "main")

      #create the font
      fFont = font.Font(os.path.join(settings.path, "data", data.getAttr(mainNode, "font", data.D_STRING)))

      #create the main box, which will cover the top left quarter of the screen
      size = ((self.screen.get_width()/2)-(OBJECTBUFFER*2), (self.screen.get_height()/2)-(OBJECTBUFFER*2))
      fn = os.path.join(settings.path, "data", data.getAttr(mainNode, "box", data.D_STRING))
      self.mainBox = box.Box(size, fn).convert(self.screen)

      #write the pokemon level and name, then draw the pokemon
      fFont.writeText("Lv%i" % self.poke.level, self.mainBox, (BORDER, BORDER)) #top left
      fFont.writeText(self.poke.getName(), self.mainBox, ((size[0]-fFont.calcWidth(self.poke.getName()))/2, BORDER)) #top centre
      self.battler = self.poke.getBattler()
      self.mainBox.blit(self.battler, ((size[0]-self.battler.get_width())/2, size[1]-self.battler.get_height()-BORDER)) #bottom centre

   def loadPage(self):
      """
      Load a new page.

      Based off the currentPage attribute.
      """

      #depending on currentPage, create the required page 
      if self.currentPage == 0:
         self.page = InfoPage(self.screen, data.getChild(self.menuNode, "info"), self.poke)
      elif self.currentPage == 1:
         self.page = SkillsPage(self.screen, data.getChild(self.menuNode, "skills"), self.poke)
      elif self.currentPage == 2:
         self.page = MovesPage(self.screen, data.getChild(self.menuNode, "moves"), self.poke)

   def inputButton(self, button):
      """
      Process a button press.

      button - the button that was pressed.
      """

      #if it's the B button, we're done
      if button == game_input.BT_B:
         self.busy = False

      #left or right should change pages
      elif button == game_input.BT_LEFT:
         if self.currentPage > 0:
            self.currentPage -= 1
            self.loadPage()
      elif button == game_input.BT_RIGHT:
         if self.currentPage < 2:
            self.currentPage += 1
            self.loadPage()

      #up and down should change pokemon (and therefore reload pages)
      elif button == game_input.BT_UP:
         if self.currentPoke > 0:
            self.currentPoke -= 1
            self.loadPokemon()
            self.loadPage()
      elif button == game_input.BT_DOWN:
         if self.currentPoke < len(self.party)-1:
            self.currentPoke += 1
            self.loadPokemon()
            self.loadPage()
            

   def draw(self):
      """Draw to the screen."""

      #fill with a background colour
      self.screen.fill((255,200,150))

      #draw the current page
      self.page.draw()

      #draw the main box
      self.screen.blit(self.mainBox, (OBJECTBUFFER,OBJECTBUFFER))

class InfoPage(foreground_object.ForegroundObject):
   """The info page of the pokemon screen."""

   def __init__(self, screen, infoNode, poke):
      """
      aa

      screen - the screen to blit to.
      infoNode - the <info> node from the menu XML file.
      poke - the pokemon.
      """

      self.screen = screen

      fFont = font.Font(os.path.join(settings.path, "data", data.getAttr(infoNode, "font", data.D_STRING)))

      size = ((self.screen.get_width()/2)-(OBJECTBUFFER*2), (self.screen.get_height()/2)-(OBJECTBUFFER*2))
      fn = os.path.join(settings.path, "data", data.getAttr(infoNode, "box", data.D_STRING))
      self.infoBox = box.Box(size, fn).convert(self.screen)

      info = {"No.": data.getAttr(poke.speciesNode, "dex", data.D_STRING),
              "Name": poke.getName(),
              "Type": "TODO",
              "OT": str(poke.trainer),
              "ID No.": str(poke.trainerID),
              "Item": str(poke.heldItem)}
      order = ["No.", "Name", "Type", "OT", "ID No.", "Item"]

      pointerY = BORDER
      for inf in order:
         fFont.writeText(inf, self.infoBox, (BORDER, pointerY))
         text = info[inf]
         fFont.writeText(text, self.infoBox, (size[0]-fFont.calcWidth(text)-BORDER, pointerY))
         pointerY += fFont.height+LINEBUFFER

      self.infoBoxLocation = (self.screen.get_width()-size[0]-OBJECTBUFFER, OBJECTBUFFER)

      size = (self.screen.get_width()-(OBJECTBUFFER*2), (self.screen.get_height()/2)-(OBJECTBUFFER*2))
      self.memoBox = box.Box(size, fn).convert(self.screen)

      pointerY = BORDER
      fFont.writeText("%s nature." % "TODO", self.memoBox, (BORDER, pointerY))
      pointerY += fFont.height+LINEBUFFER
      fFont.writeText("Met in %s." % "TODO", self.memoBox, (BORDER, pointerY))

      self.memoBoxLocation = (OBJECTBUFFER, self.screen.get_height()-size[1]-OBJECTBUFFER)

   def draw(self):
      """Draw to the screen."""
      
      self.screen.blit(self.infoBox, self.infoBoxLocation)
      self.screen.blit(self.memoBox, self.memoBoxLocation)


class SkillsPage(foreground_object.ForegroundObject):
   """The stats page of the pokemon screen."""
   
   def __init__(self, screen, skillsNode, poke):
      """
      aa

      screen - the screen to blit to.
      statsNode - the <stats> node from the menu XML file.
      poke - the pokemon.
      """

      self.screen = screen

      fFont = font.Font(os.path.join(settings.path, "data", data.getAttr(skillsNode, "font", data.D_STRING)))

      size = ((self.screen.get_width()/2)-(OBJECTBUFFER*2), (self.screen.get_height()/2)-(OBJECTBUFFER*2))
      fn = os.path.join(settings.path, "data", data.getAttr(skillsNode, "box", data.D_STRING))
      self.statsBox = box.Box(size, fn).convert(self.screen)

      stats = {"HP": pokemon.ST_HP,
               "Attack": pokemon.ST_ATTACK,
               "Defense": pokemon.ST_DEFENSE,
               "Sp Attack": pokemon.ST_SPATTACK,
               "Sp Defense": pokemon.ST_SPDEFENSE,
               "Speed": pokemon.ST_SPEED}
      order = ["HP", "Attack", "Defense", "Sp Attack", "Sp Defense", "Speed"]
      
      pointerY = BORDER
      for stat in order:
         fFont.writeText(stat, self.statsBox, (BORDER, pointerY))
         text = str(poke.stats[stats[stat]])
         fFont.writeText(text, self.statsBox, (size[0]-fFont.calcWidth(text)-BORDER, pointerY))
         pointerY += fFont.height+LINEBUFFER
      
      self.statsBoxLocation = (self.screen.get_width()-size[0]-OBJECTBUFFER, OBJECTBUFFER)

   def draw(self):
      """Draw to the screen."""

      self.screen.blit(self.statsBox, self.statsBoxLocation)

class MovesPage(foreground_object.ForegroundObject):
   def __init__(self, screen, movesNode, poke):
      self.screen = screen

      fFont = font.Font(os.path.join(settings.path, "data", data.getAttr(movesNode, "font", data.D_STRING)))

      size = ((self.screen.get_width()/2)-(OBJECTBUFFER*2), (fFont.height+BORDER)*2)
      fn = os.path.join(settings.path, "data", data.getAttr(movesNode, "box", data.D_STRING))

      moves = poke.moves
      self.moveBoxes = []
      for move in moves:
         if move is not None:
            b = box.Box(size, fn).convert(self.screen)
            fFont.writeText(move.name, b, (BORDER, BORDER))
            text = "PP %i/%i" % (move.currPP, move.maxPP)
            fFont.writeText(text, b, (size[0]-fFont.calcWidth(text)-BORDER, BORDER+fFont.height))

            self.moveBoxes.append(b)

   def draw(self):
      pointerY = BORDER

      for b in self.moveBoxes:
         self.screen.blit(b, (self.screen.get_width()-b.get_width()-OBJECTBUFFER, pointerY))
         pointerY += b.get_height()+OBJECTBUFFER




      

import os
import xml.etree.ElementTree as ET

import pygame

import settings
import game_select
import scene
import sound
import game_input
import data

class Intro(scene.Scene):
   """The main intro scene."""
   
   def __init__(self, screen):
      """
      Load all intro screens and start the first.

      screen - the screen to blit to.
      """

      #store screen for use later
      self.screen = screen

      #parse the intro XML file
      fn = os.path.join(settings.path, "data", "intro.xml")
      root = data.getTreeRoot(fn, "Ditto main")

      #create each intro screen
      self.introScreens = []
      for s in data.getChildren(root, "screen"):
         self.introScreens.append(IntroScreen(screen, s))

      #set the first screen active
      self.current = 0
      self.activeScreen = self.introScreens[self.current]
      self.activeScreen.onShow()

   def giveInput(self, inputData):
      """
      Recieve input data.

      inputData - the input data 3-tuple.
      """

      #we're only bothered about keydowns
      self.keysJustPressed = inputData[1]

   def drawFrame(self):
      """Draw a frame to the screen."""

      #call on the active screen to draw itself
      self.activeScreen.drawFrame()

   def tick(self):
      """Update the intro one frame."""

      #tick the active screen, find out whethe it's done
      done = self.activeScreen.tick()

      #if button A has been pressed, the current screen is done
      for key in self.keysJustPressed:
         if key == game_input.BT_A:
            done = True

      #if the current screen is done, move on to the next
      #if there are no more, return True to say we're done
      #otherwise load the next one
      if done:
         self.current += 1
         if self.current >= len(self.introScreens):
            return True
         else:
            self.activeScreen = self.introScreens[self.current]
            self.activeScreen.onShow()

      #we're still going
      return False

   def getNext(self):
      """Get the next game scene."""

      #return the game select scene
      return game_select.GameSelect(self.screen)

class IntroScreen():
   """A single intro screen."""
   
   def __init__(self, screen, node):
      """
      Set up the screen - load any images and play any music.

      screen - the screen to blit to.
      node - the <screen> node.
      """

      #store the screen for later
      self.screen = screen

      #set up the timer
      #time of -1 means no time limit
      self.time = data.getAttr(node, "time", data.D_INT)
      self.count = 0
      self.trackTime = (self.time != -1)
      
      #find out the background color
      #use american spelling of color by convention
      self.bgColor = data.getAttr(node, "bgcolor", data.D_INT3LIST)

      #find the music to play if any
      self.music = None
      for track in data.getChildren(node, "music"):
         self.music = os.path.join(settings.path, "data", data.getAttr(track, "file", data.D_STRING))

      #load all images
      self.images = []
      for image in data.getChildren(node, "image"):
         self.images.append(IntroImage(self.screen, image))

   def onShow(self):
      """Called when the screen is actually shown for the first time."""

      #if there is any music to play, play it                             
      if self.music is not None:
         sound.playMusic(self.music)

   def drawFrame(self):
      """Draw a frame to the screen."""

      #fill the screen with the background color                           
      self.screen.fill(self.bgColor)

      #draw all images
      for image in self.images:
         image.draw()

   def tick(self):
      """Advance the screen one frame."""

      #if we're keeping time, increase the count                             
      if self.trackTime:
         self.count += 1

      #if we've reached the end of our time, return True to indicate we've finished.
      #else return False
      if (self.count >= self.time) and self.trackTime:
         return True
      else:
         return False

class IntroImage():
   """Class to represent a single image shown on an intro screen."""
                                   
   def __init__(self, screen, node):
      """Load the image and determine it's position."""

      #store screen for later
      self.screen = screen

      #open the image
      fn = os.path.join(settings.path, "data", data.getAttr(node, "file", data.D_STRING))
      self.image = data.getImage(fn, "Intro file.").convert(self.screen)
      transparency = data.getAttr(node, "transparency", data.D_INT3LIST)
      self.image.set_colorkey(transparency)

      #calculate where the centres are for the screen and the image
      screenCentre = self.screen.get_width()/2, self.screen.get_height()/2
      imageCentre = self.image.get_width()/2, self.image.get_height()/2

      #find out the location of the image
      location = data.getAttr(node, "location", data.D_INT2LIST)

      #calculate its position on the screen
      #location (0,0) should be dead centre, (-100, 100) bottom left
      self.position = ((screenCentre[0]-imageCentre[0])+((location[0]*screenCentre[0])/100),
                       (screenCentre[1]-imageCentre[1])+((location[1]*screenCentre[1])/100))
      

   def draw(self):
      """Draw a frame to the screen."""

      #draw the image in the required place
      self.screen.blit(self.image, self.position)
      

import xml.etree.ElementTree as ET
import os
import pickle

import pygame

import tilemap
import camera
import game_input
import settings
import globs
import player
import save
import sound
import scene
import pause_menu
import data
import sprite
import script_engine

class Game(scene.Scene):
   """Class to manage the main game world."""
   
   def __init__(self, screen, savegame=None):
      """
      Open the save file (or make a new one) and create camera and script engine.

      screen - the screen to render to.
      sound - the sound manager.
      savegame - path to the save file to open, or None to start a new game.
      """

      #store variables for use later
      self.screen = screen

      #parse the game XML file
      fn = os.path.join(settings.path, "data", "game.xml")
      root = data.getTreeRoot(fn, "Ditto main")
      for p in data.getChildren(root, "property"):
         if data.getAttr(p, "name", data.D_STRING) == "menu":
            self.menuPath = data.getAttr(p, "value", data.D_STRING)

      #create script engine and initialise variables
      self.scriptEngine = script_engine.ScriptEngine()
      self.scriptEngine.setup(self)
      self.paused = False
      self.foregroundObject = None

      #if there's a save, open it
      #else start a new game
      if savegame is not None:
         self.openSave(savegame, root)
      else:
         self.newGame(os.path.join(settings.path, "saves", "ditto.sav"), root)

      #put the player onto the map and play music
      self.map.sprites["PLAYER"] = self.player
      sound.playMusic(self.player.map.music)

      #create a camera and attach to the player
      self.camera = camera.Camera(screen)
      self.camera.attachTo(self.player)

   def giveInput(self, inputData):
      """
      Take the input data from the input manager and store it.

      inputData - a 3-tuple of the keys currently down, the keys just pressed and the keys just released.
      """

      #store each list separately
      self.keysDown = inputData[0]
      self.keysJustPressed = inputData[1]
      self.keysJustReleased = inputData[2]

   def tick(self):
      """Advance the game one tick"""

      #if there's no active object, use input to update the main game world
      if self.foregroundObject is None:
         for key in self.keysJustPressed:
            if key == game_input.BT_SAVE:
               self.writeSave()
               sound.playEffect(sound.SD_SAVE)
            elif key == game_input.BT_A:
               self.player.investigate()
            elif key == game_input.BT_B:
               self.player.speed = 2
            elif key == game_input.BT_START:
               self.paused = not self.paused
               self.foregroundObject = pause_menu.PauseMenu(self.screen, self, os.path.join(settings.path, "data", self.menuPath))
            elif key == game_input.BT_DEBUG:
               pass
               
         for key in self.keysJustReleased:
            if key == game_input.BT_B:
               self.player.speed = 1

         for key in self.keysDown:
            if key == game_input.BT_UP:
               self.player.walk(sprite.DIR_UP)
            elif key == game_input.BT_DOWN:
               self.player.walk(sprite.DIR_DOWN)
            elif key == game_input.BT_LEFT:
               self.player.walk(sprite.DIR_LEFT)
            elif key == game_input.BT_RIGHT:
               self.player.walk(sprite.DIR_RIGHT)

      #if there is an active object, feed keydowns to it
      #tick it and check whether it's finished or not
      else:
         for key in self.keysJustPressed:
            self.foregroundObject.inputButton(key)

         self.foregroundObject.tick()
         if not self.foregroundObject.busy:
            self.foregroundObject = None
            self.paused = False

      #if we're not paused, tick the script engine and map      
      if not self.paused:
         self.scriptEngine.tick()
         self.player.map.tick()

      #we've not been told to exit, so not done yet   
      done = False
      return done

   def drawFrame(self):
      """Draw a frame to the screen."""

      #tell the camera to draw a frame
      #then if there is a foreground object get that drawn on top
      self.camera.drawFrame()
      if self.foregroundObject is not None:
         self.foregroundObject.draw()

   def openSave(self, fn, root):
      """
      Open a save file.

      fn - the path to the save file.
      root - the root <game> node.
      """

      #open the file for reading, load the save game, and close
      try:
         f = open(fn, "r")
         self.savegame = pickle.load(f)
         f.close()
      except pickle.PickleError:
         raise error.DittoInvalidResourceException("Ditto main", fn)
      except IOError:
         raise error.DittoIOException("Ditto main", fn)

      #create the current map and load its connections
      self.map = tilemap.Tilemap(self.savegame.currentMap)
      self.map.loadConnections()

      #create the player
      playerNode = data.getChild(root, "player")
      self.player = player.Player(playerNode, self.map, self.savegame.currentPosition, self.savegame.currentLevel)
      self.player.direction = self.savegame.currentDirection
      self.player.party = self.savegame.party

   def writeSave(self):
      """Write the save file."""

      #store required data in savegame
      self.savegame.currentMap = self.player.map.fn
      self.savegame.currentPosition = self.player.position
      self.savegame.currentLevel = self.player.level
      self.savegame.currentDirection = self.player.direction
      self.savegame.party = self.player.party

      #open the file for writing, dump the save game, and close
      try:
         f = open(self.savegame.fn, "w")
         pickle.dump(self.savegame, f)
         f.close()
      except IOError:
         raise error.DittoIOException("Ditto main", fn)

      print "Game saved to " + self.savegame.fn

   def newGame(self, fn, root):
      """Start a new game"""

      #create the new save file
      self.savegame = save.Save(fn)

      #get the new game node from the game xml file
      newgameNode = data.getChild(root, "newgame")

      #create the map, loading connections since it's the active one
      self.map = tilemap.Tilemap(os.path.join(settings.path, "data", data.getAttr(newgameNode, "map", data.D_STRING)))
      self.map.loadConnections()

      #create the player
      playerNode = data.getChild(root, "player")
      self.player = player.Player(playerNode,
                                  self.map,
                                  data.getAttr(newgameNode, "position", data.D_INT2LIST),
                                  data.getAttr(newgameNode, "level", data.D_INT))

      #if there's a new game script, run it
      script = data.getOptionalChild(newgameNode, "script")
      if script is not None:
         s = script_engine.Script(script)
         self.scriptEngine.run(s)
      

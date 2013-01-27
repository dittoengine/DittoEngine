import threading
import os
import xml.etree.ElementTree as ET

import pygame

import settings
import globs
import data

#initialise constants
SD_SAVE = 0
SD_BUMP = 1
SD_SELECT = 2
SD_CHOOSE = 3

#define the names used to refer to sound effects in the XML file
SOUNDEFFECTS = {"SAVE": SD_SAVE,
                "BUMP": SD_BUMP,
                "SELECT": SD_SELECT,
                "CHOOSE": SD_CHOOSE}

#initialise dictionary for mapping effects to sound files
effects = {}

#initialise dictionary to hold playing effects
currentEffects = {}

def init(fn):
   """
   Initialise the pygame mixer and parse XML file for sound effect locations.

   fn - the path to the XML file.
   """

   #initialise the pygame mixer
   pygame.mixer.init()

   #parse the XML file
   root = data.getTreeRoot(fn)
   for effect in data.getChildren(root, "soundeffect"):
      e = SOUNDEFFECTS[data.getAttr(effect, "name", data.D_STRING)]
      effects[e] = os.path.join(settings.path, "data", data.getAttr(effect, "file", data.D_STRING))

def playMusic(fn):
   """
   Play a music track.

   fn - the path to the track.
   """

   #if music is enabled, start a thread to play the music
   #music loading is slow, but not needed instantly so threading is a good idea
   #especially as it usually happens at processing bottleneck frames like map transfers
   if settings.music:
      t = threading.Thread(target=threadPlayMusic, args=(fn,))
      t.start()

def threadPlayMusic(fn):
   """
   Function to be called by playMusic, to run in a separate thread.

   fn - path to the music file to load.
   """

   #load the music and play it on loop
   pygame.mixer.music.load(fn)
   pygame.mixer.music.play(-1)

def playEffect(effect):
   """
   Play a sound effect.

   Checks to see whether the effect is currently playing, and won't play again if so.

   effect - the effect to play.
   """

   #if sound effects are enabled, then start doing stuff
   if settings.soundEffects:

      #make a list of keys for effects that have finished playing and delete them
      keys = [k for k in currentEffects if not currentEffects[k].get_busy()]
      for key in keys:
         del(currentEffects[key])

      #if the requested effect is not already playing, play it   
      if effect not in currentEffects:
         channel = pygame.mixer.Sound(effects[effect]).play()
         currentEffects[effect] = channel



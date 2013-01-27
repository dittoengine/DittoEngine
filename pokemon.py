import globs
import random
import settings
import xml.etree.ElementTree as ET
import os
import pygame
import data
import moves

#define constants
ST_HP = 0
ST_ATTACK = 1
ST_DEFENSE = 2
ST_SPEED = 3
ST_SPATTACK = 4
ST_SPDEFENSE = 5

G_MALE = 0
G_FEMALE = 1
G_NONE = 2

class Pokemon():
   def __init__(self, species, level):
      self.species = species

      fn = os.path.join(settings.path, "data", globs.POKEMON)
      root = data.getTreeRoot(fn, "Ditto main")

      for sp in data.getChildren(root, "species"):
         if data.getAttr(sp, "id", data.D_STRING) == self.species:
            self.speciesNode = sp
            break                           
      
      self.nickname = None
      
      self.level = level
      self.exp = 0

      typeNode = data.getChild(self.speciesNode, "type")
      self.type1 = data.getAttr(typeNode, "primary", data.D_STRING)
      self.type2 = data.getOptionalAttr(typeNode, "secondary", data.D_STRING, None)

      self.PID = random.randint(0, 4294967295)
      self.trainer = None
      self.trainerID = None

      self.ability = None

      self.gender = G_MALE
      self.nature = 0
      self.shiny = False

      self.form = 0
      self.happiness = 0
      self.pokerus = False
      
      self.EVs = {ST_HP: 0,
                  ST_ATTACK: 0,
                  ST_DEFENSE: 0,
                  ST_SPEED: 0,
                  ST_SPATTACK: 0,
                  ST_SPDEFENSE: 0}
      
      self.IVs = {ST_HP: random.randint(0,31),
                  ST_ATTACK: random.randint(0,31),
                  ST_DEFENSE: random.randint(0,31),
                  ST_SPEED: random.randint(0,31),
                  ST_SPATTACK: random.randint(0,31),
                  ST_SPDEFENSE: random.randint(0,31)}

      self.stats = {}
      self.calcStats()

      self.currentHP = self.stats[ST_HP]
      self.status = None

      self.moves = [None, None, None, None]
      movesNode = data.getChild(self.speciesNode, "attacks")
      moveNodes = sorted(data.getChildren(movesNode, "move"), key=lambda n: int(n.attrib["level"]))
      i = 0
      for node in moveNodes[-4:]:
         self.moves[i] = moves.Move(data.getAttr(node, "id", data.D_STRING))
         i += 1
      
      self.ballCaughtIn = 0

      self.heldItem = None

   def calcStats(self):
      statsNode = data.getChild(self.speciesNode, "basestats")
      
      baseStats = {}
      baseStats[ST_HP] = data.getAttr(statsNode, "hp", data.D_INT)
      baseStats[ST_ATTACK] = data.getAttr(statsNode, "attack", data.D_INT)
      baseStats[ST_DEFENSE] = data.getAttr(statsNode, "defense", data.D_INT)
      baseStats[ST_SPATTACK] = data.getAttr(statsNode, "spatk", data.D_INT)
      baseStats[ST_SPDEFENSE] = data.getAttr(statsNode, "spdef", data.D_INT)
      baseStats[ST_SPEED] = data.getAttr(statsNode, "speed", data.D_INT)

      self.stats[ST_HP] = (((self.IVs[ST_HP]+(2*baseStats[ST_HP])+(self.EVs[ST_HP]/4)+100)*self.level)/100)+10

      for stat in [ST_ATTACK, ST_DEFENSE, ST_SPATTACK, ST_SPDEFENSE, ST_SPEED]:
         self.stats[stat] = (((self.IVs[stat]+(2*baseStats[stat])+(self.EVs[stat]/4))*self.level)/100)+5

   def getName(self):
      if self.nickname is None:
         return data.getAttr(self.speciesNode, "name", data.D_STRING)
      else:
         return self.nickname

   def getBattler(self):
      graphicsNode = data.getChild(self.speciesNode, "graphics")
      battleNode = data.getChild(graphicsNode, "battle")
      battler = data.getImage(os.path.join(settings.path, "data", data.getAttr(battleNode, "front", data.D_STRING)), battleNode.ditto_fn)
      trans = data.getAttr(battleNode, "transparency", data.D_INT3LIST)
      battler.set_colorkey(trans)

      return battler
      
class Party():
   def __init__(self):
      self.pokemon = []

   def add(self, poke):
      self.pokemon.append(poke)

   def __getitem__(self, i):
      return self.pokemon[i]

   def __len__(self):
      return len(self.pokemon)

import pygame
import globs
from game import Game
from camera import Camera
import events

class debugGame(Game):
   def __init__(self, screen, savegame=None):
      Game.__init__(self, screen, savegame)

      self.camera = debugCamera(self.screen, self)
      self.camera.attachTo(self.player)

class debugCamera(Camera):
   def __init__(self, screen, game):
      Camera.__init__(self, screen)

      self.game = game

      self.walkontoTile = pygame.Surface(globs.TILESIZE)
      self.walkontoTile.fill((255,0,0))
      self.walkontoTile.set_alpha(127)

      self.investigateTile = pygame.Surface(globs.TILESIZE)
      self.investigateTile.fill((0,255,0))
      self.investigateTile.set_alpha(127)

      self.warpTile = pygame.Surface(globs.TILESIZE)
      self.warpTile.fill((0,0,255))
      self.warpTile.set_alpha(127)

   def drawFrame(self):
      Camera.drawFrame(self)

      if self.attach != None: #if attched to something
         mMap = self.attach.map #use the map of the attached object
         position = self.attach.position #use the position of the attched object
         cameraOffset = self.attach.getMoveOffset() #use the offset of the attched object
      else: #else
         mMap = self.map #use the camera's map
         position = self.position #use the camera's position
         cameraOffset = (0,0) #no offset

      for x in range(-1, self.size[0]+1):
         for y in range(-1, self.size[1]+1):
            reqPosition = position[0]-self.centre[0]+x, position[1]-self.centre[1]+y
            if mMap.events.has_key(reqPosition):
               e = mMap.events[reqPosition]
               if e.trigger == events.EV_WALKONTO:
                  if e.__class__.__name__ == "Warp":
                     self.screen.blit(self.warpTile, ((x*globs.TILESIZE[0])-cameraOffset[0], (y*globs.TILESIZE[1])-cameraOffset[1]))
                  else:
                     self.screen.blit(self.walkontoTile, ((x*globs.TILESIZE[0])-cameraOffset[0], (y*globs.TILESIZE[1])-cameraOffset[1]))
               elif e.trigger == events.EV_INVESTIGATE:
                  self.screen.blit(self.investigateTile, ((x*globs.TILESIZE[0])-cameraOffset[0], (y*globs.TILESIZE[1])-cameraOffset[1]))
      

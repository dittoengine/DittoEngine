import pygame

class ForegroundObject():
   """
   Class to provide basic structure for controlling foreground objects.

   Used across the whole system to control the active element.
   When the busy attribute is False, the parent object should clean up the foreground object.
   """
   
   def __init__(self):
      """Initialize busy to False, should be overridden by any subclasses"""
      self.busy = False

   def inputButton(self, button):
      """
      Process a button press

      button - the button which has been pressed
      """
      pass

   def draw(self):
      """Draw the object"""
      pass

   def tick(self):
      """Update the object"""
      pass

class FadeOutAndIn(ForegroundObject):
   """
   Foreground object to provide a fade transition.
   """
   
   def __init__(self, screen, time):
      """
      Create a surface to use to darken the screen, and set busy.

      screen - the surface to act on.
      time - the time taken to fade out and then back in.
      """

      #store the screen and the time to spend on each of the fade out and in
      self.screen = screen
      self.halftime = time/2

      #create a surface and fill it black
      #start with it transparent
      self.surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
      self.surface.fill((0,0,0))
      self.surface.set_alpha(0)

      #start the count at 0 and set busy
      self.count = 0
      self.busy = True

   def draw(self):
      """Draw the fade onto the screen"""

      self.screen.blit(self.surface, (0,0))

   def tick(self):
      """Update the fade effect one frame"""

      #increase the count and determine the opacity of the fade
      #if we've finished, set busy to False
      self.count += 1
      if self.count <= self.halftime:
         self.surface.set_alpha(int((self.count*255)/self.halftime))
      elif self.count <= self.halftime*2:
         self.surface.set_alpha(int(255-(((self.count-self.halftime)*255)/self.halftime)))
      if self.count >= self.halftime*2:
         self.busy = False

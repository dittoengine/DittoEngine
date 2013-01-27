import script_engine

class VisibleObject(script_engine.ScriptableObject):
   def __init__(self):
      script_engine.ScriptableObject.__init__(self)
      
      self.map = None #no map yet
      self.position = None #no position yet
      self.level = None #no level yet
      self.visible = True #we're visible
      self.tileset = None #no tileset yet
      self.tileOffset = None
      self.animations = {} #initialize animations dictionary
      self.animation = None

   def tick(self):
      if self.animation != None:
         if self.animation.active: #if currently animated
            self.animation.tick() #advance the animation

   def getTile(self):
      if self.animation.active: #if animated
         i = self.animation.getFrame() #get the frame from the animation
      else: #else
         i = 0 #get the first tile
      return self.tileset[i] #return the required tile  

   def setPosition(self, mMap, position, level):
      self.map = mMap #store map
      self.position = position #store position
      self.level = level #store level



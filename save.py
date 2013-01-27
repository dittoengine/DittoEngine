class Save():
   def __init__(self, fn):
      self.fn = fn #store the filename
      self.currentMap = None #no map yet
      self.currentPosition = None #no position yet
      self.currentLevel = None #no level yet
      self.currentDirection = None #no direction yet
      self.variables = {} #initialize game save variables
      self.party = None

   

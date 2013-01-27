import os

class DittoError(Exception):
   """Base exception inherited by other exceptions."""
   
   def describe(self):
      """Return a list of strings to print out."""
      
      return []

class DIOError(DittoError):
   def __init__(self, fn, path):
      self.fn = fn
      self.path = path

   def describe(self):
      return ["File not accessible (probably doesn't exist)",
              "In file %s attempting to open %s" % (os.path.split(self.fn)[1], os.path.split(self.path)[1])]

class DUnsupportedError(DittoError):
   def __init__(self, fn, feature, option):
      self.fn = fn
      self.feature = feature
      self.option = option

   def describe(self):
      return ["Unsupported feature",
              "In file %s" % os.path.split(self.fn)[1],
              "Unsupported %s: %s" % (self.feature, self.option)]

class DInvalidResourceError(DittoError):
   def __init__(self, fn, resourcePath):
      self.fn = fn
      self.resourcePath = resourcePath

   def describe(self):
      return ["Invalid resource",
              "In file %s:" % os.path.split(self.fn)[1],
              "Resource %s is not correct" % os.path.split(self.resourcePath)[1]]


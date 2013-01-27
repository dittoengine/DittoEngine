import os

import error

class DSyntaxError(error.DittoError):
   def __init__(self, fn, scriptId, lineno, val):
      self.lineno = lineno
      self.val = val
      self.fn = fn
      self.scriptId = scriptId

   def describe(self):
      print self.fn
      return ["Syntax error!",
              "In file %s, script %s" % (os.path.split(self.fn)[1], self.scriptId),
              "On line %i, at: %s" % (self.lineno, self.val),
              "Syntax is not correct"]

class DOperatorError(error.DittoError):
   def __init__(self, fn, scriptId, lineno, op, lhs, rhs):
      self.fn = fn
      self.scriptId = scriptId
      self.lineno = lineno
      self.op = op
      self.lhs = lhs
      self.rhs = rhs

   def describe(self):
      print self.fn
      return ["Operator error!",
              "In file %s, script %s" % (os.path.split(self.fn)[1], self.scriptId),
              "On line %i" % self.lineno,
              "Operator %s is not valid for operands %s and %s" % (self.op, str(self.lhs), str(self.rhs))]

class DLookupError(error.DittoError):
   def __init__(self, name):
      self.name = name

class DNameError(error.DittoError):
   def __init__(self, fn, scriptId, lineno, name):
      self.lineno = lineno
      self.fn = fn
      self.scriptId = scriptId
      self.name = name

   def describe(self):
      print self.fn
      return ["Name error!",
              "In file %s, script %s" % (os.path.split(self.fn)[1], self.scriptId),
              "On line %i" % self.lineno,
              "Name %s is not recognised" % self.name]

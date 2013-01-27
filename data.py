import os
import xml.etree.ElementTree as ET

import pygame

import error
import globs

D_STRING = 0
D_INT = 1
D_INTLIST = 2
D_INT2LIST = 3
D_INT3LIST = 4

class DMissingAttributeError(error.DittoError):
   def __init__(self, node, attr):
      self.fn = node.ditto_fn
      self.nodeName = node.tag
      self.attr = attr

   def describe(self):
      return ["Missing attribute",
              "On node <%s> in file %s:" % (self.nodeName, os.path.split(self.fn)[1]),
              "Unable to find attribute \"%s\"" % self.attr]

class DInvalidAttributeError(error.DittoError):
   def __init__(self, node, attr):
      self.fn = node.ditto_fn
      self.nodeName = node.tag
      self.attr = attr

   def describe(self):
      return ["Invalid attribute",
              "On node <%s> in file %s:" % (self.nodeName, os.path.split(self.fn)[1]),
              "Attribute \"%s\" is not correct" % self.attr]

class DMissingNodeError(error.DittoError):
   def __init__(self, parentNode, childName):
      self.fn = parentNode.ditto_fn
      self.parentName = parentNode.tag
      self.childName = childName

   def describe(self):
      return ["Missing node",
              "On node <%s> in file %s:" % (self.parentName, os.path.split(self.fn)[1]),
              "Unable to find child node <%s>" % self.childName]

def getTreeRoot(path, fn="Unknown file"):
   """
   Use a filename to create an XML tree and return the root node.

   path - the path to the XML file.
   fn - the file from which the XML file was requested.
   """

   #try to open it
   #if there's an IO error, raise the relevant exception.
   try:
      tree = ET.parse(path)
   except IOError:
      raise error.DIOException(fn, path)
   root = tree.getroot()

   #set the filename
   root.ditto_fn = path
   
   return root

def getAttr(node, attribute, formatting):
   """
   Get an attribute from a node, putting it to the required format.

   node - the node to get the attribute from.
   attribute - the attribute to get.
   formatting - the style to return the data in.
   """

   #try to get the raw attribute
   #if it doesn't exist, raise the relevant exception
   try:
      att = node.attrib[attribute]
   except KeyError:
      raise DMissingAttributeError(node, attribute)

   #depending on the requested formatting format, get the attribute into the required style
   #if it doesn't match the style requested, raise an exception
   if formatting == D_STRING:
      return att
   
   elif formatting == D_INT:
      try:
         return int(att)
      except ValueError:
         raise DInvalidAttributeError(node, attribute)

   elif formatting == D_INTLIST:
      try:
         return map(int, att.split(","))
      except ValueError:
         raise DInvalidAttributeError(node, attribute)
      
   elif formatting == D_INT2LIST:
      try:
         return map(int, att.split(","))
      except ValueError:
         raise DInvalidAttributeError(node, attribute)
      if len(ans) != 2:
         raise DInvalidAttributeError(node, attribute)

   elif formatting == D_INT3LIST:
      try:
         return map(int, att.split(","))
      except ValueError:
         raise DInvalidAttributeError(node, attribute)
      if len(ans) != 3:
         raise DInvalidAttributeError(node, attribute)

def getOptionalAttr(node, attribute, formatting, default=None):
   """
   Get an attribute from a node if it exists, putting it to the required format.

   node - the node to get the attribute from.
   attribute - the attribute to get.
   formatting - the style to return the data in.
   default - the value to return if the attribute is not found.
   """

   #try to get the raw attribute
   #if it doesn't exist, raise the relevant exception
   try:
      att = node.attrib[attribute]
   except KeyError:
      return default

   #depending on the requested formatting format, get the attribute into the required style
   #if it doesn't match the style requested, raise an exception
   if formatting == D_STRING:
      return att
   
   elif formatting == D_INT:
      try:
         return int(att)
      except ValueError:
         raise DInvalidAttributeError(node, attribute)

   elif formatting == D_INTLIST:
      try:
         return map(int, att.split(","))
      except ValueError:
         raise DInvalidAttributeError(node, attribute)
      
   elif formatting == D_INT2LIST:
      try:
         return map(int, att.split(","))
      except ValueError:
         raise DInvalidAttributeError(node, attribute)
      if len(ans) != 2:
         raise DInvalidAttributeError(node, attribute)

   elif formatting == D_INT3LIST:
      try:
         return map(int, att.split(","))
      except ValueError:
         raise DInvalidAttributeError(node, attribute)
      if len(ans) != 3:
         raise DInvalidAttributeError(node, attribute)
   
def getChild(node, name):
   """
   Get a child from a parent node.

   Raises an error if the child is not found.

   node - the parent node.
   name - the name of the child node.  
   """

   #try to find the child node
   #if it isn't found, raise the relevant exception
   ans = node.find(name)
   if ans is None:
      raise DMissingNodeError(node, name)

   #propagate the filename
   ans.ditto_fn = node.ditto_fn

   return ans

def getOptionalChild(node, name):
   """
   Get a child from a parent node.

   Returns None if child doesn't exist.

   node - the parent node.
   name - the name of the child node.  
   """

   #try to find the child node
   #if it isn't found, raise the relevant exception
   ans = node.find(name)
   if ans is None:
      return None

   #propagate the filename
   ans.ditto_fn = node.ditto_fn

   return ans

def getChildren(node, name):
   """
   Get all the child nodes of a certain name from a parent node.

   Returns an empty list if none are found.

   node - the parent node.
   name - the name of the child nodes.
   """

   #get any child nodes
   nodes = node.findall(name)

   #propagate the filename
   for n in nodes:
      n.ditto_fn = node.ditto_fn

   return nodes

def getImage(imagePath, fn="Unknown file"):
   """
   Open an image filename to a pygame surface.

   imagePath - the path to the image file
   fn - the file from which the image was requested
   """

   #try to open the file
   #if it doesn't work, raise the relevant exception
   try:
      return pygame.image.load(imagePath)
   except:
      raise error.DInvalidResourceError(fn, imagePath)

def check(exp, resourcePath, fn="Unknown file"):
   """
   Perform a boolean check to make sure a resource is suitable.

   If exp evaluates to False, raises an exception.

   exp - the expression to evaluate.
   resourcePath - the path to the resource that the check is relevant to.
   fn - the file from which the resource was requested.
   """
   
   if not exp:
      raise error.DInvalidResourceError(fn, resourcePath)



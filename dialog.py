import os
import xml.etree.ElementTree as ET

import pygame

import foreground_object
import box
import font
import globs
import settings
import data
import sound
import game_input

#line separator in input text
LINESEP = "$$"

#define spacings
BORDER = 10 #spacing inside the box
LINEBUFFER = 2 #spacing between lines
OBJECTBUFFER = 2 #spacing between boxes and edges

class Dialog(foreground_object.ForegroundObject):
   """
   Class to provide dialogs to be shown by the script engine.
   """
   
   def __init__(self, text, screen, drawCursor=True):
      """
      Create the dialog box and load cursors.

      text - a list of lines of text to go in the dialog.
      font - the font with which to write the text.
      screen - the surface to draw the dialog onto.
      soundManager - the sound manager.
      drawCursor - whether a continuation cursor should be drawn when the text has finished writing.
      """

      #store variables we'll need again
      self.text = text.split(LINESEP)
      self.screen = screen
      self.drawCursor = drawCursor
      
      #determine the speed to write at, in characters per tick
      if settings.textSpeed == "SLOW":
         self.speed = 1
      elif settings.textSpeed == "MEDIUM":
         self.speed = 2
      elif settings.textSpeed == "FAST":
         self.speed = 4

      #parse the dialog xml file
      fn = os.path.join(settings.path, "data", globs.DIALOG)
      root = data.getTreeRoot(fn, "Ditto main")
      transparency = data.getAttr(root, "transparency", data.D_INT3LIST)

      #create font
      fontPath = os.path.join(settings.path, "data", globs.FONT)
      self.font = font.Font(fontPath)

      #create the box
      size = ((self.screen.get_width()-(OBJECTBUFFER*2), (len(self.text)*(self.font.height+LINEBUFFER))-LINEBUFFER+(BORDER*2)))
      self.box = box.Box(size).convert(self.screen)

      #load the cursors
      cursorPath = os.path.join(settings.path, "data", data.getAttr(root, "cursor", data.D_STRING))
      self.cursor = data.getImage(cursorPath).convert(self.screen)
      self.cursor.set_colorkey(transparency)
      self.cursorLocation = (self.screen.get_width()-OBJECTBUFFER-BORDER-self.cursor.get_width(),
                             self.screen.get_height()-OBJECTBUFFER-BORDER-self.cursor.get_height())

      cursorPath = os.path.join(settings.path, "data", data.getAttr(root, "sidecursor", data.D_STRING))
      self.sideCursor = data.getImage(cursorPath).convert(self.screen)
      self.sideCursor.set_colorkey(transparency)

      #calculate location of dialog box
      self.location = OBJECTBUFFER, self.screen.get_height()-self.box.get_height()-OBJECTBUFFER

      #start progress at 0 and set drawing and busy
      self.progress = 0
      self.writing = True
      self.busy = True

   def draw(self):
      """Draw the dialog onto its screen."""

      #start a count of how many characters have been drawn
      #for each line of text, work out where it will be drawn
      #then work out how many characters on this line will be drawn
      #finally draw the text required onto the box, and increase the character count                             
      c = 0
      for i in range(0, len(self.text)): #for count lines of text
         line = self.text[i] #get the line
         location = BORDER, BORDER+(i*(self.font.height+LINEBUFFER))
         charsOnLine = self.progress - c
         if charsOnLine < len(line):
            cutText = line[:charsOnLine]
         else:
            cutText = line
         self.font.writeText(cutText, self.box, location)
         c += len(cutText)

      #draw the box
      self.screen.blit(self.box, self.location)

      #if we've finished writing and a cursor is required, draw it
      if not self.writing and self.drawCursor:
         self.screen.blit(self.cursor, self.cursorLocation)

   def inputButton(self, button):
      """
      Process a button press

      button - the button which has been pressed.
      """

      #if it's the confirm button, and we've finished drawing, then we're done                          
      if button == game_input.BT_A:
         if not self.writing:
            self.busy = False
            sound.playEffect(sound.SD_SELECT)

   def tick(self):
      """Update the dialog one frame"""

      #increase the progress, and if we've reached the end the set drawing to False                      
      self.progress += self.speed
      if self.progress > sum(map(len, self.text)):
         self.writing = False

class ChoiceDialog(Dialog):
   """
   Adds a choice box to a dialog.

   Returns the choice selected to the LASTRESULT script engine variable.
   """
   
   def __init__(self, text, font, screen, scriptEngine, choices):
      """
      Initialize the dialog and create the choice box.

      text - a list of lines of text to go in the dialog.
      font - the font with which to write the text.
      screen - the surface to draw the dialog onto.
      scriptEngine - the engine to return the option chosen to.
      choices - the possible options to choose from.
      """

      #initialize the dialog
      Dialog.__init__(self, text, font, screen, False) #initialize the main dialog

      #store variables we'll need again
      self.scriptEngine = scriptEngine
      self.choices = choices

      #create the choice box and write the options onto it
      maxWidth = max(map(self.font.calcWidth, self.choices))
      size = (maxWidth+(BORDER*2)+self.sideCursor.get_width(),
              ((self.font.height+LINEBUFFER)*len(self.choices))-LINEBUFFER+(BORDER*2))
      self.choiceBox = box.Box(size).convert(self.screen)

      for i in range(0, len(choices)):
         choice = choices[i]
         location = BORDER+self.sideCursor.get_width(), BORDER+(i*(self.font.height+LINEBUFFER))
         self.font.writeText(choice, self.choiceBox, location)

      #calculate the location of the choice box
      self.choiceLocation = (self.screen.get_width()-self.choiceBox.get_width()-OBJECTBUFFER,
                             self.location[1]-self.choiceBox.get_height()-OBJECTBUFFER)

      #set the current selected option to the first one
      self.current = 0

   def draw(self):
      """Draw the dialog, and choice box if required, onto its screen."""

      #draw the dialog
      Dialog.draw(self)

      #if the dialog has finished writing, draw the choice box and its cursor
      if not self.writing:
         self.screen.blit(self.choiceBox, self.choiceLocation)
         cursorLocation = (self.choiceLocation[0]+BORDER,
                           self.choiceLocation[1]+BORDER+(self.current*(self.font.height+LINEBUFFER)))
         self.screen.blit(self.sideCursor, cursorLocation)

   def inputButton(self, button):
      """
      Process a button press.

      button - the button which has been pressed.
      """

      #feed the button to the main dialog to process
      Dialog.inputButton(self, button)

      #if it's UP or DOWN, change the selected option as required
      if button == game_input.BT_DOWN:
         if self.current < len(self.choices)-1:
            self.current += 1
            sound.playEffect(sound.SD_CHOOSE)
      elif button == game_input.BT_UP:
         if self.current > 0:
            self.current -= 1
            sound.playEffect(sound.SD_CHOOSE)

      #if we're exiting, set the LASTRESULT script engine variable to the current selected choice      
      if self.busy == False:
         self.scriptEngine.variables["LASTRESULT"] = self.choices[self.current]

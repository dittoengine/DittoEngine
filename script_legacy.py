import globs
import settings
import font
import dialog
import os
import tilemap
import foreground_object
import events
import sprite
import sound
import pokemon
import data

#define command constants
CMD_LOCK = 0
CMD_UNLOCK = 1
CMD_FACEPLAYER = 2
CMD_WAIT = 3
CMD_MOVEME = 4
CMD_DIALOG = 8
CMD_SETVAR = 9
CMD_GETVAR = 10
CMD_PRINTRESULT = 11
CMD_COMPARE = 12
CMD_GOTO = 13
CMD_IFFALSEGOTO = 14
CMD_MOVEPLAYER = 15
CMD_CHOICEDIALOG = 19
CMD_SHOWSPRITE = 20
CMD_HIDESPRITE = 21
CMD_WARP = 22
CMD_FADEOUTANDIN = 23
CMD_GIVEPOKEMON = 24
CMD_SURF = 25

class ScriptEngine():
   """Singleton object for running scripts."""
   
   #borg singleton
   __shared_state = {}
   
   def __init__(self):
      """
      Get the shared state for this particular instance.

      Call setup() to init the object first time.
      """

      self.__dict__ = self.__shared_state
      
   def setup(self, game):
      """
      Get the script engine ready to run scripts.

      game - the Game object to run scripts on.
      """

      #store game object
      self.game = game


      self.font = font.Font(os.path.join(settings.path, "data", globs.FONT)) #create the font

      #initialise variables needed to run
      self.running = False
      self.queue = []
      self.currentCommand = 0
      self.waiting = False
      self.waitingFor = None
      self.countDown = 0

      #initialise script variables
      self.variables = {}
      self.result = None

      #determine behaviour scripts
      tree = data.getTree(globs.BEHAVIOURS)
      root = tree.getroot()
      self.behaviours = {}
      for behaviourNode in data.getChildren(root, "behaviour", globs.BEHAVIOURS):
         i = data.getAttr(behaviourNode, "index", data.D_INT, globs.BEHAVIOURS)
         s = data.getChild(behaviourNode, "script", globs.BEHAVIOURS)
         self.behaviours[i] = Script(s, False)
      
   def run(self, s, caller=None):
      if not self.running:
         print "---"
         print "Script called by " + str(caller)
         self.running = True #running a script
         self.script = s #store the script
         self.caller = caller #store the caller of the script
         self.currentCommand = 0 #reset command counter to start
         self.waiting = False #not yet waiting
         self.waitingFor = None #not waiting for anything
      else:
         print "Script queued"
         self.queue.append((s, caller))

   def processBehaviour(self, b):
      try:
         s = self.behaviours[b]
         self.run(s)
      except KeyError:
         pass

   def tick(self):
      if self.waiting: #if waiting
         if self.waitingFor is not None: #if we're waiting for an object
            if not self.waitingFor.busy: #if what we're waiting for is no longer busy
               self.waiting = False #stop waiting
               self.waitingFor = None #no longer waiting for anything
         else: #else
            self.countdown -= 1 #decrease the countdown
            if self.countdown <= 0: #if we've finished counting down
               self.waiting = False #stop waiting
      
      while (not self.waiting and self.running): #while we're not waiting and still have commands to process
         cmd = self.script.commands[self.currentCommand] #get the current command
         if cmd[0] == CMD_LOCK: #if it's LOCK
            print "LOCK"
            self.game.player.lock() #lock the player
            if self.caller.__class__.__name__ == "NPC": #if the script has a caller
               self.caller.lock() #lock it
         elif cmd[0] == CMD_UNLOCK: #if it's UNLOCK
            print "UNLOCK"
            self.game.player.unlock() #unlock the player
            if self.caller.__class__.__name__ == "NPC": #if the script has a caller
               self.caller.unlock() #unlock it
         elif cmd[0] == CMD_FACEPLAYER: #if it's FACEPLAYER
            print "FACEPLAYER"
            difference = self.game.player.position[0]-self.caller.position[0], self.game.player.position[1]-self.caller.position[1] #calculate offset between player and caller
            if difference == (0, -1): #if player is above caller
               self.caller.direction = sprite.DIR_UP #face UP
            elif difference == (0, 1): #if player is below caller
               self.caller.direction = sprite.DIR_DOWN #face DOWN
            elif difference == (-1, 0): #if player is to left of caller
               self.caller.direction = sprite.DIR_LEFT #face LEFT
            elif difference == (1, 0): #if player is to right of caller
               self.caller.direction = sprite.DIR_RIGHT #face RIGHT        
         elif cmd[0] == CMD_WAIT: #if it's WAIT
            print "WAIT"
            self.waiting = True #we're waiting
            self.waitingFor = None #not waiting for an object
            self.countdown = cmd[1] #set countdown as needed
         elif cmd[0] == CMD_MOVEME: #if it's MOVEME
            print "MOVEME"
            self.caller.walkUp(cmd[1], True) #walk, force move
            self.waiting = True #we're waiting
            self.waitingFor = self.caller #waiting for caller       
         elif cmd[0] == CMD_DIALOG: #if it's DIALOG
            print "DIALOG"
            text = map(self.resolveString, cmd[1]) #resolve the text strings for variables
            d = dialog.Dialog(text, self.font, self.game.screen, cmd[2]) #create the dialog
            self.game.foregroundObject = d #set it as the game's active object
            self.waiting = True #we're waiting
            self.waitingFor = d #waiting for the dialog
         elif cmd[0] == CMD_SETVAR:
            print "SETVAR"
            if cmd[1][0] == "$":
               self.variables[cmd[1][1:-1]] = cmd[2]
            elif cmd[1][0] == "*":
               self.game.savegame.variables[cmd[1][1:-1]] = cmd[2]
         elif cmd[0] == CMD_GETVAR:
            print "GETVAR"
            self.result = self.variables[cmd[1]]
         elif cmd[0] == CMD_COMPARE: #if it's COMPARE
            print "COMPARE"
            self.result = (self.resolveString(cmd[1]) == self.resolveString(cmd[2])) #store whether the two are equal
         elif cmd[0] == CMD_GOTO: #if it's GOTO
            print "GOTO"
            self.currentCommand = cmd[1]-1 #go to the line before the one required, which will then be advanced to the correct line
         elif cmd[0] == CMD_IFFALSEGOTO: #if it's IFFALSEGOTO
            print "IFFALSEGOTO"
            if not self.result: #if comparison result is False
               self.currentCommand = cmd[1]-1 #goto to the line before the one required, which will then be advanced to the correct line
         elif cmd[0] == CMD_MOVEPLAYER: #if it's MOVEPLAYER
            print "MOVEPLAYER"
            self.game.player.walk(cmd[1], True) #move the player
            self.waiting = True #we're waiting
            self.waitingFor = self.game.player #we're waiting for the player
         elif cmd[0] == CMD_CHOICEDIALOG: #if it's CHOICEDIALOG
            print "CHOICEDIALOG"
            text = map(self.resolveString, cmd[1]) #resolve the text for variables
            d = dialog.ChoiceDialog(text, self.font, self.game.screen, self, cmd[2]) #create the choice dialog
            self.game.foregroundObject = d #set it as the game's active object
            self.waiting = True #we're waiting
            self.waitingFor = d #waiting for the choice dialog
         elif cmd[0] == CMD_SHOWSPRITE: #if it's SHOWSPRITE
            print "SHOWSPRITE"
            if self.caller is not None: #if there's a caller
               if self.caller.__class__.__name__ == "Tilemap": #if it was a map
                  self.caller.getSpriteById(cmd[1]).visible = True #set the sprite visible
               elif self.caller.__class__.__name__ == "NPC": #if it was an NPC
                  self.caller.map.getSpriteById(cmd[1]).visible = True #set the sprite visible
            else: #else
               self.game.player.map.getSpriteById(cmd[1]).visible = True #set the sprite visible
         elif cmd[0] == CMD_HIDESPRITE: #if it's HIDESPRITE
            print "HIDESPRITE"
            if self.caller is not None: #if there's a caller
               if self.caller.__class__.__name__ == "Tilemap": #if it was a map
                  self.caller.getSpriteById(cmd[1]).visible = False #set the sprite invisible
               elif self.caller.__class__.__name__ == "NPC": #if it was an NPC
                  self.caller.map.getSpriteById(cmd[1]).visible = False #set the sprite invisible
            else: #else
               self.game.player.map.getSpriteById(cmd[1]).visible = False #set the sprite invisible
         elif cmd[0] == CMD_WARP:
            print "WARP"
            if False:
               p = self.game.player
               del(p.map.sprites["PLAYER"])
               p.map = tilemap.Tilemap(cmd[1], self)
               p.map.loadConnections()
               p.position = cmd[2]
               p.destination = cmd[2]
               p.level = cmd[3]
               p.map.sprites["PLAYER"] = p
               sound.playMusic(p.map.music)
            else:
               p = self.game.player
               mMap = tilemap.Tilemap(cmd[1], self)
               p.transferTo(mMap, cmd[2])
               p.destination = p.getPositionInFront()
               p.level = cmd[3]
         elif cmd[0] == CMD_FADEOUTANDIN:
            print "FADEOUTANDIN"
            self.game.foregroundObject = foreground_object.FadeOutAndIn(self.game.screen, cmd[1])
         elif cmd[0] == CMD_GIVEPOKEMON:
            print "GIVEPOKEMON"
            poke = pokemon.Pokemon(cmd[1], cmd[2])
            self.game.player.party.add(poke)
         elif cmd[0] == CMD_SURF:
            print "SURF"
            self.game.player.surf()
            
         self.currentCommand += 1 #advance to next command
         if self.currentCommand >= len(self.script.commands): #if we've reached the end of the script
            if len(self.queue) == 0:
               self.running = False #no longer running
            else:
               print "Script from queue"
               s, caller = self.queue.pop()
               self.running = True #running a script
               self.script = s #store the script
               self.caller = caller #store the caller of the script
               self.currentCommand = 0 #reset command counter to start
               self.waiting = False #not yet waiting
               self.waitingFor = None #not waiting for anything
            break #stop processing

   def resolveString(self, text):
      while text.find("$") != -1:
         first = text.find("$")
         second = text[first+1:].find("$")
         var = text[first+1:first+second+1]
         if not self.variables.has_key(var):
            self.variables[var] = ""
         text = text[:first] + str(self.variables[var]) + text[first+second+2:]

      while text.find("*") != -1:
         first = text.find("*")
         second = text[first+1:].find("*")
         var = text[first+1:first+second+1]
         if not self.game.savegame.variables.has_key(var):
            self.game.savegame.variables[var] = ""
         text = text[:first] + str(self.game.savegame.variables[var]) + text[first+second+2:]
         
      return text

class Script():
   def __init__(self, node, triggered=True):
      self.script = node
      if triggered:
         if node.attrib["trigger"] == "investigate":
            self.trigger = events.EV_INVESTIGATE
         elif node.attrib["trigger"] == "walkonto":
            self.trigger = events.EV_WALKONTO
         elif node.attrib["trigger"] == "load":
            self.trigger = events.EV_LOAD
         elif node.attrib["trigger"] == "newgame":
            self.trigger = events.EV_NEWGAME

      self.commands = self.parseNode(self.script)

   def parseNode(self, node):
      commands = []
      for command in node.getchildren():
         if command.tag == "lock":
            commands.append([CMD_LOCK])
         elif command.tag == "unlock":
            commands.append([CMD_UNLOCK])
         elif command.tag == "faceplayer":
            commands.append([CMD_FACEPLAYER])
         elif command.tag == "wait":
            commands.append([CMD_WAIT, int(command.attrib["frames"])])
         elif command.tag == "moveme":
            for step in command.attrib["course"].split(","):
               if step == "u":
                  commands.append([CMD_MOVEME, DIR_UP])
               elif step == "d":
                  commands.append([CMD_MOVEME, DIR_DOWN])
               elif step == "l":
                  commands.append([CMD_MOVEME, DIR_LEFT])
               elif step == "r":
                  commands.append([CMD_MOVEME, DIR_RIGHT])
         elif command.tag == "dialog":
            cursor = True
            if command.attrib.has_key("last"):
               if command.attrib["last"] == "yes":
                  cursor = False
            commands.append([CMD_DIALOG, command.attrib["text"].split(";"), cursor])
         elif command.tag == "set":
            commands.append([CMD_SETVAR, command.attrib["name"], command.attrib["value"]])
         elif command.tag == "get":
            commands.append([CMD_GETVAR, command.attrib["name"]])
         elif command.tag == "if":
            ifTrue = self.parseNode(command.find("true"))
            ifFalse = self.parseNode(command.find("false"))
            commands.append([CMD_COMPARE, command.attrib["lhs"], command.attrib["rhs"]])
            commands.append([CMD_IFFALSEGOTO, len(commands)+len(ifTrue)+2])
            commands += ifTrue
            commands.append([CMD_GOTO, len(commands)+len(ifFalse)+1])
            commands += ifFalse
         elif command.tag == "moveplayer":
            for step in command.attrib["course"].split(","):
               if step == "u":
                  commands.append([CMD_MOVEPLAYER, sprite.DIR_UP])
               elif step == "d":
                  commands.append([CMD_MOVEPLAYER, sprite.DIR_DOWN])
               elif step == "l":
                  commands.append([CMD_MOVEPLAYER, sprite.DIR_LEFT])
               elif step == "r":
                  commands.append([CMD_MOVEPLAYER, sprite.DIR_RIGHT])
         elif command.tag == "choicedialog":
            commands.append([CMD_CHOICEDIALOG, command.attrib["text"].split(";"), command.attrib["choices"].split(";")])
         elif command.tag == "showsprite":
            commands.append([CMD_SHOWSPRITE, command.attrib["id"]])
         elif command.tag == "hidesprite":
            commands.append([CMD_HIDESPRITE, command.attrib["id"]])
         elif command.tag == "givepokemon":
            commands.append([CMD_GIVEPOKEMON, command.attrib["id"], int(command.attrib["level"])])
         elif command.tag == "surf":
            commands.append([CMD_SURF])
            
      return commands

   

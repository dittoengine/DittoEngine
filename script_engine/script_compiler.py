from commands import *

def toCommands(node):
   cmds = []
   if node.kind == "STATEMENTLIST":
      for child in node.children:
         cmds += toCommands(child)
   elif node.kind == "PRINT":
      exprNode = node.children[0]
      cmds.append([CMD_PRINT, exprNode])
   elif node.kind == "ASSIGN":
      idChainNode, exprNode = node.children
      cmds.append([CMD_ASSIGN, idChainNode, exprNode])
   elif node.kind == "ASSIGNCOMMAND":
      idChainNode, commandNode = node.children
      commandIdChainNode, commandArgListNode = commandNode.children
      cmds.append([CMD_COMMANDASSIGN, idChainNode, commandNode])
   elif node.kind == "COMMANDCALL":
      commandNode = node.children[0]
      idChainNode, argListNode = commandNode.children
      cmds.append([CMD_COMMANDCALL, commandNode])
   elif node.kind == "IF":
      if len(node.children) == 2:
         exprNode, trueNode = node.children
         trueCmds = toCommands(trueNode)
         cmds.append([CMD_EVAL, exprNode])
         cmds.append([CMD_IFFALSEGOTOREL, len(trueCmds)])
         cmds += trueCmds
      elif len(node.children) == 3:
         exprNode, trueNode, falseNode = node.children
         trueCmds = toCommands(trueNode)
         falseCmds = toCommands(falseNode)
         cmds.append([CMD_EVAL, exprNode])
         cmds.append([CMD_IFFALSEGOTOREL, len(trueCmds)+1])
         cmds += trueCmds
         cmds.append([CMD_GOTOREL, len(falseCmds)])
         cmds += falseCmds         

   return cmds   

from pygame.locals import *

import game_input

DEBUG = False

screenSize = 19,15

framerate = 22
textSpeed = "SLOW"

music = True
soundEffects = True

path = "C:\\Users\\User\\Documents\\Python\\Ditto\\Gen3game"

keys = {K_UP: game_input.BT_UP,
        K_DOWN: game_input.BT_DOWN,
        K_LEFT: game_input.BT_LEFT,
        K_RIGHT: game_input.BT_RIGHT,
        K_z: game_input.BT_A,
        K_x: game_input.BT_B,
        K_RETURN: game_input.BT_START,
        K_SPACE: game_input.BT_SAVE,
        K_q: game_input.BT_DEBUG}

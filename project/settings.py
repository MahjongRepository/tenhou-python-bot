# -*- coding: utf-8 -*-

TENHOU_HOST = '133.242.10.78'
TENHOU_PORT = 10080

USER_ID = 'NoName'

LOBBY = '0'
WAITING_GAME_TIMEOUT_MINUTES = 10

# in tournament mode bot is not trying to search the game
# it just sitting in the lobby and waiting for the game start
IS_TOURNAMENT = False

STAT_SERVER_URL = ''
STAT_TOKEN = ''

ENABLE_AI = True

"""
  0 - 1 - online, 0 - bots
  1 - aka forbidden
  2 - kuitan forbidden
  3 - hanchan
  4 - 3man
  5 - dan flag
  6 - fast game
  7 - dan flag

  Combine them as:
  76543210

  00001001 = 9 = hanchan ari-ari
  00000001 = 1 = tonpu-sen ari-ari
"""
GAME_TYPE = '1'

FIVE_REDS = False

try:
    from settings_local import *
except ImportError:
    pass

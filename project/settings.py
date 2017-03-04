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
  1 - has aka
  2 - kuitan forbidden
  3 - hanchan
  4 - 3man
  5 - dan flag
  6 - fast game
  7 - dan flag

  Combine them as:
  76543210

  00001001 = 9 = kyu, hanchan ari-ari
  00000001 = 1 = kyu, tonpusen ari-ari
  10001001 = 137 = dan, hanchan ari-ari
"""
GAME_TYPE = '1'


# game related settings
# TODO put them to the separate settings files
FIVE_REDS = False
OPEN_TANYAO = True

try:
    from settings_local import *
except ImportError:
    pass

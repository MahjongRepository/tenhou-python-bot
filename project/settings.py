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

AI_PACKAGE = 'first_version'
# class will be loaded automatically
AI_CLASS = None

"""
  Game type decoding:

  0 - 1 - online, 0 - bots
  1 - aka forbiden
  2 - kuitan forbidden
  3 - hanchan
  4 - 3man
  5 - dan flag
  6 - fast game
  7 - dan flag

  Combine them as:
  76543210

  # hanchan, ari-ari examples
  00001001 = 9   - kyu
  10001001 = 137 - dan
  00101001 = 41  - upperdan
  10101001 = 169 - phoenix

  00001011 = 11 - hanchan no red five, but with open tanyao

  00001001 = 9 - kyu, hanchan ari-ari
  00000001 = 1 - kyu, tonpusen ari-ari
"""

# for dynamic game type selection (based on the bot rank and rate)
# you can use:
# GAME_TYPE = None
GAME_TYPE = '1'

try:
    from settings_local import *
except ImportError:
    pass

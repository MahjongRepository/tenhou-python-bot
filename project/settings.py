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

# 1 - tonpu-sen, ari, ari
# 9 - hanchan, ari, ari
GAME_TYPE = '1'

try:
    from settings_local import *
except ImportError:
    pass

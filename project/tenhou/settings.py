USER_ID = 'NoName'

STAT_SERVER_URL = ''
STAT_TOKEN = ''

# 0,1 - tonpu-sen, ari, ari
# 0,9 - hanchan, ari, ari
GAME_TYPE = '0,1'

try:
    from .settings_local import *
except:
    pass

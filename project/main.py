# -*- coding: utf-8 -*-
from optparse import OptionParser

from tenhou.main import connect_and_play
from utils.logger import set_up_logging
from utils.settings_handler import settings

def parse_args_and_set_up_settings():
    attrs = OptionParser()
    attrs.add_option('-u', '--user_id',
                     default=settings.USER_ID,
                     help='Tenhou\'s user id. Example: IDXXXXXXXX-XXXXXXXX')
    attrs.add_option('-g', '--game_type',
                     default=settings.GAME_TYPE,
                     help='The game type in Tenhou.net format: 0,1 or 0,9')

    opts, _ = attrs.parse_args()

    settings.USER_ID = opts.user_id
    settings.GAME_TYPE = opts.game_type


def main():
    parse_args_and_set_up_settings()
    set_up_logging()

    connect_and_play()


if __name__ == '__main__':
    main()

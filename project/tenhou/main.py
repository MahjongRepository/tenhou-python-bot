# -*- coding: utf-8 -*-
import logging

from tenhou.client import TenhouClient
from utils.settings_handler import settings


logger = logging.getLogger('tenhou')


def connect_and_play():
    logger.info('AI: {}, {}'.format(settings.AI_CLASS.version, settings.AI_PACKAGE))

    client = TenhouClient()
    client.connect()

    try:
        was_auth = client.authenticate()

        if was_auth:
            client.start_game()
        else:
            client.end_game()
    except KeyboardInterrupt:
        logger.info('Ending the game...')
        client.end_game()
    except Exception as e:
        logger.exception('Unexpected exception', exc_info=e)
        logger.info('Ending the game...')
        client.end_game(False)

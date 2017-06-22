# -*- coding: utf-8 -*-
import logging

from mahjong.ai.main import MainAI
from tenhou.client import TenhouClient
from utils.settings_handler import settings


logger = logging.getLogger('tenhou')


def connect_and_play():
    logger.info('Bot AI enabled: {}'.format(settings.ENABLE_AI))
    if settings.ENABLE_AI:
        logger.info('AI version: {}'.format(MainAI.version))

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

# -*- coding: utf-8 -*-
import logging
import socket

from tenhou.client import TenhouClient
from utils.settings_handler import settings


logger = logging.getLogger('tenhou')


def connect_and_play():
    logger.info('Bot AI enabled: {}'.format(settings.ENABLE_AI))

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

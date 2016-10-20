# -*- coding: utf-8 -*-
import logging
import socket

from tenhou.client import TenhouClient
from utils.settings_handler import settings


logger = logging.getLogger('tenhou')


def connect_and_play():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((settings.TENHOU_HOST, settings.TENHOU_PORT))

    logger.info('Bot AI enabled: {}'.format(settings.ENABLE_AI))

    client = TenhouClient(s)
    was_auth = client.authenticate()

    if was_auth:
        client.start_the_game()
    else:
        client.end_the_game()

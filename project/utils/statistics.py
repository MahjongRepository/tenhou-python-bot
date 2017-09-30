# -*- coding: utf-8 -*-
import requests

from utils.settings_handler import settings


class Statistics(object):
    """
    Send data to https://github.com/MahjongRepository/mahjong-stat/ project
    """
    game_id = ''
    username = ''

    def send_statistics(self):
        url = settings.STAT_SERVER_URL
        if not url or not self.game_id:
            return False

        url = '{0}/api/v1/tenhou/game/add/'.format(url)
        data = {
            'id': self.game_id,
            'username': self.username
        }

        result = requests.post(url, data, headers={'Token': settings.STAT_TOKEN})

        return result.status_code == 200 and result.json()['success']

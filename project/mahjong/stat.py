# -*- coding: utf-8 -*-
import requests

from utils.settings_handler import settings


class Statistics(object):
    game_id = ''

    def send_statistics(self):
        url = settings.STAT_SERVER_URL
        if not url or not self.game_id:
            return False

        url = '{0}/api/v1/tenhou/game/add/'.format(url)

        result = requests.post(url, {'id': self.game_id}, headers={'Token': settings.STAT_TOKEN})

        return result.status_code == 200 and result.json()['success']

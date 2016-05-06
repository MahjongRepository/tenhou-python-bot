import json

import requests

from tenhou import settings


class Statistics(object):
    game_id = ''
    seat = 0
    scores = 0
    position = 0

    def send_statistics(self):
        url = settings.STAT_SERVER_URL
        if not url:
            return False

        url = '{0}/api/v1/game/add/'.format(url)

        data = {
            'id': self.game_id,
            'position': self.position,
            'scores': self.scores * 100,
            'seat': self.seat,
            'rule': settings.GAME_TYPE
        }

        result = requests.post(url, {'data': json.dumps(data)}, headers={'Token': settings.STAT_TOKEN})

        return result.status_code == 200

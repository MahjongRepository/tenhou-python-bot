import requests
from utils.settings_handler import settings


class Statistics:
    """
    Send data to https://github.com/MahjongRepository/mahjong-stat/ project
    """

    game_id = ""
    username = ""

    def send_start_game(self):
        url = settings.STAT_SERVER_URL
        if not url or not self.game_id:
            return False
        url = "{0}/api/v1/tenhou/game/start/".format(url)
        data = {"id": self.game_id, "username": self.username}
        result = requests.post(url, data, headers={"Token": settings.STAT_TOKEN}, timeout=5)
        return result.status_code == 200 and result.json()["success"]

    def send_end_game(self):
        url = settings.STAT_SERVER_URL
        if not url or not self.game_id:
            return False
        url = "{0}/api/v1/tenhou/game/finish/".format(url)
        data = {"id": self.game_id, "username": self.username}
        result = requests.post(url, data, headers={"Token": settings.STAT_TOKEN}, timeout=5)
        return result.status_code == 200 and result.json()["success"]

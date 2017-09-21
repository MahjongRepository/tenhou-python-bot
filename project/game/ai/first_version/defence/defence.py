# -*- coding: utf-8 -*-


class Defence(object):
    defence = None

    def __init__(self, defence_handler):
        self.defence = defence_handler
        self.player = self.defence.player
        self.table = self.defence.table

    def find_tiles_to_discard(self, players):
        """
        Each strategy will try to find "safe" tiles to discard
        for specified players
        :param players:
        :return: list of DefenceTile objects
        """
        raise NotImplemented()


class DefenceTile(object):
    # 100% safe tile
    SAFE = 0
    ALMOST_SAFE_TILE = 10
    DANGER = 200

    # how danger this tile is
    danger = None
    # in 34 tile format
    value = None

    def __init__(self, value, danger):
        self.value = value
        self.danger = danger

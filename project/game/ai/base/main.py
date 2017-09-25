# -*- coding: utf-8 -*-


class InterfaceAI(object):
    """
    Public interface of the bot AI
    """
    version = 'none'

    player = None
    table = None

    def __init__(self, player):
        self.player = player
        self.table = player.table

    def discard_tile(self):
        """
        Simple tile discard (after draw)
        :return: int, 136 tile format
        """
        raise NotImplemented()

    def init_state(self):
        """
        Method will be called after bot hand initialization
        :return:
        """

    def erase_state(self):
        """
        Method will be called in the start of new round.
        You can null here AI attributes that depends on round data
        :return:
        """

    def draw_tile(self, tile):
        """
        :param tile: 136 tile format
        :return:
        """

    def process_discard_option(self, discard_option, closed_hand):
        """
        :param discard_option: DiscardOption object
        :param closed_hand: list of 136 tiles format
        :return:
        """

    def should_call_riichi(self):
        """
        When bot in tempai this method will be run
        You can check additional params here to decide should be riichi called or not
        :return: boolean
        """
        return False

    def should_call_kan(self, tile, is_open_kan):
        """
        Method will decide should we call a kan or upgrade pon to kan (chankan)
        :param tile: 136 tile format
        :param is_open_kan: boolean
        :return: kan type (Meld.KAN, Meld.CHANKAN) or None
        """
        return False

    def try_to_call_meld(self, tile, is_kamicha_discard):
        """
        Determine should we call a meld or not.
        :param tile: 136 format tile
        :param is_kamicha_discard: boolean
        :return: Meld and DiscardOption objects or None, None
        """
        return None, None

    def enemy_called_riichi(self, enemy_seat):
        """
        Will be called after other player riichi
        """

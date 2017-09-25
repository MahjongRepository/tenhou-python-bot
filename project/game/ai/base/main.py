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

    def discard_tile(self, discard_tile):
        """
        AI should decide what tile had to be discarded from the hand on bot turn
        :param discard_tile: 136 tile format. Sometimes we want to discard specific tile
        :return: 136 tile format
        """
        raise NotImplemented()

    def init_hand(self):
        """
        Method will be called after bot hand initialization (when tiles will be set to the player)
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

    def should_call_win(self, tile, enemy_seat):
        """
        When we can call win by other player discard this method will be called
        :return: boolean
        """
        return True

    def should_call_riichi(self):
        """
        When bot can call riichi this method will be called.
        You can check additional params here to decide should be riichi called or not
        :return: boolean
        """
        return False

    def should_call_kan(self, tile, is_open_kan):
        """
        When bot can call kan or chankan this method will be called
        :param tile: 136 tile format
        :param is_open_kan: boolean
        :return: kan type (Meld.KAN, Meld.CHANKAN) or None
        """
        return False

    def try_to_call_meld(self, tile, is_kamicha_discard):
        """
        When bot can open hand with a set (chi or pon/kan) this method will be called
        :param tile: 136 format tile
        :param is_kamicha_discard: boolean
        :return: Meld and DiscardOption objects or None, None
        """
        return None, None

    def enemy_called_riichi(self, enemy_seat):
        """
        Will be called after other player riichi
        """

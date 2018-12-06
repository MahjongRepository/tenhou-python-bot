# -*- coding: utf-8 -*-


class Defence(object):
    class TileDanger(object):
        DANGER_GENBUTSU = 0

        # honor tiles
        DANGER_LAST_HONOR = 10
        DANGER_NON_YAKUHAI_HONOR_3_LEFT = 20
        DANGER_NON_YAKUHAI_HONOR_SHONPAI = 50
        DANGER_YAKUHAI_HONOR_3_LEFT = 50
        DANGER_DOUBLE_YAKUHAI_HONOR_3_LEFT = 100
        DANGER_YAKUHAI_HONOR_SHONPAI = 80
        DANGER_DOBULE_YAKUHAI_HONOR_SHONPAI = 160

        # kabe tiles
        DANGER_NON_SHONPAI_KABE = 10
        DANGER_SHONPAI_KABE = 50

        # suji tiles
        DANGER_19_NOT_SHONPAI_SUJI = 10
        DANGER_19_SHONPAI_SUJI = 20
        DANGER_SUJI = 30
        DANGER_456_SUJI_ON_RIICHI = 50
        DANGER_2378_SUJI_ON_RIICHI = 100

        # possible ryanmen waits
        DANGER_RYANMEN_BASE = 100
        DANGER_BONUS_SENKI_SUJI = 10
        DANGER_BONUS_URA_SUJI = 10
        DANGER_BONUS_MATAGI_SUJI = 20
        DANGER_BONUS_AIDAYONKEN = 20

        # doras
        DANGER_DORA_BONUS = 100
        DANGER_DORA_CONNECTOR_BONUS = 20

        # early discards
        DANGER_NEGATIVE_BONUS_19_EARLY_2378 = -20
        DANGER_NEGATIVE_BONUS_28_EARLY_37 = -10

        # count of possible forms
        DANGER_FORM_BONUS_RYANMEN = 5
        DANGER_FORM_BONUS_OTHER = 2

        # octaves counting, (n - DANGER_OCTAVE_BASE) *  DANGER_OCTAVE_MODIFIER
        DANGER_OCTAVE_BASE = 10
        DANGER_OCTAVE_MODIFIER = 5

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

    # how dangerous this tile is
    danger = None
    # in 34 tile format
    value = None

    def __init__(self, value, danger):
        self.value = value
        self.danger = danger

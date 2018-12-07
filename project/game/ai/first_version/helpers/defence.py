# -*- coding: utf-8 -*-


class TileDanger:
    GENBUTSU = {
        'value': 0,
        'description': 'Genbutsu'
    }
    IMPOSSIBLE_WAIT = {
        'value': 0,
        'description': 'Impossible wait'
    }

    # FIXME
    # change format for all remaining options

    # honor tiles
    LAST_HONOR = 10
    NON_YAKUHAI_HONOR_3_LEFT = 20
    NON_YAKUHAI_HONOR_SHONPAI = 50
    YAKUHAI_HONOR_3_LEFT = 50
    DOUBLE_YAKUHAI_HONOR_3_LEFT = 100
    YAKUHAI_HONOR_SHONPAI = 80
    DOBULE_YAKUHAI_HONOR_SHONPAI = 160

    # kabe tiles
    NON_SHONPAI_KABE = 10
    SHONPAI_KABE = 50

    # suji tiles
    SUJI_19_NOT_SHONPAI = 10
    SUJI_19_SHONPAI = 20
    SUJI = 30
    SUJI_456_ON_RIICHI = 50
    SUJI_2378_ON_RIICHI = 100

    # possible ryanmen waits
    RYANMEN_BASE = 100
    BONUS_SENKI_SUJI = 10
    BONUS_URA_SUJI = 10
    BONUS_MATAGI_SUJI = 20
    BONUS_AIDAYONKEN = 20

    # doras
    DORA_BONUS = 100
    DORA_CONNECTOR_BONUS = 20

    # early discards
    NEGATIVE_BONUS_19_EARLY_2378 = -20
    NEGATIVE_BONUS_28_EARLY_37 = -10

    # count of possible forms
    FORM_BONUS_RYANMEN = 5
    FORM_BONUS_OTHER = 2

    # octaves counting, (n - OCTAVE_BASE) *  OCTAVE_MODIFIER
    OCTAVE_BASE = 10
    OCTAVE_MODIFIER = 5


class DefenceHandler:
    """
    Place to keep information of tile danger level for each player
    """
    values = None

    def __init__(self):
        """
        1, 2, 3 is our opponents seats
        """
        self.values = {
            1: [],
            2: [],
            3: []
        }

    def __unicode__(self):
        return self.values

    def set_danger(self, player, danger):
        self.values[player].append(danger)

    def get_danger_total(self, player):
        return sum([x['value'] for x in self.values[player]])

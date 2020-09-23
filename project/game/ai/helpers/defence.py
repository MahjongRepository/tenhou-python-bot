class TileDanger:
    IMPOSSIBLE_WAIT = {
        "value": 0,
        "description": "Impossible wait",
    }

    # honor tiles
    HONOR_THIRD = {
        "value": 10,
        "description": "Third honor tile",
    }
    NON_YAKUHAI_HONOR_SECOND = {
        "value": 20,
        "description": "Second non-yakuhai honor",
    }
    NON_YAKUHAI_HONOR_SHONPAI = {
        "value": 50,
        "description": "Shonpai non-yakuhai honor",
    }
    YAKUHAI_HONOR_SECOND = {
        "value": 50,
        "description": "Second yakuhai honor",
    }
    DOUBLE_YAKUHAI_HONOR_SECOND = {
        "value": 100,
        "description": "Second double-yakuhai honor",
    }
    YAKUHAI_HONOR_SHONPAI = {
        "value": 80,
        "description": "Shonpai yakuhai honor",
    }
    DOUBLE_YAKUHAI_HONOR_SHONPAI = {
        "value": 160,
        "description": "Shonpai double-yakuhai honor",
    }

    # kabe tiles
    NON_SHONPAI_KABE = {
        "value": 10,
        "description": "Non-shonpai strong kabe tile",
    }
    SHONPAI_KABE = {
        "value": 50,
        "description": "Shonpai string kabe tile",
    }

    # suji tiles
    SUJI_19_NOT_SHONPAI = {
        "value": 10,
        "description": "Non-shonpai 1 or 9 with suji",
    }
    SUJI_19_SHONPAI = {
        "value": 20,
        "description": "Shonpai 1 or 9 with suji",
    }
    SUJI = {
        "value": 30,
        "description": "Default suji",
    }
    SUJI_2378_ON_RIICHI = {
        "value": 100,
        "description": "Suji on 2, 3, 7 or 8 on riichi declaration",
    }

    # possible ryanmen waits
    RYANMEN_BASE = {
        "value": 100,
        "description": "Base danger for possible ryanmen wait",
    }
    BONUS_SENKI_SUJI = {
        "value": 10,
        "description": "Additional danger for senki-suji pattern",
    }
    BONUS_URA_SUJI = {
        "value": 10,
        "description": "Additional danger for ura-suji pattern",
    }
    BONUS_MATAGI_SUJI = {
        "value": 20,
        "description": "Additinal danger for matagi-suji pattern",
    }
    BONUS_AIDAYONKEN = {
        "value": 20,
        "description": "Additional danger for aidayonken pattern",
    }

    # doras
    DORA_BONUS = {
        "value": 100,
        "description": "Additional danger for tile being a dora",
    }
    DORA_CONNECTOR_BONUS = {
        "value": 20,
        "description": "Additional danger for tile being dora connector",
    }

    # early discards - these are considered only if ryanmen is possible
    NEGATIVE_BONUS_19_EARLY_2378 = {
        "value": -20,
        "description": "Subtracted danger for 1 or 9 because of early 2, 3, 7 or 8 discard",
    }
    NEGATIVE_BONUS_28_EARLY_37 = {
        "value": -10,
        "description": "Subtracted danger for 2 or 8 because of early 3 or 7 discard",
    }

    ###############
    # The following constants don't follow the logic of other constants, so they are not dictionaries
    ##############

    # count of possible forms
    FORM_BONUS_DESCRIPTION = "Forms bonus"
    FORM_BONUS_KANCHAN = 2
    FORM_BONUS_PENCHAN = 2
    FORM_BONUS_SYANPON = 8
    FORM_BONUS_TANKI = 8
    FORM_BONUS_RYANMEN = 5

    # octaves counting, (n - OCTAVE_BASE) *  OCTAVE_MODIFIER
    OCTAVE_BASE = 10
    OCTAVE_MODIFIER = 5


class EnemyDanger:
    THREAT_RIICHI = {
        "id": "threatening_riichi",
        "description": "Enemy called riichi",
    }
    THREAT_OPEN_HAND_AND_MULTIPLE_DORA = {
        "id": "threatening_open_hand_dora",
        "description": "Enemy opened hand with 3+ dora and now is 6+ step",
    }
    THREAT_HONITSU = {
        "id": "threatening_honitsu",
        "description": "Enemy hand looks like honitsu",
    }
    THREAT_EXPENSIVE_OPEN_HAND = {
        "id": "threatening_honitsu",
        "description": "Enemy opened hand has 3+ han",
    }


class TileDangerHandler:
    """
    Place to keep information of tile danger level for each player
    """

    values = None

    def __init__(self):
        """
        1, 2, 3 is our opponents seats
        """
        self.values = {1: [], 2: [], 3: []}

    def __unicode__(self):
        return self.values

    def set_danger(self, player_seat, danger):
        self.values[player_seat].append(danger)

    def get_danger_reasons(self, player_seat):
        return self.values[player_seat]

    def get_total_danger(self, player_seat):
        safe = [x for x in self.values[player_seat] if x["description"] == TileDanger.IMPOSSIBLE_WAIT["description"]]

        # no matter what other metrics says, this tile is safe
        if safe:
            return 0

        return sum([x["value"] for x in self.values[player_seat]])

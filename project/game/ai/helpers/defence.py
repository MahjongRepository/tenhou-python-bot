from typing import Optional


class TileDanger:
    IMPOSSIBLE_WAIT = {
        "value": 0,
        "description": "Impossible wait",
    }
    SAFE_AGAINST_THREATENING_HAND = {
        "value": 0,
        "description": "Tile can't be used by analyzed threat",
    }

    # honor tiles
    HONOR_THIRD = {
        "value": 40,
        "description": "Third honor tile",
    }
    NON_YAKUHAI_HONOR_SECOND = {
        "value": 80,
        "description": "Second non-yakuhai honor",
    }
    NON_YAKUHAI_HONOR_SHONPAI = {
        "value": 160,
        "description": "Shonpai non-yakuhai honor",
    }
    YAKUHAI_HONOR_SECOND = {
        "value": 120,
        "description": "Second yakuhai honor",
    }
    DOUBLE_YAKUHAI_HONOR_SECOND = {
        "value": 200,
        "description": "Second double-yakuhai honor",
    }
    YAKUHAI_HONOR_SHONPAI = {
        "value": 240,
        "description": "Shonpai yakuhai honor",
    }
    DOUBLE_YAKUHAI_HONOR_SHONPAI = {
        "value": 480,
        "description": "Shonpai double-yakuhai honor",
    }

    # kabe tiles
    NON_SHONPAI_KABE = {
        "value": 40,
        "description": "Non-shonpai strong kabe tile",
    }
    SHONPAI_KABE = {
        "value": 200,
        "description": "Shonpai string kabe tile",
    }

    # suji tiles
    SUJI_19_NOT_SHONPAI = {
        "value": 40,
        "description": "Non-shonpai 1 or 9 with suji",
    }
    SUJI_19_SHONPAI = {
        "value": 80,
        "description": "Shonpai 1 or 9 with suji",
    }
    SUJI = {
        "value": 120,
        "description": "Default suji",
    }
    SUJI_2378_ON_RIICHI = {
        "value": 400,
        "description": "Suji on 2, 3, 7 or 8 on riichi declaration",
    }

    # possible ryanmen waits
    RYANMEN_BASE = {
        "value": 400,
        "description": "Base danger for possible ryanmen wait",
    }
    BONUS_SENKI_SUJI = {
        "value": 40,
        "description": "Additional danger for senki-suji pattern",
    }
    BONUS_URA_SUJI = {
        "value": 40,
        "description": "Additional danger for ura-suji pattern",
    }
    BONUS_MATAGI_SUJI = {
        "value": 80,
        "description": "Additinal danger for matagi-suji pattern",
    }
    BONUS_AIDAYONKEN = {
        "value": 80,
        "description": "Additional danger for aidayonken pattern",
    }

    # doras
    DORA_BONUS = {
        "value": 200,
        "description": "Additional danger for tile being a dora",
    }
    DORA_CONNECTOR_BONUS = {
        "value": 80,
        "description": "Additional danger for tile being dora connector",
    }

    # early discards - these are considered only if ryanmen is possible
    NEGATIVE_BONUS_19_EARLY_2378 = {
        "value": -80,
        "description": "Subtracted danger for 1 or 9 because of early 2, 3, 7 or 8 discard",
    }
    NEGATIVE_BONUS_28_EARLY_37 = {
        "value": -40,
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

    # suji counting, (SUJI_COUNT_BOUNDARY - n) *  SUJI_COUNT_MODIFIER
    # We count how many ryanmen waits are still possible. Maximum n is 18, minimum is 1.
    # If there are many possible ryanmens left, we consider situation less dangerous
    # than if there are few possible ryanmens left.
    # If n is 0, we don't consider this as a factor at all, because that means that wait is not ryanmen.
    # Actually that should mean that non-ryanmen waits are now much more dangerous that before.
    SUJI_COUNT_BOUNDARY = 10
    SUJI_COUNT_MODIFIER = 20

    # acceptable danger bases
    DANGER_BORDER_EXTREME = 1200
    DANGER_BORDER_VERY_HIGH = 1000
    DANGER_BORDER_HIGH = 800
    DANGER_BORDER_UPPER_MEDIUM = 700
    DANGER_BORDER_MEDIUM = 600
    DANGER_BORDER_LOWER_MEDIUM = 500
    DANGER_BORDER_UPPER_LOW = 400
    DANGER_BORDER_LOW = 300
    DANGER_BORDER_VERY_LOW = 200
    DANGER_BORDER_EXTREMELY_LOW = 120
    DANGER_BORDER_LOWEST = 80
    DANGER_BORDER_BETAORI = 0

    DEFAULT_DANGER_BORDER = DANGER_BORDER_BETAORI
    IGNORE_DANGER = 1000000


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

    values: dict
    weighted_cost: Optional[int]
    danger_border: dict

    def __init__(self):
        """
        1, 2, 3 is our opponents seats
        """
        self.values = {1: [], 2: [], 3: []}
        self.weighted_cost = 0
        self.danger_border = {1: {}, 2: {}, 3: {}}

    def set_danger(self, player_seat, danger):
        self.values[player_seat].append(danger)

    def set_danger_border(self, player_seat, danger_border: int, our_hand_cost: int):
        self.danger_border[player_seat] = {"border": danger_border, "our_hand_cost": our_hand_cost}

    def get_danger_reasons(self, player_seat):
        return self.values[player_seat]

    def get_danger_border(self, player_seat):
        return self.danger_border[player_seat]

    def get_total_danger_for_player(self, player_seat):
        return sum([x["value"] for x in self.values[player_seat]])

    def get_max_danger(self):
        return max(
            [
                self.get_total_danger_for_player(1),
                self.get_total_danger_for_player(2),
                self.get_total_danger_for_player(3),
            ]
        )

    def get_min_danger_border(self):
        borders = []
        if self.get_danger_border(1).get("border"):
            borders.append(self.get_danger_border(1).get("border"))
        if self.get_danger_border(2).get("border"):
            borders.append(self.get_danger_border(2).get("border"))
        if self.get_danger_border(3).get("border"):
            borders.append(self.get_danger_border(3).get("border"))
        return borders and min(borders) or 0

    def clear_danger(self, player_seat):
        self.values[player_seat] = []
        self.danger_border[player_seat] = {}

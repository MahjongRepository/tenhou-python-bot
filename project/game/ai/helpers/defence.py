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
    NON_SHONPAI_KABE_STRONG = {
        "value": 40,
        "description": "Non-shonpai strong kabe tile",
    }
    SHONPAI_KABE_STRONG = {
        "value": 200,
        "description": "Shonpai strong kabe tile",
    }
    NON_SHONPAI_KABE_WEAK = {
        "value": 80,
        "description": "Non-shonpai weak kabe tile",
    }
    # weak shonpai kabe is actually less suspicious then a strong one
    SHONPAI_KABE_WEAK = {
        "value": 120,
        "description": "Shonpai weak kabe tile",
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
        "value": 300,
        "description": "Suji on 2, 3, 7 or 8 on riichi declaration",
    }

    # possible ryanmen waits
    RYANMEN_BASE_SINGLE = {
        "value": 300,
        "description": "Base danger for possible wait in a single ryanmen",
    }
    RYANMEN_BASE_DOUBLE = {
        "value": 500,
        "description": "Base danger for possible wait in two ryanmens",
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
    FORM_BONUS_KANCHAN = 3
    FORM_BONUS_PENCHAN = 3
    FORM_BONUS_SYANPON = 12
    FORM_BONUS_TANKI = 12
    FORM_BONUS_RYANMEN = 8

    # suji counting, (SUJI_COUNT_BOUNDARY - n) *  SUJI_COUNT_MODIFIER
    # We count how many ryanmen waits are still possible. Maximum n is 18, minimum is 1.
    # If there are many possible ryanmens left, we consider situation less dangerous
    # than if there are few possible ryanmens left.
    # If n is 0, we don't consider this as a factor at all, because that means that wait is not ryanmen.
    # Actually that should mean that non-ryanmen waits are now much more dangerous that before.
    SUJI_COUNT_BOUNDARY = 10
    SUJI_COUNT_MODIFIER = 20

    # borders indicating late round
    ALMOST_LATE_ROUND = 10
    LATE_ROUND = 12
    VERY_LATE_ROUND = 16


class DangerBorder:
    IGNORE = 1000000
    EXTREME = 1200
    VERY_HIGH = 1000
    HIGH = 800
    UPPER_MEDIUM = 700
    MEDIUM = 600
    LOWER_MEDIUM = 500
    UPPER_LOW = 400
    LOW = 300
    VERY_LOW = 200
    EXTREMELY_LOW = 120
    LOWEST = 80
    BETAORI = 0

    one_step_down_dict = dict(
        {
            IGNORE: EXTREME,
            EXTREME: VERY_HIGH,
            VERY_HIGH: HIGH,
            HIGH: UPPER_MEDIUM,
            UPPER_MEDIUM: MEDIUM,
            MEDIUM: LOWER_MEDIUM,
            LOWER_MEDIUM: UPPER_LOW,
            UPPER_LOW: LOW,
            LOW: VERY_LOW,
            VERY_LOW: EXTREMELY_LOW,
            EXTREMELY_LOW: LOWEST,
            LOWEST: BETAORI,
            BETAORI: BETAORI,
        }
    )

    late_danger_dict = dict(
        {
            IGNORE: IGNORE,
            EXTREME: VERY_HIGH,
            VERY_HIGH: HIGH,
            HIGH: UPPER_MEDIUM,
            UPPER_MEDIUM: MEDIUM,
            MEDIUM: LOWER_MEDIUM,
            LOWER_MEDIUM: UPPER_LOW,
            UPPER_LOW: LOW,
            LOW: VERY_LOW,
            VERY_LOW: EXTREMELY_LOW,
            EXTREMELY_LOW: LOWEST,
            LOWEST: BETAORI,
            BETAORI: BETAORI,
        }
    )

    very_late_danger_dict = dict(
        {
            IGNORE: VERY_HIGH,
            EXTREME: HIGH,
            VERY_HIGH: UPPER_MEDIUM,
            HIGH: MEDIUM,
            UPPER_MEDIUM: LOWER_MEDIUM,
            MEDIUM: UPPER_LOW,
            LOWER_MEDIUM: LOW,
            UPPER_LOW: VERY_LOW,
            LOW: EXTREMELY_LOW,
            VERY_LOW: LOWEST,
            EXTREMELY_LOW: BETAORI,
            LOWEST: BETAORI,
            BETAORI: BETAORI,
        }
    )

    @staticmethod
    def tune_down(danger_border, steps):
        for _ in range(steps):
            danger_border = DangerBorder.one_step_down_dict[danger_border]

        return danger_border

    @staticmethod
    def tune_for_round(player, danger_border, shanten):
        danger_border_dict = None

        if shanten == 0 or shanten == 1:
            if len(player.discards) > TileDanger.LATE_ROUND:
                danger_border_dict = DangerBorder.late_danger_dict
            if len(player.discards) > TileDanger.VERY_LATE_ROUND:
                danger_border_dict = DangerBorder.very_late_danger_dict
        elif shanten == 2:
            if len(player.discards) > TileDanger.ALMOST_LATE_ROUND:
                danger_border_dict = DangerBorder.late_danger_dict
            if len(player.discards) > TileDanger.LATE_ROUND:
                return DangerBorder.BETAORI

        if not danger_border_dict:
            return danger_border

        return danger_border_dict[danger_border]


class EnemyDanger:
    THREAT_RIICHI = {
        "id": "threatening_riichi",
        "description": "Enemy called riichi",
    }
    THREAT_OPEN_HAND_AND_MULTIPLE_DORA = {
        "id": "threatening_open_hand_dora",
        "description": "Enemy opened hand with 3+ dora and now is 6+ step",
    }
    THREAT_EXPENSIVE_OPEN_HAND = {
        "id": "threatening_3_han_meld",
        "description": "Enemy opened hand has 3+ han",
    }
    THREAT_LATE_ROUND = {
        "id": "threatening_late_round",
        "description": "Enemy could be in tempai",
    }

    LATE_ROUND_BORDER = 12
    LATE_ROUND_HAND_COST = 2000


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

    def get_sum_danger(self):
        return sum(
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

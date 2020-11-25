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
        "description": "Third honor tile (early game)",
    }

    NON_YAKUHAI_HONOR_SECOND_EARLY = {
        "value": 60,
        "description": "Second non-yakuhai honor (early game)",
    }
    NON_YAKUHAI_HONOR_SHONPAI_EARLY = {
        "value": 120,
        "description": "Shonpai non-yakuhai honor (early game)",
    }
    YAKUHAI_HONOR_SECOND_EARLY = {
        "value": 80,
        "description": "Second yakuhai honor (early game)",
    }
    YAKUHAI_HONOR_SHONPAI_EARLY = {
        "value": 160,
        "description": "Shonpai yakuhai honor (early game)",
    }
    DOUBLE_YAKUHAI_HONOR_SECOND_EARLY = {
        "value": 120,
        "description": "Second double-yakuhai honor (early game)",
    }
    DOUBLE_YAKUHAI_HONOR_SHONPAI_EARLY = {
        "value": 240,
        "description": "Shonpai double-yakuhai honor (early game)",
    }

    NON_YAKUHAI_HONOR_SECOND_MID = {
        "value": 80,
        "description": "Second non-yakuhai honor (mid game)",
    }
    NON_YAKUHAI_HONOR_SHONPAI_MID = {
        "value": 160,
        "description": "Shonpai non-yakuhai honor (mid game)",
    }
    YAKUHAI_HONOR_SECOND_MID = {
        "value": 120,
        "description": "Second yakuhai honor (mid game)",
    }
    DOUBLE_YAKUHAI_HONOR_SECOND_MID = {
        "value": 200,
        "description": "Second double-yakuhai honor (mid game)",
    }
    YAKUHAI_HONOR_SHONPAI_MID = {
        "value": 240,
        "description": "Shonpai yakuhai honor (mid game)",
    }
    DOUBLE_YAKUHAI_HONOR_SHONPAI_MID = {
        "value": 480,
        "description": "Shonpai double-yakuhai honor (mid game)",
    }

    NON_YAKUHAI_HONOR_SECOND_LATE = {
        "value": 160,
        "description": "Second non-yakuhai honor (late game)",
    }
    NON_YAKUHAI_HONOR_SHONPAI_LATE = {
        "value": 240,
        "description": "Shonpai non-yakuhai honor (late game)",
    }
    YAKUHAI_HONOR_SECOND_LATE = {
        "value": 200,
        "description": "Second yakuhai honor (late game)",
    }
    DOUBLE_YAKUHAI_HONOR_SECOND_LATE = {
        "value": 300,
        "description": "Second double-yakuhai honor (late game)",
    }
    YAKUHAI_HONOR_SHONPAI_LATE = {
        "value": 400,
        "description": "Shonpai yakuhai honor (late game)",
    }
    DOUBLE_YAKUHAI_HONOR_SHONPAI_LATE = {
        "value": 600,
        "description": "Shonpai double-yakuhai honor (late game)",
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

    NON_SHONPAI_KABE_STRONG_OPEN_HAND = {
        "value": 60,
        "description": "Non-shonpai strong kabe tile (against open hand)",
    }
    SHONPAI_KABE_STRONG_OPEN_HAND = {
        "value": 300,
        "description": "Shonpai strong kabe tile (against open hand)",
    }
    NON_SHONPAI_KABE_WEAK_OPEN_HAND = {
        "value": 120,
        "description": "Non-shonpai weak kabe tile (against open hand)",
    }
    SHONPAI_KABE_WEAK_OPEN_HAND = {
        "value": 200,
        "description": "Shonpai weak kabe tile (against open hand)",
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
    SUJI_28_ON_RIICHI = {
        "value": 300,
        "description": "Suji on 2 or 8 on riichi declaration",
    }
    SUJI_37_ON_RIICHI = {
        "value": 400,
        "description": "Suji on 3 or 7 on riichi declaration",
    }

    SUJI_19_NOT_SHONPAI_OPEN_HAND = {
        "value": 100,
        "description": "Non-shonpai 1 or 9 with suji (against open hand)",
    }
    SUJI_19_SHONPAI_OPEN_HAND = {
        "value": 200,
        "description": "Shonpai 1 or 9 with suji (against open hand)",
    }
    SUJI_OPEN_HAND = {
        "value": 160,
        "description": "Default suji (against open hand)",
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

    # bonus dangers for possible ryanmen waits
    BONUS_MATAGI_SUJI = {
        "value": 80,
        "description": "Additional danger for matagi-suji pattern",
    }
    BONUS_AIDAYONKEN = {
        "value": 80,
        "description": "Additional danger for aidayonken pattern",
    }
    BONUS_EARLY_5 = {
        "value": 80,
        "description": "Additional danger for 1 and 9 in case of early 5 discarded in that suit",
    }
    BONUS_EARLY_28 = {
        "value": -80,
        "description": "Negative danger for 19 after early 28",
    }
    BONUS_EARLY_37 = {
        "value": -60,
        "description": "Negative danger for 1289 after early 37",
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

    # bonus danger for different yaku
    # they may add up
    HONITSU_THIRD_HONOR_BONUS_DANGER = {
        "value": 80,
        "description": "Additional danger for third honor against honitsu hands",
    }
    HONITSU_SECOND_HONOR_BONUS_DANGER = {
        "value": 160,
        "description": "Additional danger for second honor against honitsu hands",
    }
    HONITSU_SHONPAI_HONOR_BONUS_DANGER = {
        "value": 280,
        "description": "Additional danger for shonpai honor against honitsu hands",
    }

    TOITOI_SECOND_YAKUHAI_HONOR_BONUS_DANGER = {
        "value": 120,
        "description": "Additional danger for second honor against honitsu hands",
    }
    TOITOI_SHONPAI_NON_YAKUHAI_BONUS_DANGER = {
        "value": 160,
        "description": "Additional danger for non-yakuhai shonpai tiles agains toitoi hands",
    }
    TOITOI_SHONPAI_YAKUHAI_BONUS_DANGER = {
        "value": 240,
        "description": "Additional danger for shonpai yakuhai against toitoi hands",
    }
    TOITOI_SHONPAI_DORA_BONUS_DANGER = {
        "value": 240,
        "description": "Additional danger for shonpai dora tiles agains toitoi hands",
    }

    ATODZUKE_YAKUHAI_HONOR_BONUS_DANGER = {
        "value": 400,
        "description": "Bonus danger yakuhai tiles for atodzuke yakuhai hands",
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
    VERY_LATE_ROUND = 15

    @staticmethod
    def make_unverified_suji_coeff(value):
        return {"value": value, "description": "Additional bonus for number of unverified suji"}

    @staticmethod
    def is_safe(danger):
        return danger == TileDanger.IMPOSSIBLE_WAIT or danger == TileDanger.SAFE_AGAINST_THREATENING_HAND


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

    one_step_up_dict = dict(
        {
            IGNORE: IGNORE,
            EXTREME: IGNORE,
            VERY_HIGH: EXTREME,
            HIGH: VERY_HIGH,
            UPPER_MEDIUM: HIGH,
            MEDIUM: UPPER_MEDIUM,
            LOWER_MEDIUM: MEDIUM,
            UPPER_LOW: LOWER_MEDIUM,
            LOW: UPPER_LOW,
            VERY_LOW: LOW,
            EXTREMELY_LOW: VERY_LOW,
            LOWEST: EXTREMELY_LOW,
            # betaori means betaori, don't tune it up
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
        assert steps >= 0
        for _ in range(steps):
            danger_border = DangerBorder.one_step_down_dict[danger_border]

        return danger_border

    @staticmethod
    def tune_up(danger_border, steps):
        assert steps >= 0
        for _ in range(steps):
            danger_border = DangerBorder.one_step_up_dict[danger_border]

        return danger_border

    @staticmethod
    def tune(danger_border, value):
        if value > 0:
            return DangerBorder.tune_up(danger_border, value)
        elif value < 0:
            return DangerBorder.tune_down(danger_border, abs(value))

        return danger_border

    @staticmethod
    def tune_for_round(player, danger_border, shanten):
        danger_border_dict = None

        if shanten == 0:
            if len(player.discards) > TileDanger.LATE_ROUND:
                danger_border_dict = DangerBorder.late_danger_dict
            if len(player.discards) > TileDanger.VERY_LATE_ROUND:
                danger_border_dict = DangerBorder.very_late_danger_dict
        elif shanten == 1:
            if len(player.discards) > TileDanger.LATE_ROUND:
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
    THREAT_OPEN_HAND_UNKNOWN_COST = {
        "id": "threatening_melds",
        "description": "Enemy opened hand and we are not sure if it's expensive",
    }


class TileDangerHandler:
    """
    Place to keep information of tile danger level for each player
    """

    values: dict
    weighted_cost: Optional[int]
    danger_border: dict
    can_be_used_for_ryanmen: bool

    # if we estimate that one's threat cost is less than COST_PERCENT_THRESHOLD of other's
    # we ignore it when choosing tile for fold
    COST_PERCENT_THRESHOLD = 40

    def __init__(self):
        """
        1, 2, 3 is our opponents seats
        """
        self.values = {1: [], 2: [], 3: []}
        self.weighted_cost = 0
        self.danger_border = {1: {}, 2: {}, 3: {}}
        self.can_be_used_for_ryanmen: bool = False

    def set_danger(self, player_seat, danger):
        self.values[player_seat].append(danger)

    def set_danger_border(self, player_seat, danger_border: int, our_hand_cost: int, enemy_hand_cost: int):
        self.danger_border[player_seat] = {
            "border": danger_border,
            "our_hand_cost": our_hand_cost,
            "enemy_hand_cost": enemy_hand_cost,
        }

    def get_danger_reasons(self, player_seat):
        return self.values[player_seat]

    def get_danger_border(self, player_seat):
        return self.danger_border[player_seat]

    def get_total_danger_for_player(self, player_seat):
        total = sum([x["value"] for x in self.values[player_seat]])
        assert total >= 0
        return total

    def get_max_danger(self):
        return max(self._danger_array)

    def get_sum_danger(self):
        return sum(self._danger_array)

    def get_weighted_danger(self):
        costs = [
            self.get_danger_border(1).get("enemy_hand_cost") or 0,
            self.get_danger_border(2).get("enemy_hand_cost") or 0,
            self.get_danger_border(3).get("enemy_hand_cost") or 0,
        ]
        max_cost = max(costs)
        if max_cost == 0:
            return 0

        dangers = self._danger_array

        weighted = 0
        num_dangers = 0

        for cost, danger in zip(costs, dangers):
            if cost * 100 / max_cost >= self.COST_PERCENT_THRESHOLD:
                # divide by 8000 so it's more human-readable
                weighted += cost * danger / 8000
                num_dangers += 1

        assert num_dangers > 0

        # this way we balance out tiles that are kinda safe against all the threats
        # and tiles that are genbutsu against one threat and are dangerours against the other
        if num_dangers == 1:
            danger_multiplier = 1
        else:
            danger_multiplier = 0.8

        weighted *= danger_multiplier

        return weighted

    def get_min_danger_border(self):
        return min(self._borders_array)

    def clear_danger(self, player_seat):
        self.values[player_seat] = []
        self.danger_border[player_seat] = {}

    def is_danger_acceptable(self):
        for border, danger in zip(self._borders_array, self._danger_array):
            if border < danger:
                return False

        return True

    @property
    def _danger_array(self):
        return [
            self.get_total_danger_for_player(1),
            self.get_total_danger_for_player(2),
            self.get_total_danger_for_player(3),
        ]

    @property
    def _borders_array(self):
        return [
            self.get_danger_border(1).get("border") or 0,
            self.get_danger_border(2).get("border") or 0,
            self.get_danger_border(3).get("border") or 0,
        ]

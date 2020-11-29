from game.ai.helpers.defence import TileDangerHandler
from game.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor, is_man, is_pin, is_sou, plus_dora, simplify


class DiscardOption:
    DORA_VALUE = 10000
    DORA_FIRST_NEIGHBOUR = 1000
    DORA_SECOND_NEIGHBOUR = 100

    UKEIRE_FIRST_FILTER_PERCENTAGE = 20
    UKEIRE_SECOND_FILTER_PERCENTAGE = 25
    UKEIRE_DANGER_FILTER_PERCENTAGE = 10

    MIN_UKEIRE_DANGER_BORDER = 2
    MIN_UKEIRE_TEMPAI_BORDER = 2
    MIN_UKEIRE_SHANTEN_1_BORDER = 4
    MIN_UKEIRE_SHANTEN_2_BORDER = 8

    player = None

    # in 136 tile format
    tile_to_discard_136 = None
    # are we calling riichi on this tile or not
    with_riichi = None
    # array of tiles that will improve our hand
    waiting = None
    # how much tiles will improve our hand
    ukeire = None
    ukeire_second = None
    # number of shanten for that tile
    shanten = None
    # sometimes we had to force tile to be discarded
    had_to_be_discarded = False
    # special cases where we had to save tile in hand (usually for atodzuke opened hand)
    had_to_be_saved = False
    # calculated tile value, for sorting
    valuation = None
    # how danger this tile is
    danger = None
    # wait to ukeire map
    wait_to_ukeire = None
    # second level cost approximation for 1-shanten hands
    second_level_cost = None
    # second level average number of waits approximation for 1-shanten hands
    average_second_level_waits = None
    # second level average cost approximation for 1-shanten hands
    average_second_level_cost = None
    # special descriptor for tempai with additional info
    tempai_descriptor = None

    def __init__(self, player, tile_to_discard_136, shanten, waiting, ukeire, wait_to_ukeire=None):
        self.player = player
        self.tile_to_discard_136 = tile_to_discard_136
        self.with_riichi = False
        self.shanten = shanten
        self.waiting = waiting
        self.ukeire = ukeire
        self.ukeire_second = 0
        self.count_of_dora = 0
        self.danger = TileDangerHandler()
        self.had_to_be_saved = False
        self.had_to_be_discarded = False
        self.wait_to_ukeire = wait_to_ukeire
        self.second_level_cost = 0
        self.average_second_level_waits = 0
        self.average_second_level_cost = 0
        self.tempai_descriptor = None

        self.calculate_valuation()

    @property
    def tile_to_discard_34(self):
        return self.tile_to_discard_136 // 4

    def serialize(self):
        data = {
            "tile": TilesConverter.to_one_line_string(
                [self.tile_to_discard_136], print_aka_dora=self.player.table.has_aka_dora
            ),
            "shanten": self.shanten,
            "ukeire": self.ukeire,
            "valuation": self.valuation,
            "danger": {
                "max_danger": self.danger.get_max_danger(),
                "sum_danger": self.danger.get_sum_danger(),
                "weighted_danger": self.danger.get_weighted_danger(),
                "min_border": self.danger.get_min_danger_border(),
                "danger_border": self.danger.danger_border,
                "weighted_cost": self.danger.weighted_cost,
                "danger_reasons": self.danger.values,
                "can_be_used_for_ryanmen": self.danger.can_be_used_for_ryanmen,
            },
        }
        if self.shanten == 0:
            data["with_riichi"] = self.with_riichi
        if self.ukeire_second:
            data["ukeire2"] = self.ukeire_second
        if self.average_second_level_waits:
            data["average_second_level_waits"] = self.average_second_level_waits
        if self.average_second_level_cost:
            data["average_second_level_cost"] = self.average_second_level_cost
        if self.had_to_be_saved:
            data["had_to_be_saved"] = self.had_to_be_saved
        if self.had_to_be_discarded:
            data["had_to_be_discarded"] = self.had_to_be_discarded
        return data

    def calculate_valuation(self):
        # base is 100 for ability to mark tiles as not needed (like set value to 50)
        value = 100
        honored_value = 20

        if is_honor(self.tile_to_discard_34):
            if self.tile_to_discard_34 in self.player.valued_honors:
                count_of_winds = [x for x in self.player.valued_honors if x == self.tile_to_discard_34]
                # for west-west, east-east we had to double tile value
                value += honored_value * len(count_of_winds)
        else:
            # aim for tanyao
            if self.player.ai.current_strategy and self.player.ai.current_strategy.type == BaseStrategy.TANYAO:
                suit_tile_grades = [10, 20, 30, 50, 40, 50, 30, 20, 10]
            # usual hand
            else:
                suit_tile_grades = [10, 20, 40, 50, 30, 50, 40, 20, 10]

            simplified_tile = simplify(self.tile_to_discard_34)
            value += suit_tile_grades[simplified_tile]

            for indicator in self.player.table.dora_indicators:
                indicator_34 = indicator // 4
                if is_honor(indicator_34):
                    continue

                # indicator and tile not from the same suit
                if is_sou(indicator_34) and not is_sou(self.tile_to_discard_34):
                    continue

                # indicator and tile not from the same suit
                if is_man(indicator_34) and not is_man(self.tile_to_discard_34):
                    continue

                # indicator and tile not from the same suit
                if is_pin(indicator_34) and not is_pin(self.tile_to_discard_34):
                    continue

                simplified_indicator = simplify(indicator_34)
                simplified_dora = simplified_indicator + 1
                # indicator is 9 man
                if simplified_dora == 9:
                    simplified_dora = 0

                # tile so close to the dora
                if simplified_tile + 1 == simplified_dora or simplified_tile - 1 == simplified_dora:
                    value += DiscardOption.DORA_FIRST_NEIGHBOUR

                # tile not far away from dora
                if simplified_tile + 2 == simplified_dora or simplified_tile - 2 == simplified_dora:
                    value += DiscardOption.DORA_SECOND_NEIGHBOUR

        count_of_dora = plus_dora(
            self.tile_to_discard_136, self.player.table.dora_indicators, add_aka_dora=self.player.table.has_aka_dora
        )

        self.count_of_dora = count_of_dora
        value += count_of_dora * DiscardOption.DORA_VALUE

        if is_honor(self.tile_to_discard_34):
            # depends on how much honor tiles were discarded
            # we will decrease tile value
            discard_percentage = [100, 75, 20, 0, 0]
            discarded_tiles = self.player.table.revealed_tiles[self.tile_to_discard_34]

            value = (value * discard_percentage[discarded_tiles]) / 100

            # three honor tiles were discarded,
            # so we don't need this tile anymore
            if value == 0:
                self.had_to_be_discarded = True

        self.valuation = int(value)

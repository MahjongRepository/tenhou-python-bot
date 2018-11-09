import copy

from mahjong.constants import AKA_DORA_LIST
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter
from mahjong.utils import is_tile_strictly_isolated, is_pair

import utils.decisions_constants as log
from game.ai.discard import DiscardOption
from utils.decisions_logger import DecisionsLogger


class HandBuilder:
    player = None
    ai = None

    def __init__(self, player, ai):
        self.player = player
        self.ai = ai

    def discard_tile(self, tiles, closed_hand, open_sets_34, print_log=True):
        selected_tile = self.choose_tile_to_discard(
            tiles,
            closed_hand,
            open_sets_34,
            print_log=print_log
        )

        # bot think that there is a threat on the table
        # and better to fold
        # if we can't find safe tiles, let's continue to build our hand
        if self.ai.defence.should_go_to_defence_mode(selected_tile):
            if not self.ai.in_defence:
                DecisionsLogger.debug(log.DEFENCE_ACTIVATE)
                self.ai.in_defence = True

            defence_tile = self.ai.defence.try_to_find_safe_tile_to_discard()
            if defence_tile:
                return self.process_discard_option(defence_tile, closed_hand)
        else:
            if self.ai.in_defence:
                DecisionsLogger.debug(log.DEFENCE_DEACTIVATE)
            self.ai.in_defence = False

        return self.process_discard_option(selected_tile, closed_hand, print_log=print_log)

    def calculate_waits(self, tiles_34, open_sets_34=None):
        """
        :param tiles_34: array of tiles in 34 formant, 13 of them (this is important)
        :param open_sets_34: array of array with tiles in 34 format
        :return: array of waits in 34 format and number of shanten
        """
        shanten = self.ai.shanten_calculator.calculate_shanten(tiles_34, open_sets_34, chiitoitsu=self.ai.use_chitoitsu)
        waiting = []
        for j in range(0, 34):
            if tiles_34[j] == 4:
                continue

            tiles_34[j] += 1

            key = '{},{},{}'.format(
                ''.join([str(x) for x in tiles_34]),
                ';'.join([str(x) for x in open_sets_34]),
                self.ai.use_chitoitsu and 1 or 0
            )

            if key in self.ai.hand_cache:
                new_shanten = self.ai.hand_cache[key]
            else:
                new_shanten = self.ai.shanten_calculator.calculate_shanten(
                    tiles_34,
                    open_sets_34,
                    chiitoitsu=self.ai.use_chitoitsu
                )
                self.ai.hand_cache[key] = new_shanten

            if new_shanten == shanten - 1:
                waiting.append(j)

            tiles_34[j] -= 1

        return waiting, shanten

    def find_discard_options(self, tiles, closed_hand, open_sets_34=None):
        """
        :param tiles: array of tiles in 136 format
        :param closed_hand: array of tiles in 136 format
        :param open_sets_34: array of array with tiles in 34 format
        :return:
        """
        if open_sets_34 is None:
            open_sets_34 = []

        tiles_34 = TilesConverter.to_34_array(tiles)
        closed_tiles_34 = TilesConverter.to_34_array(closed_hand)
        is_agari = self.ai.agari.is_agari(tiles_34, self.player.meld_34_tiles)

        results = []
        for hand_tile in range(0, 34):
            if not closed_tiles_34[hand_tile]:
                continue

            tiles_34[hand_tile] -= 1
            waiting, shanten = self.calculate_waits(tiles_34, open_sets_34)
            tiles_34[hand_tile] += 1

            if waiting:
                results.append(DiscardOption(player=self.player,
                                             shanten=shanten,
                                             tile_to_discard=hand_tile,
                                             waiting=waiting,
                                             ukeire=self.count_tiles(waiting, closed_tiles_34)))

        if is_agari:
            shanten = Shanten.AGARI_STATE
        else:
            shanten = self.ai.shanten_calculator.calculate_shanten(
                tiles_34,
                open_sets_34,
                chiitoitsu=self.ai.use_chitoitsu
            )

        return results, shanten

    def count_tiles(self, waiting, tiles_34):
        n = 0
        not_suitable_tiles = self.ai.current_strategy and self.ai.current_strategy.not_suitable_tiles or []
        for tile_34 in waiting:
            if self.player.is_open_hand and tile_34 in not_suitable_tiles:
                continue

            n += 4 - self.player.total_tiles(tile_34, tiles_34)
        return n

    def divide_hand(self, closed_hand, melds, waiting):
        tiles = closed_hand + [waiting * 4]
        closed_melds = [x for x in melds if not x.opened]
        for meld in closed_melds:
            tiles.extend(meld.tiles[:3])

        tiles_34 = TilesConverter.to_34_array(tiles)

        results = self.player.ai.hand_divider.divide_hand(tiles_34)
        return results, tiles_34

    def _choose_best_tanki_wait(self, discard_desc):
        # FIXME: implement

        return discard_desc[0]['discard_option']

    def _choose_best_discard_in_tempai(self, discard_options):
        # first of all we find tiles that have the best hand cost * ukeire value
        call_riichi = not self.player.is_open_hand

        discard_desc = []

        for discard_option in discard_options:
            tile = discard_option.find_tile_in_hand(self.player.closed_hand)
            # temporary remove discard option to estimate hand value
            self.player.tiles.remove(tile)

            cost_x_ukeire = 0
            hand_cost = 0
            if len(discard_option.waiting) == 1:
                waiting = discard_option.waiting[0]
                hand_value = self.player.ai.estimate_hand_value(waiting, call_riichi=call_riichi)
                if hand_value.error is None:
                    hand_cost = hand_value.cost['main']
                    cost_x_ukeire = hand_cost * discard_option.ukeire

                # let's check if this is a tanki wait
                results = self.divide_hand(self.player.closed_hand, self.player.melds, waiting)
                result = results[0]

                is_tanki = False
                for hand_set in result:
                    if waiting not in hand_set:
                        continue

                    if is_pair(hand_set):
                        is_tanki = True
                        break

                discard_desc.append({
                    'discard_option': discard_option,
                    'hand_cost': hand_cost,
                    'cost_x_ukeire': cost_x_ukeire,
                    'is_tanki': is_tanki
                })
            else:
                cost_x_ukeire_sum = 0
                for waiting in discard_option.waiting:
                    hand_value = self.player.ai.estimate_hand_value(waiting, call_riichi=call_riichi)
                    if hand_value.error is None:
                        cost_x_ukeire_sum += hand_value.cost['main'] * discard_option.ukeire

                cost_x_ukeire = cost_x_ukeire_sum / len(discard_option.waiting)

                discard_desc.append({
                    'discard_option': discard_option,
                    'hand_cost': None,
                    'cost_x_ukeire': cost_x_ukeire,
                    'is_tanki': False
                })

            # return tile back to hand
            self.player.tiles.append(tile)

        discard_desc = sorted(discard_desc, key=lambda k: k['cost_x_ukeire'], reverse=True)
        best_discard_desc = [x for x in discard_desc if x['cost_x_ukeire'] == discard_desc[0]['cost_x_ukeire']]
        num_tanki_waits = len([x for x in discard_desc if x['is_tanki'] == True])

        # if we don't have any good options, e.g. all our possible waits ara karaten
        # FIXME: in that case, discard the safest tile
        if discard_desc[0]['cost_x_ukeire'] == 0:
            return sorted(discard_options, key=lambda x: x.valuation)[0]

        # what if all our waits are tanki waits? we need a special handling for that case
        if num_tanki_waits == len(discard_options):
            return self._choose_best_tanki_wait(discard_desc)

        # we only have one best option based on ukeire and cost, nothing more to do here
        if len(best_discard_desc) == 1:
            return best_discard_desc[0]['discard_option']

        # if we have several options that give us similar wait
        # FIXME: 1. we find the safest tile to discard
        # FIXME: 2. if safeness is the same, we try to discard non-dora tiles
        return best_discard_desc[0]['discard_option']

    def choose_tile_to_discard(self, tiles, closed_hand, open_sets_34, print_log=True):
        """
        Try to find best tile to discard, based on different rules
        """

        discard_options, _ = self.find_discard_options(
            tiles,
            closed_hand,
            open_sets_34
        )

        # our strategy can affect discard options
        if self.ai.current_strategy:
            discard_options = self.ai.current_strategy.determine_what_to_discard(
                discard_options,
                closed_hand,
                open_sets_34
            )

        had_to_be_discarded_tiles = [x for x in discard_options if x.had_to_be_discarded]
        if had_to_be_discarded_tiles:
            discard_options = sorted(had_to_be_discarded_tiles, key=lambda x: (x.shanten, -x.ukeire, x.valuation))
            DecisionsLogger.debug(
                log.DISCARD_OPTIONS,
                'Discard marked tiles first',
                discard_options,
                print_log=print_log
            )
            return discard_options[0]

        # remove needed tiles from discard options
        discard_options = [x for x in discard_options if not x.had_to_be_saved]

        discard_options = sorted(discard_options, key=lambda x: (x.shanten, -x.ukeire))
        first_option = discard_options[0]
        results_with_same_shanten = [x for x in discard_options if x.shanten == first_option.shanten]

        possible_options = [first_option]
        ukeire_borders = self._choose_ukeire_borders(first_option, 20, 'ukeire')
        for discard_option in results_with_same_shanten:
            # there is no sense to check already chosen tile
            if discard_option.tile_to_discard == first_option.tile_to_discard:
                continue

            # let's choose tiles that are close to the max ukeire tile
            if discard_option.ukeire >= first_option.ukeire - ukeire_borders:
                possible_options.append(discard_option)

        if first_option.shanten in [1, 2, 3]:
            ukeire_field = 'ukeire_second'
            for x in possible_options:
                self.calculate_second_level_ukeire(x)

            possible_options = sorted(possible_options, key=lambda x: -getattr(x, ukeire_field))

            filter_percentage = 20
            possible_options = self._filter_list_by_percentage(
                possible_options,
                ukeire_field,
                filter_percentage
            )
        else:
            ukeire_field = 'ukeire'
            possible_options = sorted(possible_options, key=lambda x: -getattr(x, ukeire_field))

        # tempai state has a special handling
        if first_option.shanten == 0:
            other_tiles_with_same_shanten = [x for x in possible_options if x.shanten == 0]
            return self._choose_best_discard_in_tempai(other_tiles_with_same_shanten)

        tiles_without_dora = [x for x in possible_options if x.count_of_dora == 0]

        # we have only dora candidates to discard
        if not tiles_without_dora:
            DecisionsLogger.debug(
                log.DISCARD_OPTIONS,
                context=possible_options,
                print_log=print_log
            )

            min_dora = min([x.count_of_dora for x in possible_options])
            min_dora_list = [x for x in possible_options if x.count_of_dora == min_dora]

            return sorted(min_dora_list, key=lambda x: -getattr(x, ukeire_field))[0]

        # we filter 10% of options here
        if first_option.shanten == 2 or first_option.shanten == 3:
            second_filter_percentage = 10
            filtered_options = self._filter_list_by_percentage(
                tiles_without_dora,
                ukeire_field,
                second_filter_percentage
            )
        # we should also consider borders for 3+ shanten hands
        else:
            best_option_without_dora = tiles_without_dora[0]
            ukeire_borders = self._choose_ukeire_borders(best_option_without_dora, 10, ukeire_field)
            filtered_options = []
            for discard_option in tiles_without_dora:
                val = getattr(best_option_without_dora, ukeire_field) - ukeire_borders
                if getattr(discard_option, ukeire_field) >= val:
                    filtered_options.append(discard_option)

        DecisionsLogger.debug(
            log.DISCARD_OPTIONS,
            context=possible_options,
            print_log=print_log
        )

        closed_hand_34 = TilesConverter.to_34_array(closed_hand)
        isolated_tiles = [x for x in filtered_options if is_tile_strictly_isolated(closed_hand_34, x.tile_to_discard)]
        # isolated tiles should be discarded first
        if isolated_tiles:
            # let's sort tiles by value and let's choose less valuable tile to discard
            return sorted(isolated_tiles, key=lambda x: x.valuation)[0]

        # there are no isolated tiles or we don't care about them
        # let's discard tile with greater ukeire/ukeire2
        filtered_options = sorted(filtered_options, key=lambda x: -getattr(x, ukeire_field))
        first_option = filtered_options[0]

        other_tiles_with_same_ukeire = [x for x in filtered_options
                                        if getattr(x, ukeire_field) == getattr(first_option, ukeire_field)]

        # it will happen with shanten=1, all tiles will have ukeire_second == 0
        # or in tempai we can have several tiles with same ukeire
        if other_tiles_with_same_ukeire:
            return sorted(other_tiles_with_same_ukeire, key=lambda x: x.valuation)[0]

        # we have only one candidate to discard with greater ukeire
        return first_option

    def process_discard_option(self, discard_option, closed_hand, force_discard=False, print_log=True):
        if print_log:
            DecisionsLogger.debug(
                log.DISCARD,
                context=discard_option
            )

        self.player.in_tempai = discard_option.shanten == 0
        self.ai.waiting = discard_option.waiting
        self.ai.shanten = discard_option.shanten
        self.ai.ukeire = discard_option.ukeire
        self.ai.ukeire_second = discard_option.ukeire_second

        # when we called meld we don't need "smart" discard
        if force_discard:
            return discard_option.find_tile_in_hand(closed_hand)

        last_draw_34 = self.player.last_draw and self.player.last_draw // 4 or None
        if self.player.last_draw not in AKA_DORA_LIST and last_draw_34 == discard_option.tile_to_discard:
            return self.player.last_draw
        else:
            return discard_option.find_tile_in_hand(closed_hand)

    def calculate_second_level_ukeire(self, discard_option):
        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
        not_suitable_tiles = self.ai.current_strategy and self.ai.current_strategy.not_suitable_tiles or []

        tiles = copy.copy(self.player.tiles)
        tiles.remove(discard_option.find_tile_in_hand(self.player.closed_hand))

        sum_tiles = 0
        for wait_34 in discard_option.waiting:
            if self.player.is_open_hand and wait_34 in not_suitable_tiles:
                continue

            wait_136 = wait_34 * 4
            tiles.append(wait_136)

            results, shanten = self.find_discard_options(
                tiles,
                self.player.closed_hand,
                self.player.meld_34_tiles
            )
            results = [x for x in results if x.shanten == discard_option.shanten - 1]

            # let's take best ukeire here
            if results:
                best_one = sorted(results, key=lambda x: -x.ukeire)[0]
                live_tiles = 4 - self.player.total_tiles(wait_34, closed_hand_34)
                sum_tiles += best_one.ukeire * live_tiles

            tiles.remove(wait_136)

        discard_option.ukeire_second = sum_tiles

    def _filter_list_by_percentage(self, items, attribute, percentage):
        filtered_options = []
        first_option = items[0]
        ukeire_borders = round((getattr(first_option, attribute) / 100) * percentage)
        for x in items:
            if getattr(x, attribute) >= getattr(first_option, attribute) - ukeire_borders:
                filtered_options.append(x)
        return filtered_options

    def _choose_ukeire_borders(self, first_option, border_percentage, border_field):
        ukeire_borders = round((getattr(first_option, border_field) / 100) * border_percentage)

        if first_option.shanten == 0 and ukeire_borders < 2:
            ukeire_borders = 2

        if first_option.shanten == 1 and ukeire_borders < 4:
            ukeire_borders = 4

        if first_option.shanten >= 2 and ukeire_borders < 8:
            ukeire_borders = 8

        return ukeire_borders
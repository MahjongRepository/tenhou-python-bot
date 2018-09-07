# -*- coding: utf-8 -*-
import copy
import logging

from mahjong.agari import Agari
from mahjong.constants import AKA_DORA_LIST
from mahjong.hand_calculating.divider import HandDivider
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.meld import Meld
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter
from mahjong.utils import is_pon, is_tile_strictly_isolated

from game.ai.base.main import InterfaceAI
from game.ai.discard import DiscardOption
from game.ai.first_version.riichi import Riichi
from game.ai.first_version.defence.main import DefenceHandler
from game.ai.first_version.strategies.chiitoitsu import ChiitoitsuStrategy
from game.ai.first_version.strategies.chinitsu import ChinitsuStrategy
from game.ai.first_version.strategies.formal_tempai import FormalTempaiStrategy
from game.ai.first_version.strategies.honitsu import HonitsuStrategy
from game.ai.first_version.strategies.main import BaseStrategy
from game.ai.first_version.strategies.tanyao import TanyaoStrategy
from game.ai.first_version.strategies.yakuhai import YakuhaiStrategy

logger = logging.getLogger('ai')


class ImplementationAI(InterfaceAI):
    version = '0.4.0-dev'

    agari = None
    shanten_calculator = None
    defence = None
    damaten = None
    hand_divider = None
    finished_hand = None

    shanten = 7
    ukeire = 0
    ukeire_second = 0
    in_defence = False
    waiting = None

    current_strategy = None
    last_discard_option = None

    use_chitoitsu = False

    hand_cache = {}

    def __init__(self, player):
        super(ImplementationAI, self).__init__(player)

        self.agari = Agari()
        self.shanten_calculator = Shanten()
        self.defence = DefenceHandler(player)
        self.riichi = Riichi(player)
        self.hand_divider = HandDivider()
        self.finished_hand = HandCalculator()

        self.erase_state()

    def init_hand(self):
        # it will set correct hand shanten number and ukeire to the new hand
        # tile will not be removed from the hand
        self.discard_tile(None)
        self.player.in_tempai = False

        # Let's decide what we will do with our hand (like open for tanyao and etc.)
        self.determine_strategy(self.player.tiles)

    def draw_tile(self, tile):
        """
        :param tile: 136 tile format
        :return:
        """
        self.determine_strategy(self.player.tiles)

    def discard_tile(self, discard_tile):
        # we called meld and we had discard tile that we wanted to discard
        if discard_tile is not None:
            if not self.last_discard_option:
                return discard_tile

            return self.process_discard_option(self.last_discard_option, self.player.closed_hand, True)

        results, shanten = self.calculate_outs(self.player.tiles,
                                               self.player.closed_hand,
                                               self.player.meld_34_tiles)

        selected_tile = self.process_discard_options_and_select_tile_to_discard(results, shanten)

        # bot think that there is a threat on the table
        # and better to fold
        # if we can't find safe tiles, let's continue to build our hand
        if self.defence.should_go_to_defence_mode(selected_tile):
            if not self.in_defence:
                logger.info('We decided to fold against other players')
                self.in_defence = True

            defence_tile = self.defence.try_to_find_safe_tile_to_discard(results)
            if defence_tile:
                return self.process_discard_option(defence_tile, self.player.closed_hand)
        else:
            if self.in_defence:
                logger.info('Stop defence mode')
            self.in_defence = False

        return self.process_discard_option(selected_tile, self.player.closed_hand)

    def process_discard_options_and_select_tile_to_discard(self, results, shanten, had_was_open=False):
        # we had to update tiles value there
        # because it is related with shanten number
        for result in results:
            result.ukeire = self.count_tiles(result.waiting, TilesConverter.to_34_array(self.player.closed_hand))
            result.calculate_value(shanten)

        # current strategy can affect on our discard options
        # so, don't use strategy specific choices for calling riichi
        if self.current_strategy:
            results = self.current_strategy.determine_what_to_discard(self.player.closed_hand,
                                                                      results,
                                                                      shanten,
                                                                      False,
                                                                      None,
                                                                      had_was_open)

        return self.choose_tile_to_discard(results)

    def calculate_outs(self, tiles, closed_hand, open_sets_34=None):
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
        is_agari = self.agari.is_agari(tiles_34, self.player.meld_34_tiles)

        results = []
        for hand_tile in range(0, 34):
            if not closed_tiles_34[hand_tile]:
                continue

            tiles_34[hand_tile] -= 1

            shanten = self.shanten_calculator.calculate_shanten(tiles_34, open_sets_34, chiitoitsu=self.use_chitoitsu)

            waiting = []
            for j in range(0, 34):
                if tiles_34[j] == 4:
                    continue

                # agari is a special case, we are forced to make number
                # of shanten larger, so we don't skip any tiles
                # in the end we let the strategy decide what to do if agari without yaku happened
                if not is_agari and hand_tile == j:
                    continue

                tiles_34[j] += 1

                key = '{},{},{}'.format(
                    ''.join([str(x) for x in tiles_34]),
                    ';'.join([str(x) for x in open_sets_34]),
                    self.use_chitoitsu and 1 or 0
                )

                if key in self.hand_cache:
                    new_shanten = self.hand_cache[key]
                else:
                    new_shanten = self.shanten_calculator.calculate_shanten(
                        tiles_34,
                        open_sets_34,
                        chiitoitsu=self.use_chitoitsu
                    )
                    self.hand_cache[key] = new_shanten

                if new_shanten == shanten - 1:
                    waiting.append(j)

                tiles_34[j] -= 1

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
            shanten = self.shanten_calculator.calculate_shanten(tiles_34, open_sets_34, chiitoitsu=self.use_chitoitsu)

        return results, shanten

    def count_tiles(self, waiting, tiles_34):
        n = 0
        not_suitable_tiles = self.current_strategy and self.current_strategy.not_suitable_tiles or []
        for tile_34 in waiting:
            if self.player.is_open_hand and tile_34 in not_suitable_tiles:
                continue

            n += 4 - self.player.total_tiles(tile_34, tiles_34)
        return n

    def try_to_call_meld(self, tile, is_kamicha_discard):
        tiles_136 = self.player.tiles[:] + [tile]
        self.determine_strategy(tiles_136)

        if not self.current_strategy:
            return None, None

        tiles_34 = TilesConverter.to_34_array(tiles_136)
        previous_shanten = self.shanten_calculator.calculate_shanten(
            tiles_34,
            self.player.meld_34_tiles,
            chiitoitsu=self.use_chitoitsu
        )
        if previous_shanten == Shanten.AGARI_STATE:
            if not self.current_strategy.can_meld_into_agari():
                return None, None

        meld, discard_option = self.current_strategy.try_to_call_meld(tile, is_kamicha_discard, tiles_136)
        tile_to_discard = None
        if discard_option:
            self.last_discard_option = discard_option
            tile_to_discard = discard_option.tile_to_discard

        return meld, tile_to_discard

    def determine_strategy(self, tiles_136):
        self.use_chitoitsu = False

        # for already opened hand we don't need to give up on selected strategy
        if self.player.is_open_hand and self.current_strategy:
            return False

        old_strategy = self.current_strategy
        self.current_strategy = None

        # order is important
        strategies = [
            ChinitsuStrategy(BaseStrategy.CHINITSU, self.player),
            HonitsuStrategy(BaseStrategy.HONITSU, self.player),
            YakuhaiStrategy(BaseStrategy.YAKUHAI, self.player),
        ]

        if self.player.table.has_open_tanyao:
            strategies.append(TanyaoStrategy(BaseStrategy.TANYAO, self.player))

        strategies.append(ChiitoitsuStrategy(BaseStrategy.CHIITOITSU, self.player))
        strategies.append(FormalTempaiStrategy(BaseStrategy.FORMAL_TEMPAI, self.player))

        for strategy in strategies:
            if strategy.should_activate_strategy(tiles_136):
                self.current_strategy = strategy

        if self.current_strategy:
            self.use_chitoitsu = self.current_strategy.type == BaseStrategy.CHIITOITSU

            if not old_strategy or self.current_strategy.type != old_strategy.type:
                message = '{} switched to {} strategy'.format(self.player.name, self.current_strategy)
                if old_strategy:
                    message += ' from {}'.format(old_strategy)
                logger.debug(message)
                logger.debug('With hand: {}'.format(TilesConverter.to_one_line_string(self.player.tiles)))

        if not self.current_strategy and old_strategy:
            logger.debug('{} gave up on {}'.format(self.player.name, old_strategy))

        return self.current_strategy and True or False

    def choose_tile_to_discard(self, results: [DiscardOption]) -> DiscardOption:
        """
        Try to find best tile to discard, based on different rules
        """

        had_to_be_discarded_tiles = [x for x in results if x.had_to_be_discarded]
        if had_to_be_discarded_tiles:
            return sorted(had_to_be_discarded_tiles, key=lambda x: (x.shanten, -x.ukeire, x.valuation))[0]

        # remove needed tiles from discard options
        results = [x for x in results if not x.had_to_be_saved]

        results = sorted(results, key=lambda x: (x.shanten, -x.ukeire))
        first_option = results[0]
        results_with_same_shanten = [x for x in results if x.shanten == first_option.shanten]

        possible_options = [first_option]

        ukeire_borders = self._choose_ukeire_borders(first_option, 20)

        for discard_option in results_with_same_shanten:
            # there is no sense to check already chosen tile
            if discard_option.tile_to_discard == first_option.tile_to_discard:
                continue

            # let's choose tiles that are close to the max ukeire tile
            if discard_option.ukeire >= first_option.ukeire - ukeire_borders:
                possible_options.append(discard_option)

        # for 2 or 3 shanten hand we consider ukeire one step ahead
        if first_option.shanten == 2 or first_option.shanten == 3:
            sorting_field = 'ukeire_second'
            for x in possible_options:
                self.calculate_second_level_ukeire(x)

            possible_options = sorted(possible_options, key=lambda x: -getattr(x, sorting_field))

            filter_percentage = 20
            possible_options = self._filter_list_by_percentage(
                possible_options,
                sorting_field,
                filter_percentage
            )
        else:
            sorting_field = 'ukeire'
            possible_options = sorted(possible_options, key=lambda x: -getattr(x, sorting_field))

        tiles_without_dora = [x for x in possible_options if x.count_of_dora == 0]

        # we have only dora candidates to discard
        if not tiles_without_dora:
            min_dora = min([x.count_of_dora for x in possible_options])
            min_dora_list = [x for x in possible_options if x.count_of_dora == min_dora]

            return sorted(min_dora_list, key=lambda x: -getattr(x, sorting_field))[0]

        # we filter 10% of options, but if we use ukeire, we should also consider borders
        if first_option.shanten == 2 or first_option.shanten == 3:
            second_filter_percentage = 10
            filtered_options = self._filter_list_by_percentage(
                tiles_without_dora,
                sorting_field,
                second_filter_percentage
            )
        else:
            best_option_without_dora = tiles_without_dora[0]
            ukeire_borders = self._choose_ukeire_borders(best_option_without_dora, 10)
            filtered_options = [best_option_without_dora]
            for discard_option in tiles_without_dora:
                if discard_option.ukeire >= best_option_without_dora.ukeire - ukeire_borders:
                    filtered_options.append(discard_option)

        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
        isolated_tiles = [x for x in filtered_options if is_tile_strictly_isolated(closed_hand_34, x.tile_to_discard)]
        # isolated tiles should be discarded first
        if isolated_tiles:
            # let's sort tiles by value and let's choose less valuable tile to discard
            return sorted(isolated_tiles, key=lambda x: x.valuation)[0]

        # there are no isolated tiles
        # let's discard tile with greater ukeire2
        filtered_options = sorted(filtered_options, key=lambda x: -getattr(x, sorting_field))
        first_option = filtered_options[0]

        other_tiles_with_same_ukeire = [x for x in filtered_options
                                        if getattr(x, sorting_field) == getattr(first_option, sorting_field)]

        # it will happen with shanten=1, all tiles will have ukeire_second == 0
        if other_tiles_with_same_ukeire:
            # let's sort tiles by value and let's choose less valuable tile to discard
            return sorted(other_tiles_with_same_ukeire, key=lambda x: x.valuation)[0]

        # we have only one candidate to discard with greater ukeire
        return first_option

    def process_discard_option(self, discard_option, closed_hand, force_discard=False):
        self.waiting = discard_option.waiting
        self.player.ai.shanten = discard_option.shanten
        self.player.in_tempai = self.player.ai.shanten == 0
        self.player.ai.ukeire = discard_option.ukeire
        self.player.ai.ukeire_second = discard_option.ukeire_second

        # when we called meld we don't need "smart" discard
        if force_discard:
            return discard_option.find_tile_in_hand(closed_hand)

        last_draw_34 = self.player.last_draw and self.player.last_draw // 4 or None
        if self.player.last_draw not in AKA_DORA_LIST and last_draw_34 == discard_option.tile_to_discard:
            return self.player.last_draw
        else:
            return discard_option.find_tile_in_hand(closed_hand)

    def estimate_hand_value(self, win_tile, tiles=None, call_riichi=False):
        """
        :param win_tile: 34 tile format
        :param tiles:
        :param call_riichi:
        :return:
        """
        win_tile *= 4

        # we don't need to think, that our waiting is aka dora
        if win_tile in AKA_DORA_LIST:
            win_tile += 1

        if not tiles:
            tiles = copy.copy(self.player.tiles)

        tiles += [win_tile]

        config = HandConfig(
            is_riichi=call_riichi,
            player_wind=self.player.player_wind,
            round_wind=self.player.table.round_wind,
            has_aka_dora=self.player.table.has_aka_dora,
            has_open_tanyao=self.player.table.has_open_tanyao
        )

        result = self.finished_hand.estimate_hand_value(tiles,
                                                        win_tile,
                                                        self.player.melds,
                                                        self.player.table.dora_indicators,
                                                        config)
        return result

    def should_call_riichi(self):
        return self.riichi.should_call_riichi()

    def should_call_kan(self, tile, open_kan, from_riichi=False):
        """
        Method will decide should we call a kan,
        or upgrade pon to kan
        :param tile: 136 tile format
        :param open_kan: boolean
        :param from_riichi: boolean
        :return: kan type
        """

        # we can't call kan on the latest tile
        if self.table.count_of_remaining_tiles <= 1:
            return None

        # we don't need to add dora for other players
        if self.player.ai.in_defence:
            return None

        if open_kan:
            # we don't want to start open our hand from called kan
            if not self.player.is_open_hand:
                return None

            # there is no sense to call open kan when we are not in tempai
            if not self.player.in_tempai:
                return None

            # we have a bad wait, rinshan chance is low
            if len(self.waiting) < 2:
                return None

        tile_34 = tile // 4
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)

        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
        pon_melds = [x for x in self.player.meld_34_tiles if is_pon(x)]

        # let's check can we upgrade opened pon to the kan
        if pon_melds:
            for meld in pon_melds:
                # tile is equal to our already opened pon,
                # so let's call chankan!
                if tile_34 in meld:
                    return Meld.CHANKAN

        # we can try to call closed meld
        if closed_hand_34[tile_34] == 3:
            if not open_kan and not from_riichi:
                tiles_34[tile_34] += 1

            melds = self.player.meld_34_tiles
            previous_shanten = self.shanten_calculator.calculate_shanten(tiles_34, melds, chiitoitsu=self.use_chitoitsu)

            if not open_kan and not from_riichi:
                tiles_34[tile_34] -= 1

            melds += [[tile_34, tile_34, tile_34]]
            new_shanten = self.shanten_calculator.calculate_shanten(tiles_34, melds, chiitoitsu=self.use_chitoitsu)

            # called kan will not ruin our hand
            if new_shanten <= previous_shanten:
                return Meld.KAN

        return None

    def should_call_win(self, tile, enemy_seat):
        return True

    def enemy_called_riichi(self, enemy_seat):
        """
        After enemy riichi we had to check will we fold or not
        it is affect open hand decisions
        :return:
        """
        if self.defence.should_go_to_defence_mode():
            self.in_defence = True

    def calculate_second_level_ukeire(self, discard_option):
        tiles = copy.copy(self.player.tiles)
        tiles.remove(discard_option.find_tile_in_hand(self.player.closed_hand))

        sum_tiles = 0
        for wait in discard_option.waiting:
            wait = wait * 4
            tiles.append(wait)

            results, shanten = self.calculate_outs(
                tiles,
                self.player.closed_hand,
                self.player.meld_34_tiles
            )
            results = [x for x in results if x.shanten == discard_option.shanten - 1]
            # let's take best ukeire here
            if results:
                sum_tiles += sorted(results, key=lambda x: -x.ukeire)[0].ukeire

            tiles.remove(wait)

        discard_option.ukeire_second = sum_tiles

    @property
    def enemy_players(self):
        """
        Return list of players except our bot
        """
        return self.player.table.players[1:]

    @staticmethod
    def _filter_list_by_percentage(items, attribute, percentage):
        filtered_options = []
        first_option = items[0]
        ukeire_borders = round((getattr(first_option, attribute) / 100) * percentage)
        for x in items:
            if getattr(x, attribute) >= getattr(first_option, attribute) - ukeire_borders:
                filtered_options.append(x)
        return filtered_options

    @staticmethod
    def _choose_ukeire_borders(first_option, border_percentage):
        ukeire_borders = round((first_option.ukeire / 100) * border_percentage)

        if first_option.shanten == 0 and ukeire_borders < 2:
            ukeire_borders = 2

        if first_option.shanten == 1 and ukeire_borders < 4:
            ukeire_borders = 4

        if first_option.shanten >= 2 and ukeire_borders < 8:
            ukeire_borders = 8

        return ukeire_borders

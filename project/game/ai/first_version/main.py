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
from mahjong.utils import is_pair, is_pon, is_tile_strictly_isolated

from game.ai.base.main import InterfaceAI
from game.ai.discard import DiscardOption
from game.ai.first_version.defence.main import DefenceHandler
from game.ai.first_version.strategies.honitsu import HonitsuStrategy
from game.ai.first_version.strategies.main import BaseStrategy
from game.ai.first_version.strategies.tanyao import TanyaoStrategy
from game.ai.first_version.strategies.yakuhai import YakuhaiStrategy
from game.ai.first_version.strategies.formal_tempai import FormalTempaiStrategy

logger = logging.getLogger('ai')


class ImplementationAI(InterfaceAI):
    version = '0.4.0-dev'

    agari = None
    shanten = None
    defence = None
    hand_divider = None
    finished_hand = None
    last_discard_option = None

    previous_shanten = 7
    ukeire = 0
    ukeire_second = 0
    in_defence = False
    waiting = None

    current_strategy = None

    def __init__(self, player):
        super(ImplementationAI, self).__init__(player)

        self.agari = Agari()
        self.shanten = Shanten()
        self.defence = DefenceHandler(player)
        self.hand_divider = HandDivider()
        self.finished_hand = HandCalculator()
        self.previous_shanten = 7
        self.ukeire = 0
        self.ukeire_second = 0
        self.current_strategy = None
        self.waiting = []
        self.in_defence = False
        self.last_discard_option = None

    def init_hand(self):
        """
        Let's decide what we will do with our hand (like open for tanyao and etc.)
        """
        self.determine_strategy()

    def erase_state(self):
        self.current_strategy = None
        self.waiting = []
        self.in_defence = False
        self.last_discard_option = None
        self.previous_shanten = 7
        self.ukeire = 0
        self.ukeire_second = 0

    def draw_tile(self, tile):
        """
        :param tile: 136 tile format
        :return:
        """
        self.determine_strategy()

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
            self.in_defence = False

        return self.process_discard_option(selected_tile, self.player.closed_hand)

    def process_discard_options_and_select_tile_to_discard(self, results, shanten, had_was_open=False):
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)

        # we had to update tiles value there
        # because it is related with shanten number
        for result in results:
            result.ukeire = self.count_tiles(result.waiting, tiles_34)
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
        tiles_34 = TilesConverter.to_34_array(tiles)
        closed_tiles_34 = TilesConverter.to_34_array(closed_hand)
        is_agari = self.agari.is_agari(tiles_34, self.player.meld_34_tiles)

        results = []
        for hand_tile in range(0, 34):
            if not closed_tiles_34[hand_tile]:
                continue

            tiles_34[hand_tile] -= 1

            shanten = self.shanten.calculate_shanten(tiles_34, open_sets_34)

            waiting = []
            for j in range(0, 34):
                if hand_tile == j or tiles_34[j] == 4:
                    continue

                tiles_34[j] += 1
                if self.shanten.calculate_shanten(tiles_34, open_sets_34) == shanten - 1:
                    waiting.append(j)
                tiles_34[j] -= 1

            tiles_34[hand_tile] += 1

            if waiting:
                results.append(DiscardOption(player=self.player,
                                             shanten=shanten,
                                             tile_to_discard=hand_tile,
                                             waiting=waiting,
                                             ukeire=self.count_tiles(waiting, tiles_34)))

        if is_agari:
            shanten = Shanten.AGARI_STATE
        else:
            shanten = self.shanten.calculate_shanten(tiles_34, open_sets_34)

        return results, shanten

    def count_tiles(self, waiting, tiles_34):
        n = 0
        for item in waiting:
            n += 4 - self.player.total_tiles(item, tiles_34)
        return n

    def try_to_call_meld(self, tile, is_kamicha_discard):
        if not self.current_strategy:
            return None, None

        meld, discard_option = self.current_strategy.try_to_call_meld(tile, is_kamicha_discard)
        tile_to_discard = None
        if discard_option:
            self.last_discard_option = discard_option
            tile_to_discard = discard_option.tile_to_discard

        return meld, tile_to_discard

    def determine_strategy(self):
        # for already opened hand we don't need to give up on selected strategy
        if self.player.is_open_hand and self.current_strategy:
            return False

        old_strategy = self.current_strategy
        self.current_strategy = None

        # order is important
        strategies = [
            YakuhaiStrategy(BaseStrategy.YAKUHAI, self.player),
            HonitsuStrategy(BaseStrategy.HONITSU, self.player),
        ]

        if self.player.table.has_open_tanyao:
            strategies.append(TanyaoStrategy(BaseStrategy.TANYAO, self.player))

        strategies.append(FormalTempaiStrategy(BaseStrategy.FORMAL_TEMPAI, self.player))

        for strategy in strategies:
            if strategy.should_activate_strategy():
                self.current_strategy = strategy

        if self.current_strategy:
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
        border_percentage = 20
        for discard_option in results_with_same_shanten:
            # there is no sense to check already chosen tile
            if discard_option.tile_to_discard == first_option.tile_to_discard:
                continue

            # we don't need to select tiles almost dead waits
            if discard_option.ukeire <= 2:
                continue

            ukeire_borders = round((first_option.ukeire / 100) * border_percentage)

            if first_option.shanten == 0 and ukeire_borders < 2:
                ukeire_borders = 2

            if first_option.shanten == 1 and ukeire_borders < 4:
                ukeire_borders = 4

            if first_option.shanten >= 2 and ukeire_borders < 8:
                ukeire_borders = 8

            # let's choose tiles that are close to the max ukeire tile
            if discard_option.ukeire >= first_option.ukeire - ukeire_borders:
                possible_options.append(discard_option)

        if first_option.shanten <= 1:
            # let's sort tiles by value and let's choose less valuable tile to discard
            return sorted(possible_options, key=lambda x: x.valuation)[0]

        # as second step
        # let's choose tiles that are close to the max ukeire2 tile
        for x in possible_options:
            self.calculate_second_level_ukeire(x)

        possible_options = sorted(possible_options, key=lambda x: -x.ukeire_second)

        filter_percentage = 20
        filtered_options = self._filter_list_by_percentage(
            possible_options,
            'ukeire_second',
            filter_percentage
        )

        dora_tiles = [x for x in filtered_options if x.count_of_dora > 0]
        # we have only dora candidates to discard
        if len(dora_tiles) == len(filtered_options):
            min_dora = min([x.count_of_dora for x in filtered_options])
            min_dora_list = [x for x in filtered_options if x.count_of_dora == min_dora]

            # let's discard tile with greater ukeire2
            return sorted(min_dora_list, key=lambda x: -x.ukeire_second)[0]

        second_filter_percentage = 10
        filtered_options = self._filter_list_by_percentage(
            filtered_options,
            'ukeire_second',
            second_filter_percentage
        )

        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
        isolated_tiles = [x for x in filtered_options if is_tile_strictly_isolated(closed_hand_34, x.tile_to_discard)]
        # isolated tiles should be discarded first
        if isolated_tiles:
            # let's sort tiles by value and let's choose less valuable tile to discard
            return sorted(isolated_tiles, key=lambda x: x.valuation)[0]

        # there are no isolated tiles
        # let's discard tile with greater ukeire2
        return sorted(filtered_options, key=lambda x: -x.ukeire_second)[0]

    def process_discard_option(self, discard_option, closed_hand, force_discard=False):
        self.waiting = discard_option.waiting
        self.player.ai.previous_shanten = discard_option.shanten
        self.player.in_tempai = self.player.ai.previous_shanten == 0
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
            tiles = self.player.tiles

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
        # empty waiting can be found in some cases
        if not self.waiting:
            return False

        if self.in_defence:
            return False

        # we have a good wait, let's riichi
        if len(self.waiting) > 1:
            return True

        waiting = self.waiting[0]
        tiles = self.player.closed_hand + [waiting * 4]
        closed_melds = [x for x in self.player.melds if not x.opened]
        for meld in closed_melds:
            tiles.extend(meld.tiles[:3])

        tiles_34 = TilesConverter.to_34_array(tiles)

        results = self.hand_divider.divide_hand(tiles_34)
        result = results[0]

        count_of_pairs = len([x for x in result if is_pair(x)])
        # with chitoitsu we can call a riichi with pair wait
        if count_of_pairs == 7:
            return True

        for hand_set in result:
            # better to not call a riichi for a pair wait
            # it can be easily improved
            if is_pair(hand_set) and waiting in hand_set:
                return False

        return True

    def should_call_kan(self, tile, open_kan):
        """
        Method will decide should we call a kan,
        or upgrade pon to kan
        :param tile: 136 tile format
        :param open_kan: boolean
        :return: kan type
        """
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

        count_of_needed_tiles = 4
        # for open kan 3 tiles is enough to call a kan
        if open_kan:
            count_of_needed_tiles = 3

        # we can try to call closed meld
        if closed_hand_34[tile_34] == count_of_needed_tiles:
            melds = self.player.meld_34_tiles
            previous_shanten = self.shanten.calculate_shanten(tiles_34, melds)

            if not open_kan:
                tiles_34[tile_34] -= 1

            melds += [[tile_34, tile_34, tile_34]]
            new_shanten = self.shanten.calculate_shanten(tiles_34, melds)

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
            sum_tiles += sum([x.ukeire for x in results])

            tiles.remove(wait)

        discard_option.ukeire_second = sum_tiles

    @property
    def enemy_players(self):
        """
        Return list of players except our bot
        """
        return self.player.table.players[1:]

    def _filter_list_by_percentage(self, items, attribute, percentage):
        filtered_options = []
        first_option = items[0]
        ukeire_borders = round((getattr(first_option, attribute) / 100) * percentage)
        for x in items:
            if getattr(x, attribute) >= getattr(first_option, attribute) - ukeire_borders:
                filtered_options.append(x)
        return filtered_options

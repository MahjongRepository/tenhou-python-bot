# -*- coding: utf-8 -*-
import logging

from mahjong.ai.agari import Agari
from mahjong.ai.base import BaseAI
from mahjong.ai.defence.main import DefenceHandler
from mahjong.ai.discard import DiscardOption
from mahjong.ai.shanten import Shanten
from mahjong.ai.strategies.honitsu import HonitsuStrategy
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.ai.strategies.tanyao import TanyaoStrategy
from mahjong.ai.strategies.yakuhai import YakuhaiStrategy
from mahjong.constants import HAKU, CHUN, HATSU, AKA_DORA_LIST
from mahjong.hand import HandDivider, FinishedHand
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_pair, is_pon
from utils.settings_handler import settings

logger = logging.getLogger('ai')


class MainAI(BaseAI):
    version = '0.2.5'

    agari = None
    shanten = None
    defence = None
    hand_divider = None
    finished_hand = None

    previous_shanten = 7
    in_defence = False
    waiting = None

    current_strategy = None

    def __init__(self, player):
        super(MainAI, self).__init__(player)

        self.agari = Agari()
        self.shanten = Shanten()
        self.defence = DefenceHandler(player)
        self.hand_divider = HandDivider()
        self.finished_hand = FinishedHand()
        self.previous_shanten = 7
        self.current_strategy = None
        self.waiting = []
        self.in_defence = False

    def erase_state(self):
        self.current_strategy = None
        self.in_defence = False

    def discard_tile(self):
        results, shanten = self.calculate_outs(self.player.tiles,
                                               self.player.closed_hand,
                                               self.player.open_hand_34_tiles)

        we_can_call_riichi = shanten == 0 and self.player.can_call_riichi()

        selected_tile = self.process_discard_options_and_select_tile_to_discard(results, shanten)

        # bot think that there is a threat on the table
        # and better to fold
        # if we can't find safe tiles, let's continue to build our hand
        if self.defence.should_go_to_defence_mode(selected_tile) and not we_can_call_riichi:
            if not self.in_defence:
                logger.info('We decided to fold against other players')
                self.in_defence = True

            defence_tile = self.defence.try_to_find_safe_tile_to_discard(results)
            if defence_tile:
                return self.process_discard_option(defence_tile, self.player.closed_hand)
        else:
            self.in_defence = False

        return self.process_discard_option(selected_tile, self.player.closed_hand)

    def process_discard_options_and_select_tile_to_discard(self, results, shanten):
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        we_can_call_riichi = shanten == 0 and self.player.can_call_riichi()

        # we had to update tiles value there
        # because it is related with shanten number
        for result in results:
            result.tiles_count = self.count_tiles(result.waiting, tiles_34)
            result.calculate_value(shanten)

        # current strategy can affect on our discard options
        # so, don't use strategy specific choices for calling riichi
        if self.current_strategy and not we_can_call_riichi:
            results = self.current_strategy.determine_what_to_discard(self.player.closed_hand,
                                                                      results,
                                                                      shanten,
                                                                      False,
                                                                      None)

        return self.chose_tile_to_discard(results)

    def calculate_outs(self, tiles, closed_hand, open_sets_34=None):
        """
        :param tiles: array of tiles in 136 format
        :param closed_hand: array of tiles in 136 format
        :param open_sets_34: array of array with tiles in 34 format
        :return:
        """
        tiles_34 = TilesConverter.to_34_array(tiles)
        closed_tiles_34 = TilesConverter.to_34_array(closed_hand)
        is_agari = self.agari.is_agari(tiles_34, self.player.open_hand_34_tiles)

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
                                             tiles_count=self.count_tiles(waiting, tiles_34)))

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

        return self.current_strategy.try_to_call_meld(tile, is_kamicha_discard)

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

        if settings.OPEN_TANYAO:
            strategies.append(TanyaoStrategy(BaseStrategy.TANYAO, self.player))

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

    def chose_tile_to_discard(self, results: [DiscardOption]) -> DiscardOption:
        """
        Try to find best tile to discard, based on different valuations
        """

        def sorting(x):
            # - is important for x.tiles_count
            # in that case we will discard tile that will give for us more tiles
            # to complete a hand
            return x.shanten, -x.tiles_count, x.valuation

        had_to_be_discarded_tiles = [x for x in results if x.had_to_be_discarded]
        if had_to_be_discarded_tiles:
            had_to_be_discarded_tiles = sorted(had_to_be_discarded_tiles, key=sorting)
            selected_tile = had_to_be_discarded_tiles[0]
        else:
            results = sorted(results, key=sorting)
            # remove needed tiles from discard options
            results = [x for x in results if not x.had_to_be_saved]

            # let's chose most valuable tile first
            temp_tile = results[0]
            # and let's find all tiles with same shanten
            results_with_same_shanten = [x for x in results if x.shanten == temp_tile.shanten]
            possible_options = [temp_tile]
            for discard_option in results_with_same_shanten:
                # there is no sense to check already chosen tile
                if discard_option.tile_to_discard == temp_tile.tile_to_discard:
                    continue

                # we don't need to select tiles almost dead waits
                if discard_option.tiles_count <= 2:
                    continue

                # let's check all other tiles with same shanten
                # maybe we can find tiles that have almost same tiles count number
                if temp_tile.tiles_count - 2 < discard_option.tiles_count < temp_tile.tiles_count + 2:
                    possible_options.append(discard_option)

            # let's sort got tiles by value and let's chose less valuable tile to discard
            possible_options = sorted(possible_options, key=lambda x: x.valuation)
            selected_tile = possible_options[0]

        return selected_tile

    def process_discard_option(self, selected_tile, closed_hand):
        self.waiting = selected_tile.waiting
        self.player.ai.previous_shanten = selected_tile.shanten
        self.player.in_tempai = self.player.ai.previous_shanten == 0
        return selected_tile.find_tile_in_hand(closed_hand)

    def estimate_hand_value(self, win_tile, tiles=None):
        """
        :param win_tile: 34 tile format
        :param tiles:
        :return:
        """
        win_tile *= 4
        # we don't need to think, that our waiting is aka dora
        if win_tile in AKA_DORA_LIST:
            win_tile += 1

        if not tiles:
            tiles = self.player.tiles

        tiles += [win_tile]
        result = self.finished_hand.estimate_hand_value(tiles=tiles,
                                                        win_tile=win_tile,
                                                        is_tsumo=False,
                                                        is_riichi=False,
                                                        is_dealer=self.player.is_dealer,
                                                        open_sets=self.player.open_hand_34_tiles,
                                                        player_wind=self.player.player_wind,
                                                        round_wind=self.player.table.round_wind,
                                                        dora_indicators=self.player.table.dora_indicators)
        return result

    def should_call_riichi(self):
        # empty waiting can be found in some cases
        if not self.waiting:
            return False

        # we have a good wait, let's riichi
        if len(self.waiting) > 1:
            return True

        waiting = self.waiting[0]
        tiles_34 = TilesConverter.to_34_array(self.player.closed_hand + [waiting * 4])

        results = self.hand_divider.divide_hand(tiles_34, [], [])
        if not results:
            return False

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

    def can_call_kan(self, tile, open_kan):
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
        pon_melds = [x for x in self.player.open_hand_34_tiles if is_pon(x)]

        # let's check can we upgrade opened pon to the kan
        if pon_melds:
            for meld in pon_melds:
                # tile is equal to our already opened pon,
                # so let's call chankan!
                if tile_34 in meld:
                    return Meld.CHANKAN

        # we have 3 tiles in our hand,
        # so we can try to call closed meld
        if closed_hand_34[tile_34] == 3:
            melds = self.player.open_hand_34_tiles
            previous_shanten = self.shanten.calculate_shanten(tiles_34, melds)

            melds += [[tile_34, tile_34, tile_34]]
            new_shanten = self.shanten.calculate_shanten(tiles_34, melds)

            # called kan will not ruin our hand
            if new_shanten <= previous_shanten:
                return Meld.KAN

        return None

    @property
    def valued_honors(self):
        return [CHUN, HAKU, HATSU, self.player.table.round_wind, self.player.player_wind]

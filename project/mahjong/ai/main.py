# -*- coding: utf-8 -*-
import logging

from mahjong.ai.agari import Agari
from mahjong.ai.base import BaseAI
from mahjong.ai.defence import Defence
from mahjong.ai.discard import DiscardOption
from mahjong.ai.shanten import Shanten
from mahjong.ai.strategies.honitsu import HonitsuStrategy
from mahjong.ai.strategies.main import BaseStrategy
from mahjong.ai.strategies.tanyao import TanyaoStrategy
from mahjong.ai.strategies.yakuhai import YakuhaiStrategy
from mahjong.constants import HAKU, CHUN, HATSU
from mahjong.hand import HandDivider, FinishedHand
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor

logger = logging.getLogger('ai')


class MainAI(BaseAI):
    version = '0.2.0'

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
        self.defence = Defence(player)
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
                                               self.player.is_open_hand)
        # we had to update tiles value
        # because it is related with shanten number
        self.previous_shanten = shanten
        for result in results:
            result.calculate_value()

        # bot think that there is a threat on the table
        # and better to fold
        # if we can't find safe tiles, let's continue to build our hand
        if self.defence.should_go_to_defence_mode():
            if not self.in_defence:
                logger.info('We decided to fold against other players')
                self.in_defence = True

            tile = self.defence.try_to_find_safe_tile_to_discard(results)
            if tile is not None:
                return tile
        else:
            self.in_defence = False

        if shanten == 0:
            self.player.in_tempai = True

        # we are win!
        if shanten == Shanten.AGARI_STATE:
            # special conditions for open hands
            if self.player.is_open_hand:
                # sometimes we can draw a tile that gave us agari,
                # but didn't give us a yaku
                # in that case we had to do last draw discard
                result = self.finished_hand.estimate_hand_value(tiles=self.player.tiles,
                                                                win_tile=self.player.last_draw,
                                                                is_tsumo=True,
                                                                is_riichi=False,
                                                                is_dealer=self.player.is_dealer,
                                                                open_sets=self.player.meld_tiles,
                                                                player_wind=self.player.player_wind,
                                                                round_wind=self.player.table.round_wind)
                if result['error'] is not None:
                    return self.player.last_draw

            return Shanten.AGARI_STATE

        # we are in agari state, but we can't win because we don't have yaku
        # in that case let's do tsumogiri
        if not results:
            return self.player.last_draw

        we_can_call_riichi = shanten == 0 and self.player.can_call_riichi()
        # current strategy can affect on our discard options
        # and don't use strategy specific choices for calling riichi
        if self.current_strategy and not we_can_call_riichi:
            results = self.current_strategy.determine_what_to_discard(self.player.closed_hand,
                                                                      results,
                                                                      shanten,
                                                                      False,
                                                                      None)

        # we had to discard dead waits first (last honor tile)
        for result in results:
            if is_honor(result.tile_to_discard) and self.player.table.revealed_tiles[result.tile_to_discard] == 3:
                result.tiles_count = 2000

        return self.chose_tile_to_discard(results, self.player.closed_hand)

    def calculate_outs(self, tiles, closed_hand, is_open_hand=False):
        """
        :param tiles: array of tiles in 136 format
        :param closed_hand: array of tiles in 136 format
        :param is_open_hand: boolean flag
        :return:
        """
        tiles_34 = TilesConverter.to_34_array(tiles)
        closed_tiles_34 = TilesConverter.to_34_array(closed_hand)
        shanten = self.shanten.calculate_shanten(tiles_34, is_open_hand, self.player.meld_tiles)

        # win
        if shanten == Shanten.AGARI_STATE:
            return [], shanten

        results = []

        for i in range(0, 34):
            if not tiles_34[i]:
                continue

            if not closed_tiles_34[i]:
                continue

            tiles_34[i] -= 1

            waiting = []
            for j in range(0, 34):
                if i == j or tiles_34[j] == 4:
                    continue

                tiles_34[j] += 1
                if self.shanten.calculate_shanten(tiles_34, is_open_hand, self.player.meld_tiles) == shanten - 1:
                    waiting.append(j)
                tiles_34[j] -= 1

            tiles_34[i] += 1

            if waiting:
                results.append(DiscardOption(player=self.player,
                                             tile_to_discard=i,
                                             waiting=waiting,
                                             tiles_count=self.count_tiles(waiting, tiles_34)))

        return results, shanten

    def count_tiles(self, waiting, tiles):
        n = 0
        for item in waiting:
            n += 4 - tiles[item]
            n -= self.player.table.revealed_tiles[item]
        return n

    def try_to_call_meld(self, tile, is_kamicha_discard):
        if not self.current_strategy:
            return None, None, None

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
            TanyaoStrategy(BaseStrategy.TANYAO, self.player),
        ]

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

    def chose_tile_to_discard(self, results, closed_hand):
        # - is important for x.tiles_count
        # in that case we will discard tile that will give for us more tiles
        # to complete a hand
        results = sorted(results, key=lambda x: (-x.tiles_count, x.value))
        selected_tile = results[0]
        self.waiting = selected_tile.waiting
        return selected_tile.find_tile_in_hand(closed_hand)

    def estimate_hand_value(self, win_tile):
        """
        :param win_tile: 36 tile format
        :return:
        """
        win_tile *= 4
        tiles = self.player.tiles + [win_tile]
        result = self.finished_hand.estimate_hand_value(tiles=tiles,
                                                        win_tile=win_tile,
                                                        is_tsumo=False,
                                                        is_riichi=False,
                                                        is_dealer=self.player.is_dealer,
                                                        open_sets=self.player.meld_tiles,
                                                        player_wind=self.player.player_wind,
                                                        round_wind=self.player.table.round_wind,
                                                        dora_indicators=self.player.table.dora_indicators)
        return result

    @property
    def valued_honors(self):
        return [CHUN, HAKU, HATSU, self.player.table.round_wind, self.player.player_wind]

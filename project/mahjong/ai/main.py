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
from mahjong.hand import HandDivider
from mahjong.tile import TilesConverter

logger = logging.getLogger('ai')


class MainAI(BaseAI):
    version = '0.1.0'

    agari = None
    shanten = None
    defence = None
    hand_divider = None
    previous_shanten = 7

    current_strategy = None

    def __init__(self, table, player):
        super(MainAI, self).__init__(table, player)

        self.agari = Agari()
        self.shanten = Shanten()
        self.defence = Defence(table)
        self.hand_divider = HandDivider()
        self.previous_shanten = 7
        self.current_strategy = None

    def erase_state(self):
        self.current_strategy = None

    def discard_tile(self):
        results, shanten = self.calculate_outs(self.player.tiles,
                                               self.player.closed_hand,
                                               self.player.is_open_hand)
        self.previous_shanten = shanten

        if shanten == 0:
            self.player.in_tempai = True

        # we are win!
        if shanten == Shanten.AGARI_STATE:
            return Shanten.AGARI_STATE

        # we are in agari state, but we can't win because we don't have yaku
        # in that case let's do tsumogiri
        if not results:
            return self.player.last_draw

        # current strategy can affect on our discard options
        if self.current_strategy:
            results = self.current_strategy.determine_what_to_discard(self.player.closed_hand,
                                                                      results,
                                                                      shanten,
                                                                      False)

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

    def count_tiles(self, raw_data, tiles):
        n = 0
        for i in range(0, len(raw_data)):
            n += 4 - tiles[raw_data[i]]
        return n

    def try_to_call_meld(self, tile, is_kamicha_discard):
        if not self.current_strategy:
            return None, None, None

        return self.current_strategy.try_to_call_meld(tile, is_kamicha_discard)

    def determine_strategy(self):
        # for already opened hand we don't need to give up on selected strategy
        if self.player.is_open_hand:
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
        results = sorted(results, key=lambda x: x.tiles_count, reverse=True)
        return results[0].find_tile_in_hand(closed_hand)

    @property
    def valued_honors(self):
        return [CHUN, HAKU, HATSU, self.player.table.round_wind, self.player.player_wind]

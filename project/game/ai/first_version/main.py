# -*- coding: utf-8 -*-
import copy
import utils.decisions_constants as log

from mahjong.agari import Agari
from mahjong.constants import AKA_DORA_LIST, DISPLAY_WINDS
from mahjong.hand_calculating.divider import HandDivider
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.meld import Meld
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter
from mahjong.utils import is_pon

from game.ai.base.main import InterfaceAI
from game.ai.first_version.defence.main import DefenceHandler
from game.ai.first_version.hand_builder import HandBuilder
from game.ai.first_version.riichi import Riichi
from game.ai.first_version.strategies.chiitoitsu import ChiitoitsuStrategy
from game.ai.first_version.strategies.chinitsu import ChinitsuStrategy
from game.ai.first_version.strategies.formal_tempai import FormalTempaiStrategy
from game.ai.first_version.strategies.honitsu import HonitsuStrategy
from game.ai.first_version.strategies.main import BaseStrategy
from game.ai.first_version.strategies.tanyao import TanyaoStrategy
from game.ai.first_version.strategies.yakuhai import YakuhaiStrategy
from utils.decisions_logger import DecisionsLogger


class ImplementationAI(InterfaceAI):
    version = '0.4.0-dev'

    agari = None
    shanten_calculator = None
    defence = None
    riichi = None
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
        self.hand_builder = HandBuilder(player, self)

        self.erase_state()

    def erase_state(self):
        self.shanten = 7
        self.ukeire = 0
        self.ukeire_second = 0
        self.in_defence = False
        self.waiting = None

        self.current_strategy = None
        self.last_discard_option = None
        self.use_chitoitsu = False

        self.hand_cache = {}

    def init_hand(self):
        DecisionsLogger.debug(log.INIT_HAND, context=[
            'Round  wind: {}'.format(DISPLAY_WINDS[self.table.round_wind_tile]),
            'Player wind: {}'.format(DISPLAY_WINDS[self.player.player_wind]),
            'Hand: {}'.format(self.player.format_hand_for_print()),
        ])

        # it will set correct hand shanten number and ukeire to the new hand
        # tile will not be removed from the hand
        self.discard_tile(None, print_log=False)
        self.player.in_tempai = False

        # Let's decide what we will do with our hand (like open for tanyao and etc.)
        self.determine_strategy(self.player.tiles)

    def draw_tile(self, tile_136):
        self.determine_strategy(self.player.tiles)

    def discard_tile(self, discard_tile, print_log=True):
        # we called meld and we had discard tile that we wanted to discard
        if discard_tile is not None:
            if not self.last_discard_option:
                return discard_tile

            return self.hand_builder.process_discard_option(self.last_discard_option, self.player.closed_hand, True)

        return self.hand_builder.discard_tile(
            self.player.tiles,
            self.player.closed_hand,
            self.player.melds,
            print_log
        )

    def try_to_call_meld(self, tile_136, is_kamicha_discard):
        tiles_136 = self.player.tiles[:] + [tile_136]
        self.determine_strategy(tiles_136)

        if not self.current_strategy:
            return None, None

        tiles_34 = TilesConverter.to_34_array(tiles_136)
        previous_shanten = self.shanten_calculator.calculate_shanten(
            tiles_34,
            self.player.meld_34_tiles,
            chiitoitsu=self.use_chitoitsu
        )

        if previous_shanten == Shanten.AGARI_STATE and not self.current_strategy.can_meld_into_agari():
            return None, None

        meld, discard_option = self.current_strategy.try_to_call_meld(tile_136, is_kamicha_discard, tiles_136)
        if discard_option:
            self.last_discard_option = discard_option

            DecisionsLogger.debug(log.MELD_CALL, 'Try to call meld', context=[
                'Hand: {}'.format(self.player.format_hand_for_print(tile_136)),
                'Meld: {}'.format(meld),
                'Discard after meld: {}'.format(discard_option)
            ])

        return meld, discard_option

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
                DecisionsLogger.debug(
                    log.STRATEGY_ACTIVATE,
                    context=self.current_strategy,
                )

        if not self.current_strategy and old_strategy:
            DecisionsLogger.debug(log.STRATEGY_DROP, context=old_strategy)

        return self.current_strategy and True or False

    def estimate_hand_value(self, win_tile, tiles=None, call_riichi=False, is_tsumo=False):
        """
        :param win_tile: 34 tile format
        :param tiles:
        :param call_riichi:
        :param is_tsumo
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
            round_wind=self.player.table.round_wind_tile,
            has_aka_dora=self.player.table.has_aka_dora,
            has_open_tanyao=self.player.table.has_open_tanyao,
            is_tsumo=is_tsumo,
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

        melds_34 = copy.copy(self.player.meld_34_tiles)
        tiles = copy.copy(self.player.tiles)
        closed_hand_tiles = copy.copy(self.player.closed_hand)

        # we can try to call closed meld
        if closed_hand_34[tile_34] == 3:
            if open_kan or from_riichi:
                # this 4 tiles can only be used in kan, no other options
                previous_waiting, previous_shanten = self.hand_builder.calculate_waits(tiles_34, melds_34)
                previous_waits_cnt = self.hand_builder.count_tiles(previous_waiting, closed_hand_34)

                # shanten calculator doesn't like working with kans, so we pretend it's a pon
                melds_34 += [[tile_34, tile_34, tile_34]]
                closed_hand_34[tile_34] = 0

                new_waiting, new_shanten = self.hand_builder.calculate_waits(tiles_34, melds_34)
                new_waits_cnt = self.hand_builder.count_tiles(new_waiting, closed_hand_34)
            else:
                # if we can use or tile in the hand for the forms other than KAN
                tiles.append(tile)

                closed_hand_tiles.append(tile)
                closed_hand_34[tile_34] += 1

                previous_results, previous_shanten = self.hand_builder.find_discard_options(
                    tiles,
                    closed_hand_tiles,
                    self.player.melds
                )

                previous_results = [x for x in previous_results if x.shanten == previous_shanten]

                # it is possible that we don't have results here
                # when we are in agari state (but without yaku)
                if not previous_results:
                    return None

                previous_waits_cnt = sorted(previous_results, key=lambda x: -x.ukeire)[0].ukeire

                # shanten calculator doesn't like working with kans, so we pretend it's a pon
                closed_hand_34[tile_34] = 0
                melds_34 += [[tile_34, tile_34, tile_34]]

                new_waiting, new_shanten = self.hand_builder.calculate_waits(tiles_34, melds_34)
                new_waits_cnt = self.hand_builder.count_tiles(new_waiting, closed_hand_34)

            # it is not possible to reduce number of shanten by calling a kan
            assert new_shanten >= previous_shanten

            # if shanten number is the same, we should only call kan if ukeire didn't become worse
            if new_shanten == previous_shanten:
                # we cannot improve ukeire by calling kan (not considering the tile we drew from the dead wall)
                assert new_waits_cnt <= previous_waits_cnt
                if new_waits_cnt == previous_waits_cnt:
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
            DecisionsLogger.debug(log.DEFENCE_ACTIVATE)

    @property
    def enemy_players(self):
        """
        Return list of players except our bot
        """
        return self.player.table.players[1:]

from typing import List, Optional

import utils.decisions_constants as log
from game.ai.defence.main import TileDangerHandler
from game.ai.hand_builder import HandBuilder
from game.ai.helpers.kabe import Kabe
from game.ai.helpers.suji import Suji
from game.ai.riichi import Riichi
from game.ai.strategies.chiitoitsu import ChiitoitsuStrategy
from game.ai.strategies.chinitsu import ChinitsuStrategy
from game.ai.strategies.formal_tempai import FormalTempaiStrategy
from game.ai.strategies.honitsu import HonitsuStrategy
from game.ai.strategies.main import BaseStrategy
from game.ai.strategies.tanyao import TanyaoStrategy
from game.ai.strategies.yakuhai import YakuhaiStrategy
from mahjong.agari import Agari
from mahjong.constants import AKA_DORA_LIST, DISPLAY_WINDS
from mahjong.hand_calculating.divider import HandDivider
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter
from mahjong.utils import is_pon
from utils.cache import build_estimate_hand_value_cache_key, build_shanten_cache_key
from utils.decisions_logger import DecisionsLogger, MeldPrint


class MahjongAI:
    version = "0.5.0-dev"

    agari = None
    shanten_calculator = None
    defence = None
    riichi = None
    hand_divider = None
    finished_hand = None

    shanten = 7
    ukeire = 0
    ukeire_second = 0
    waiting = None

    current_strategy = None
    last_discard_option = None

    hand_cache_shanten = {}
    hand_cache_estimation = {}

    def __init__(self, player):
        self.player = player
        self.table = player.table

        self.agari = Agari()
        self.shanten_calculator = Shanten()
        self.defence = TileDangerHandler(player)
        self.riichi = Riichi(player)
        self.hand_divider = HandDivider()
        self.finished_hand = HandCalculator()
        self.hand_builder = HandBuilder(player, self)

        self.suji = Suji(player)
        self.kabe = Kabe(player)

        self.erase_state()

    def erase_state(self):
        self.shanten = 7
        self.ukeire = 0
        self.ukeire_second = 0
        self.waiting = None

        self.current_strategy = None
        self.last_discard_option = None

        self.hand_cache_shanten = {}
        self.hand_cache_estimation = {}

    def init_hand(self):
        DecisionsLogger.debug(
            log.INIT_HAND,
            context=[
                f"Round  wind: {DISPLAY_WINDS[self.table.round_wind_tile]}",
                f"Player wind: {DISPLAY_WINDS[self.player.player_wind]}",
                f"Hand: {self.player.format_hand_for_print()}",
            ],
        )

        self.shanten, _ = self.hand_builder.calculate_shanten_and_decide_hand_structure(
            TilesConverter.to_34_array(self.player.tiles)
        )

    def draw_tile(self, tile_136):
        self.determine_strategy(self.player.tiles)

    def discard_tile(self, discard_tile):
        # we called meld and we had discard tile that we wanted to discard
        if discard_tile is not None:
            if not self.last_discard_option:
                return discard_tile

            return self.hand_builder.process_discard_option(self.last_discard_option, self.player.closed_hand, True)

        return self.hand_builder.discard_tile(self.player.tiles, self.player.closed_hand, self.player.melds)

    def try_to_call_meld(self, tile_136, is_kamicha_discard):
        tiles_136_previous = self.player.tiles[:]
        tiles_136 = tiles_136_previous + [tile_136]
        self.determine_strategy(tiles_136)

        if not self.current_strategy:
            DecisionsLogger.debug(log.MELD_DEBUG, "We don't have active strategy. Abort melding.")
            return None, None

        tiles_34_previous = TilesConverter.to_34_array(tiles_136_previous)
        previous_shanten, _ = self.hand_builder.calculate_shanten_and_decide_hand_structure(
            tiles_34_previous, self.player.meld_34_tiles
        )

        if previous_shanten == Shanten.AGARI_STATE and not self.current_strategy.can_meld_into_agari():
            return None, None

        meld, discard_option = self.current_strategy.try_to_call_meld(tile_136, is_kamicha_discard, tiles_136)
        if discard_option:
            self.last_discard_option = discard_option

            DecisionsLogger.debug(
                log.MELD_CALL,
                "We decided to open hand",
                context=[
                    f"Hand: {self.player.format_hand_for_print(tile_136)}",
                    f"Meld: {meld.serialize()}",
                    f"Discard after meld: {discard_option.serialize()}",
                ],
            )

        return meld, discard_option

    def determine_strategy(self, tiles_136):
        # for already opened hand we don't need to give up on selected strategy
        if self.player.is_open_hand and self.current_strategy:
            return False

        old_strategy = self.current_strategy
        self.current_strategy = None

        # order is important, we add strategies with the highest priority first
        strategies = []

        if self.player.table.has_open_tanyao:
            strategies.append(TanyaoStrategy(BaseStrategy.TANYAO, self.player))

        strategies.append(YakuhaiStrategy(BaseStrategy.YAKUHAI, self.player))
        strategies.append(HonitsuStrategy(BaseStrategy.HONITSU, self.player))
        strategies.append(ChinitsuStrategy(BaseStrategy.CHINITSU, self.player))

        strategies.append(ChiitoitsuStrategy(BaseStrategy.CHIITOITSU, self.player))
        strategies.append(FormalTempaiStrategy(BaseStrategy.FORMAL_TEMPAI, self.player))

        for strategy in strategies:
            if strategy.should_activate_strategy(tiles_136):
                self.current_strategy = strategy
                break

        if self.current_strategy and (not old_strategy or self.current_strategy.type != old_strategy.type):
            DecisionsLogger.debug(
                log.STRATEGY_ACTIVATE,
                context=self.current_strategy,
            )

        if not self.current_strategy and old_strategy:
            DecisionsLogger.debug(log.STRATEGY_DROP, context=old_strategy)

        return self.current_strategy and True or False

    def estimate_hand_value_or_get_from_cache(self, win_tile_34, tiles=None, call_riichi=False, is_tsumo=False):
        win_tile_136 = win_tile_34 * 4

        # we don't need to think, that our waiting is aka dora
        if win_tile_136 in AKA_DORA_LIST:
            win_tile_136 += 1

        if not tiles:
            tiles = self.player.tiles[:]

        tiles += [win_tile_136]

        cache_key = build_estimate_hand_value_cache_key(
            tiles, call_riichi, is_tsumo, self.player.melds, self.player.table.dora_indicators
        )
        if self.hand_cache_estimation.get(cache_key):
            return self.hand_cache_estimation.get(cache_key)

        config = HandConfig(
            is_riichi=call_riichi,
            player_wind=self.player.player_wind,
            round_wind=self.player.table.round_wind_tile,
            is_tsumo=is_tsumo,
            options=OptionalRules(
                has_aka_dora=self.player.table.has_aka_dora,
                has_open_tanyao=self.player.table.has_open_tanyao,
            ),
        )

        result = self.finished_hand.estimate_hand_value(
            tiles,
            win_tile_136,
            self.player.melds,
            self.player.table.dora_indicators,
            config,
        )

        self.hand_cache_estimation[cache_key] = result
        return result

    def estimate_weighted_mean_hand_value(self, discard_option):
        weighted_hand_cost = 0
        number_of_tiles = 0
        for waiting in discard_option.waiting:
            tiles = self.player.tiles[:]
            tiles.remove(discard_option.find_tile_in_hand(self.player.closed_hand))

            hand_cost = self.estimate_hand_value_or_get_from_cache(
                waiting, tiles=tiles, call_riichi=not self.player.is_open_hand, is_tsumo=True
            )

            if not hand_cost.cost:
                continue

            weighted_hand_cost += (
                hand_cost.cost["main"] + 2 * hand_cost.cost["additional"]
            ) * discard_option.wait_to_ukeire[waiting]
            number_of_tiles += discard_option.wait_to_ukeire[waiting]

        return number_of_tiles and int(weighted_hand_cost / number_of_tiles) or 0

    def should_call_riichi(self):
        should_riichi = self.riichi.should_call_riichi()

        if should_riichi:
            DecisionsLogger.debug(log.RIICHI, "Decided to riichi.")
        else:
            DecisionsLogger.debug(log.RIICHI, "Decided to stay damaten.")

        return should_riichi

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

        melds_34 = self.player.meld_34_tiles[:]
        tiles = self.player.tiles[:]
        closed_hand_tiles = self.player.closed_hand[:]

        new_shanten = 0
        previous_shanten = 0
        new_waits_count = 0
        previous_waits_count = 0

        # let's check can we upgrade opened pon to the kan
        pon_melds = [x for x in self.player.meld_34_tiles if is_pon(x)]
        has_shouminkan_candidate = False
        for meld in pon_melds:
            # tile is equal to our already opened pon
            if tile_34 in meld:
                has_shouminkan_candidate = True

                tiles.append(tile)
                closed_hand_tiles.append(tile)

                previous_shanten, previous_waits_count = self._calculate_shanten_for_kan(
                    tiles, closed_hand_tiles, self.player.melds
                )

                tiles_34 = TilesConverter.to_34_array(tiles)
                tiles_34[tile_34] -= 1

                new_waiting, new_shanten = self.hand_builder.calculate_waits(
                    tiles_34, self.player.meld_34_tiles, use_chiitoitsu=False
                )
                new_waits_count = self.hand_builder.count_tiles(new_waiting, closed_hand_34)

        if not has_shouminkan_candidate:
            # we don't have enough tiles in the hand
            if closed_hand_34[tile_34] != 3:
                return None

            if open_kan or from_riichi:
                # this 4 tiles can only be used in kan, no other options
                previous_waiting, previous_shanten = self.hand_builder.calculate_waits(
                    tiles_34, melds_34, use_chiitoitsu=False
                )
                previous_waits_count = self.hand_builder.count_tiles(previous_waiting, closed_hand_34)
            else:
                tiles.append(tile)
                closed_hand_tiles.append(tile)

                previous_shanten, previous_waits_count = self._calculate_shanten_for_kan(
                    tiles, closed_hand_tiles, self.player.melds
                )

            # shanten calculator doesn't like working with kans, so we pretend it's a pon
            melds_34 += [[tile_34, tile_34, tile_34]]
            new_waiting, new_shanten = self.hand_builder.calculate_waits(tiles_34, melds_34, use_chiitoitsu=False)

            closed_hand_34[tile_34] = 4
            new_waits_count = self.hand_builder.count_tiles(new_waiting, closed_hand_34)

        # it is possible that we don't have results here
        # when we are in agari state (but without yaku)
        if previous_shanten is None:
            return None

        # it is not possible to reduce number of shanten by calling a kan
        assert new_shanten >= previous_shanten

        # if shanten number is the same, we should only call kan if ukeire didn't become worse
        if new_shanten == previous_shanten:
            # we cannot improve ukeire by calling kan (not considering the tile we drew from the dead wall)
            assert new_waits_count <= previous_waits_count

            if new_waits_count == previous_waits_count:
                kan_type = has_shouminkan_candidate and MeldPrint.SHOUMINKAN or MeldPrint.KAN
                DecisionsLogger.debug(log.KAN_DEBUG, f"Open kan type='{kan_type}'")
                return kan_type

        return None

    def should_call_win(self, tile, enemy_seat):
        return True

    def enemy_called_riichi(self, enemy_seat):
        """
        After enemy riichi we had to check will we fold or not
        it is affect open hand decisions
        :return:
        """
        pass

    def calculate_shanten_or_get_from_cache(
        self, tiles_34: List[int], open_sets_34: Optional[List[List[int]]], use_chiitoitsu: bool
    ):
        """
        Sometimes we are calculating shanten for the same hand multiple times
        to save some resources let's cache previous calculations
        """
        key = build_shanten_cache_key(tiles_34, open_sets_34, use_chiitoitsu)
        if key in self.hand_cache_shanten:
            return self.hand_cache_shanten[key]
        if use_chiitoitsu and not open_sets_34:
            result = self.shanten_calculator.calculate_shanten_for_chiitoitsu_hand(tiles_34)
        else:
            result = self.shanten_calculator.calculate_shanten_for_regular_hand(
                tiles_34,
                open_sets_34,
            )
        self.hand_cache_shanten[key] = result
        return result

    @property
    def enemy_players(self):
        """
        Return list of players except our bot
        """
        return self.player.table.players[1:]

    def _calculate_shanten_for_kan(self, tiles, closed_hand_tiles, melds):
        previous_results, previous_shanten = self.hand_builder.find_discard_options(tiles, closed_hand_tiles, melds)

        previous_results = [x for x in previous_results if x.shanten == previous_shanten]

        # it is possible that we don't have results here
        # when we are in agari state (but without yaku)
        if not previous_results:
            return None, None

        previous_waits_cnt = sorted(previous_results, key=lambda x: -x.ukeire)[0].ukeire

        return previous_shanten, previous_waits_cnt

import utils.decisions_constants as log
from game.ai.strategies_v2.chinitsu import ChinitsuStrategy
from game.ai.strategies_v2.common_open_tempai import CommonOpenTempaiStrategy
from game.ai.strategies_v2.formal_tempai import FormalTempaiStrategy
from game.ai.strategies_v2.honitsu import HonitsuStrategy
from game.ai.strategies_v2.main import BaseStrategy
from game.ai.strategies_v2.tanyao import TanyaoStrategy
from game.ai.strategies_v2.yakuhai import YakuhaiStrategy
from mahjong.shanten import Shanten
from mahjong.tile import TilesConverter


class OpenHandHandlerV2:
    player = None
    current_strategy = None
    last_discard_option = None

    def __init__(self, player):
        self.player = player

    def determine_strategy(self, tiles_136, meld_tile=None):
        # for already opened hand we don't need to give up on selected strategy
        if self.player.is_open_hand and self.current_strategy:
            return False

        old_strategy = self.current_strategy
        self.current_strategy = None

        # order is important, we add strategies with the highest priority first
        strategies = []

        # first priority
        if self.player.table.has_open_tanyao:
            strategies.append(TanyaoStrategy(BaseStrategy.TANYAO, self.player))

        # second priority
        strategies.append(HonitsuStrategy(BaseStrategy.HONITSU, self.player))
        strategies.append(ChinitsuStrategy(BaseStrategy.CHINITSU, self.player))

        # third priority
        strategies.append(YakuhaiStrategy(BaseStrategy.YAKUHAI, self.player))

        # fourth priority
        strategies.append(FormalTempaiStrategy(BaseStrategy.FORMAL_TEMPAI, self.player))
        strategies.append(CommonOpenTempaiStrategy(BaseStrategy.COMMON_OPEN_TEMPAI, self.player))

        for strategy in strategies:
            if strategy.should_activate_strategy(tiles_136, meld_tile=meld_tile):
                self.current_strategy = strategy
                break

        if self.current_strategy and (not old_strategy or self.current_strategy.type != old_strategy.type):
            self.player.logger.debug(
                log.STRATEGY_ACTIVATE,
                context=self.current_strategy,
            )

        if not self.current_strategy and old_strategy:
            self.player.logger.debug(log.STRATEGY_DROP, context=old_strategy)

        return self.current_strategy and True or False

    def try_to_call_meld(self, tile_136, is_kamicha_discard):
        tiles_136_previous = self.player.tiles[:]
        closed_hand_136_previous = self.player.closed_hand[:]
        tiles_136 = tiles_136_previous + [tile_136]
        self.determine_strategy(tiles_136, meld_tile=tile_136)

        if not self.current_strategy:
            self.player.logger.debug(log.MELD_DEBUG, "We don't have active strategy. Abort melding.")
            return None, None

        closed_hand_34_previous = TilesConverter.to_34_array(closed_hand_136_previous)
        previous_shanten, _ = self.player.ai.hand_builder.calculate_shanten_and_decide_hand_structure(
            closed_hand_34_previous
        )

        if previous_shanten == Shanten.AGARI_STATE and not self.current_strategy.can_meld_into_agari():
            return None, None

        meld, discard_option = self.current_strategy.try_to_call_meld(tile_136, is_kamicha_discard, tiles_136)
        if discard_option:
            self.last_discard_option = discard_option

            self.player.logger.debug(
                log.MELD_CALL,
                "We decided to open hand",
                context=[
                    f"Hand: {self.player.format_hand_for_print(tile_136)}",
                    f"Meld: {meld.serialize()}",
                    f"Discard after meld: {discard_option.serialize()}",
                ],
            )

        return meld, discard_option

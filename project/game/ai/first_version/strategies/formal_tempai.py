# -*- coding: utf-8 -*-
from mahjong.utils import plus_dora, is_aka_dora

from game.ai.first_version.strategies.main import BaseStrategy


class FormalTempaiStrategy(BaseStrategy):

    def should_activate_strategy(self):
        """
        When we get closer to the end of the round, we start to consider
        going for formal tempai.
        :return: boolean
        """

        result = super(FormalTempaiStrategy, self).should_activate_strategy()
        if not result:
            return False

        # if we already in tempai, we don't need this strategy
        if self.player.in_tempai:
            return False

        # it's too early to go for formal tempai before 11th turn
        if self.player.round_step < 11:
            return False

        # it's 11th turn or later and we still have 3 shanten or more,
        # let's try to go for formal tempai at least
        if self.player.ai.previous_shanten >= 3:
            return True

        dora_count = sum([plus_dora(x, self.player.table.dora_indicators) for x in self.player.tiles])
        dora_count += sum([1 for x in self.player.tiles if is_aka_dora(x, self.player.table.has_open_tanyao)])

        if self.player.ai.previous_shanten == 2:
            if dora_count < 2:
                # having 0 or 1 dora and 2 shanten, let's go for formal tempai
                # starting from 11th turn
                return True
            # having 2 or more doras and 2 shanten, let's go for formal
            # tempai starting from 12th turn
            return self.player.round_step >= 12

        # for 1 shanten we check number of doras and ukeire to determine
        # correct time to go for formal tempai
        if self.player.ai.previous_shanten == 1:
            if dora_count == 0:
                if self.player.ai.ukeire <= 16:
                    return True

                if self.player.ai.ukeire <= 28:
                    return self.player.round_step >= 12

                return self.player.round_step >= 13

            if dora_count == 1:
                if self.player.ai.ukeire <= 16:
                    return self.player.round_step >= 12

                if self.player.ai.ukeire <= 28:
                    return self.player.round_step >= 13

                return self.player.round_step >= 14

            if self.player.ai.ukeire <= 16:
                return self.player.round_step >= 13

            return self.player.round_step >= 14

        # we actually never reach here
        return False

    def is_tile_suitable(self, tile):
        """
        All tiles are suitable for formal tempai.
        :param tile: 136 tiles format
        :return: True
        """
        return True

from game.ai.strategies.main import BaseStrategy


class FormalTempaiStrategy(BaseStrategy):
    def should_activate_strategy(self, tiles_136, meld_tile=None):
        """
        When we get closer to the end of the round, we start to consider
        going for formal tempai.
        """

        result = super(FormalTempaiStrategy, self).should_activate_strategy(tiles_136)
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
        if self.player.ai.shanten >= 3:
            return True

        if self.player.ai.shanten == 2:
            if self.dora_count_total < 2:
                # having 0 or 1 dora and 2 shanten, let's go for formal tempai
                # starting from 11th turn
                return True
            # having 2 or more doras and 2 shanten, let's go for formal
            # tempai starting from 12th turn
            return self.player.round_step >= 12

        # for 1 shanten we check number of doras and ukeire to determine
        # correct time to go for formal tempai
        if self.player.ai.shanten == 1:
            if self.dora_count_total == 0:
                if self.player.ai.ukeire <= 16:
                    return True

                if self.player.ai.ukeire <= 28:
                    return self.player.round_step >= 12

                return self.player.round_step >= 13

            if self.dora_count_total == 1:
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

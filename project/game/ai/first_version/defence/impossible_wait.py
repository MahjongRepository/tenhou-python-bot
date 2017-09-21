# -*- coding: utf-8 -*-
from mahjong.constants import HONOR_INDICES

from game.ai.first_version.defence.defence import Defence, DefenceTile


class ImpossibleWait(Defence):

    def find_tiles_to_discard(self, _):
        """
        Impossible waits: fourth honor
        Pair waits: third honor
        """

        results = []
        for x in HONOR_INDICES:
            if self.player.total_tiles(x, self.defence.hand_34) == 4:
                results.append(DefenceTile(x, DefenceTile.SAFE))

            if self.player.total_tiles(x, self.defence.hand_34) == 3:
                results.append(DefenceTile(x, DefenceTile.ALMOST_SAFE_TILE))

        return results

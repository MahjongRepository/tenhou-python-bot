from typing import Optional

import utils.decisions_constants as log
from mahjong.tile import TilesConverter
from mahjong.utils import is_pon
from utils.decisions_logger import MeldPrint


class Kan:
    def __init__(self, player):
        self.player = player

    # TODO for better readability need to separate it on three methods:
    # should_call_closed_kan, should_call_open_kan, should_call_shouminkan
    def should_call_kan(self, tile_136: int, open_kan: bool, from_riichi=False) -> Optional[str]:
        """
        Method will decide should we call a kan, or upgrade pon to kan
        :return: kan type
        """

        # we can't call kan on the latest tile
        if self.player.table.count_of_remaining_tiles <= 1:
            return None

        if self.player.config.FEATURE_DEFENCE_ENABLED:
            threats = self.player.ai.defence.get_threatening_players()
        else:
            threats = []

        if open_kan:
            # we don't want to start open our hand from called kan
            if not self.player.is_open_hand:
                return None

            # there is no sense to call open kan when we are not in tempai
            if not self.player.in_tempai:
                return None

            # we have a bad wait, rinshan chance is low
            if len(self.player.ai.waiting) < 2 or self.player.ai.ukeire < 5:
                return None

            # there are threats, open kan is probably a bad idea
            if threats:
                return None

        tile_34 = tile_136 // 4
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)

        # save original hand state
        original_tiles = self.player.tiles[:]

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

                closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
                previous_shanten, previous_waits_count = self._calculate_shanten_for_kan()
                self.player.tiles = original_tiles[:]

                closed_hand_34[tile_34] -= 1
                tiles_34[tile_34] -= 1
                new_waiting, new_shanten = self.player.ai.hand_builder.calculate_waits(
                    closed_hand_34, tiles_34, use_chiitoitsu=False
                )
                new_waits_count = self.player.ai.hand_builder.count_tiles(new_waiting, closed_hand_34)

        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
        if not open_kan and not has_shouminkan_candidate and closed_hand_34[tile_34] != 4:
            return None

        if open_kan and closed_hand_34[tile_34] != 3:
            return None

        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)

        if not has_shouminkan_candidate:
            if open_kan:
                # this 4 tiles can only be used in kan, no other options
                previous_waiting, previous_shanten = self.player.ai.hand_builder.calculate_waits(
                    closed_hand_34, tiles_34, use_chiitoitsu=False
                )
                previous_waits_count = self.player.ai.hand_builder.count_tiles(previous_waiting, closed_hand_34)
            elif from_riichi:
                # hand did not change since we last recalculated it, and the only thing we can do is to call kan
                previous_waits_count = self.player.ai.ukeire
            else:
                previous_shanten, previous_waits_count = self._calculate_shanten_for_kan()
                self.player.tiles = original_tiles[:]

            closed_hand_34[tile_34] = 0
            new_waiting, new_shanten = self.player.ai.hand_builder.calculate_waits(
                closed_hand_34, tiles_34, use_chiitoitsu=False
            )

            closed_hand_34[tile_34] = 4
            new_waits_count = self.player.ai.hand_builder.count_tiles(new_waiting, closed_hand_34)

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
                if kan_type == MeldPrint.SHOUMINKAN:
                    if threats:
                        # there are threats and we are not even in tempai - let's not do shouminkan
                        if not self.player.in_tempai:
                            return None

                        # there are threats and our tempai is weak, let's not do shouminkan
                        if len(self.player.ai.waiting) < 2 or self.player.ai.ukeire < 3:
                            return None
                    else:
                        # no threats, but too many shanten, let's not do shouminkan
                        if new_shanten > 2:
                            return None

                        # no threats, and ryanshanten, but ukeire is meh, let's not do shouminkan
                        if new_shanten == 2:
                            if self.player.ai.ukeire < 16:
                                return None

                self.player.logger.debug(log.KAN_DEBUG, f"Open kan type='{kan_type}'")
                return kan_type

        return None

    def _calculate_shanten_for_kan(self):
        previous_results, previous_shanten = self.player.ai.hand_builder.find_discard_options()

        previous_results = [x for x in previous_results if x.shanten == previous_shanten]

        # it is possible that we don't have results here
        # when we are in agari state (but without yaku)
        if not previous_results:
            return None, None

        previous_waits_cnt = sorted(previous_results, key=lambda x: -x.ukeire)[0].ukeire

        return previous_shanten, previous_waits_cnt

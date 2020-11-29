import utils.decisions_constants as log
from game.ai.strategies.main import BaseStrategy
from mahjong.constants import HONOR_INDICES, TERMINAL_INDICES
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor, is_tile_strictly_isolated
from utils.test_helpers import tiles_to_string


class TanyaoStrategy(BaseStrategy):
    min_shanten = 3
    not_suitable_tiles = TERMINAL_INDICES + HONOR_INDICES

    def get_open_hand_han(self):
        return 1

    def should_activate_strategy(self, tiles_136, meld_tile=None):
        """
        Tanyao hand is a hand without terminal and honor tiles, to achieve this
        we will use different approaches
        :return: boolean
        """

        result = super(TanyaoStrategy, self).should_activate_strategy(tiles_136)
        if not result:
            return False

        tiles = TilesConverter.to_34_array(self.player.tiles)

        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
        isolated_tiles = [
            x // 4 for x in self.player.tiles if is_tile_strictly_isolated(closed_hand_34, x // 4) or is_honor(x // 4)
        ]

        count_of_terminal_pon_sets = 0
        count_of_terminal_pairs = 0
        count_of_valued_pairs = 0
        count_of_not_suitable_tiles = 0
        count_of_not_suitable_not_isolated_tiles = 0
        for x in range(0, 34):
            tile = tiles[x]
            if not tile:
                continue

            if x in self.not_suitable_tiles and tile == 3:
                count_of_terminal_pon_sets += 1

            if x in self.not_suitable_tiles and tile == 2:
                count_of_terminal_pairs += 1

                if x in self.player.valued_honors:
                    count_of_valued_pairs += 1

            if x in self.not_suitable_tiles:
                count_of_not_suitable_tiles += tile

            if x in self.not_suitable_tiles and x not in isolated_tiles:
                count_of_not_suitable_not_isolated_tiles += tile

        # we have too much terminals and honors
        if count_of_not_suitable_tiles >= 5:
            return False

        # if we already have pon of honor\terminal tiles
        # we don't need to open hand for tanyao
        if count_of_terminal_pon_sets > 0:
            return False

        # with valued pair (yakuhai wind or dragon)
        # we don't need to go for tanyao
        if count_of_valued_pairs > 0:
            return False

        # one pair is ok in tanyao pair
        # but 2+ pairs can't be suitable
        if count_of_terminal_pairs > 1:
            return False

        # 3 or more not suitable tiles that
        # are not isolated is too much
        if count_of_not_suitable_not_isolated_tiles >= 3:
            return False

        # if we are 1 shanten, even 2 tiles
        # that are not suitable and not isolated
        # is too much
        if count_of_not_suitable_not_isolated_tiles >= 2 and self.player.ai.shanten == 1:
            return False

        # TODO: don't open from good 1-shanten into tanyao 1-shaten with same ukeire or worse

        # 123 and 789 indices
        indices = [[0, 1, 2], [6, 7, 8], [9, 10, 11], [15, 16, 17], [18, 19, 20], [24, 25, 26]]

        for index_set in indices:
            first = tiles[index_set[0]]
            second = tiles[index_set[1]]
            third = tiles[index_set[2]]
            if first >= 1 and second >= 1 and third >= 1:
                return False

        # if we have 2 or more non-central doras
        # we don't want to go for tanyao
        if self.dora_count_not_central >= 2:
            return False

        # if we have less than two central doras
        # let's not consider open tanyao
        if self.dora_count_central < 2:
            return False

        # if we have only two central doras let's
        # wait for 5th turn before opening our hand
        if self.dora_count_central == 2 and self.player.round_step < 5:
            return False

        return True

    def determine_what_to_discard(self, discard_options, hand, open_melds):
        is_open_hand = self.player.is_open_hand

        # our hand is closed, we don't need to discard terminal tiles here
        if not is_open_hand:
            return discard_options

        first_option = sorted(discard_options, key=lambda x: x.shanten)[0]
        shanten = first_option.shanten

        if shanten > 1:
            return super(TanyaoStrategy, self).determine_what_to_discard(discard_options, hand, open_melds)

        results = []
        not_suitable_tiles = []
        for item in discard_options:
            if not self.is_tile_suitable(item.tile_to_discard_136):
                item.had_to_be_discarded = True
                not_suitable_tiles.append(item)
                continue

            # there is no sense to wait 1-4 if we have open hand
            # but let's only avoid atodzuke tiles in tempai, the rest will be dealt with in
            # generic logic
            if item.shanten == 0:
                all_waiting_are_fine = all(
                    [(self.is_tile_suitable(x * 4) or item.wait_to_ukeire[x] == 0) for x in item.waiting]
                )
                if all_waiting_are_fine:
                    results.append(item)

        if not_suitable_tiles:
            return not_suitable_tiles

        # we don't have a choice
        # we had to have on bad wait
        if not results:
            return discard_options

        return results

    def is_tile_suitable(self, tile):
        """
        We can use only simples tiles (2-8) in any suit
        :param tile: 136 tiles format
        :return: True
        """
        tile //= 4
        return tile not in self.not_suitable_tiles

    def validate_meld(self, chosen_meld_dict):
        # if we have already opened our hand, let's go by default riles
        if self.player.is_open_hand:
            return True

        # choose if base method requires us to keep hand closed
        if not super(TanyaoStrategy, self).validate_meld(chosen_meld_dict):
            return False

        # otherwise let's not open hand if that does not improve our ukeire
        closed_tiles_34 = TilesConverter.to_34_array(self.player.closed_hand)
        waiting, shanten = self.player.ai.hand_builder.calculate_waits(
            closed_tiles_34, closed_tiles_34, use_chiitoitsu=False
        )
        wait_to_ukeire = dict(
            zip(waiting, [self.player.ai.hand_builder.count_tiles([x], closed_tiles_34) for x in waiting])
        )
        old_ukeire = sum(wait_to_ukeire.values())
        selected_tile = chosen_meld_dict["discard_tile"]

        logger_context = {
            "hand": tiles_to_string(self.player.closed_hand),
            "meld": chosen_meld_dict,
            "old_shanten": shanten,
            "old_ukeire": old_ukeire,
            "new_shanten": selected_tile.shanten,
            "new_ukeire": selected_tile.ukeire,
        }

        if selected_tile.shanten > shanten:
            self.player.logger.debug(
                log.MELD_DEBUG, "Opening into tanyao increases number of shanten, let's not do that", logger_context
            )
            return False

        if selected_tile.shanten == shanten:
            if old_ukeire >= selected_tile.ukeire:
                self.player.logger.debug(
                    log.MELD_DEBUG,
                    "Opening into tanyao keeps same number of shanten and does not improve ukeire, let's not do that",
                    logger_context,
                )
                return False

            if old_ukeire != 0:
                improvement_percent = ((selected_tile.ukeire - old_ukeire) / old_ukeire) * 100
            else:
                improvement_percent = selected_tile.ukeire * 100

            if improvement_percent < 30:
                self.player.logger.debug(
                    log.MELD_DEBUG,
                    "Opening into tanyao keeps same number of shanten and ukeire improvement is low, don't open",
                    logger_context,
                )
                return False

            self.player.logger.debug(
                log.MELD_DEBUG,
                "Opening into tanyao keeps same number of shanten and ukeire improvement is good, let's call meld",
                logger_context,
            )
            return True

        self.player.logger.debug(
            log.MELD_DEBUG, "Opening into tanyao improves number of shanten, let's call meld", logger_context
        )
        return True

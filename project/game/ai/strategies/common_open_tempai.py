import utils.decisions_constants as log
from game.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter
from utils.test_helpers import tiles_to_string


class CommonOpenTempaiStrategy(BaseStrategy):
    min_shanten = 1

    def should_activate_strategy(self, tiles_136, meld_tile=None):
        """
        We activate this strategy only when we have a chance to meld for good tempai.
        """
        result = super(CommonOpenTempaiStrategy, self).should_activate_strategy(tiles_136)
        if not result:
            return False

        # we only use this strategy for meld opportunities, if it's a self draw, just skip it
        if meld_tile is None:
            assert tiles_136 == self.player.tiles
            return False

        # only go from 1-shanten to tempai with this strategy
        if self.player.ai.shanten != 1:
            return False

        tiles_copy = self.player.closed_hand[:] + [meld_tile]
        tiles_34 = TilesConverter.to_34_array(tiles_copy)
        # we only open for tempai with that strategy
        new_shanten = self.player.ai.calculate_shanten_or_get_from_cache(tiles_34, use_chiitoitsu=False)

        # we always activate this strategy if we have a chance to get tempai
        # then we will validate meld to see if it's really a good one
        return self.player.ai.shanten == 1 and new_shanten == 0

    def is_tile_suitable(self, tile):
        """
        All tiles are suitable for formal tempai.
        :param tile: 136 tiles format
        :return: True
        """
        return True

    def validate_meld(self, chosen_meld_dict):
        # if we have already opened our hand, let's go by default riles
        if self.player.is_open_hand:
            return True

        # choose if base method requires us to keep hand closed
        if not super(CommonOpenTempaiStrategy, self).validate_meld(chosen_meld_dict):
            return False

        selected_tile = chosen_meld_dict["discard_tile"]
        logger_context = {
            "hand": tiles_to_string(self.player.closed_hand),
            "meld": chosen_meld_dict,
            "new_shanten": selected_tile.shanten,
            "new_ukeire": selected_tile.ukeire,
        }

        if selected_tile.shanten != 0:
            self.player.logger.debug(
                log.MELD_DEBUG,
                "Common tempai: for whatever reason we didn't choose discard giving us tempai, so abort melding",
                logger_context,
            )
            return False

        if not selected_tile.tempai_descriptor:
            self.player.logger.debug(
                log.MELD_DEBUG, "Common tempai: no tempai descriptor found, so abort melding", logger_context
            )
            return False

        if selected_tile.ukeire == 0:
            self.player.logger.debug(log.MELD_DEBUG, "Common tempai: 0 ukeire, abort melding", logger_context)
            return False

        if selected_tile.tempai_descriptor["hand_cost"]:
            hand_cost = selected_tile.tempai_descriptor["hand_cost"]
        else:
            hand_cost = selected_tile.tempai_descriptor["cost_x_ukeire"] / selected_tile.ukeire

        if hand_cost == 0:
            self.player.logger.debug(log.MELD_DEBUG, "Common tempai: hand costs nothing, abort melding", logger_context)
            return False

        # maybe we need a special handling due to placement
        # we have already checked that our meld is enough, now let's check that maybe we don't need to aim
        # for higher costs
        enough_cost = 32000
        if self.player.ai.placement.is_oorasu:
            placement = self.player.ai.placement.get_current_placement()
            if placement and placement["place"] == 4:
                enough_cost = self.player.ai.placement.get_minimal_cost_needed_considering_west()

        if self.player.round_step <= 6:
            if hand_cost >= min(7700, enough_cost):
                self.player.logger.debug(log.MELD_DEBUG, "Common tempai: the cost is good, call meld", logger_context)
                return True
        elif self.player.round_step <= 12:
            if self.player.is_dealer:
                if hand_cost >= min(5800, enough_cost):
                    self.player.logger.debug(
                        log.MELD_DEBUG,
                        "Common tempai: the cost is ok for dealer and round step, call meld",
                        logger_context,
                    )
                    return True
            else:
                if hand_cost >= min(3900, enough_cost):
                    self.player.logger.debug(
                        log.MELD_DEBUG,
                        "Common tempai: the cost is ok for non-dealer and round step, call meld",
                        logger_context,
                    )
                    return True
        else:
            self.player.logger.debug(
                log.MELD_DEBUG, "Common tempai: taking any tempai in the late round", logger_context
            )
            return True

        self.player.logger.debug(log.MELD_DEBUG, "Common tempai: the cost is meh, so abort melding", logger_context)
        return False

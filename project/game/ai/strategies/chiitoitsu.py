from game.ai.strategies.main import BaseStrategy
from mahjong.tile import TilesConverter


class ChiitoitsuStrategy(BaseStrategy):
    min_shanten = 2

    def should_activate_strategy(self, tiles_136):
        """
        We can go for chiitoitsu strategy if we have 5 pairs
        """

        result = super(ChiitoitsuStrategy, self).should_activate_strategy(tiles_136)
        if not result:
            return False

        tiles_34 = TilesConverter.to_34_array(self.player.tiles)

        num_pairs = len([x for x in range(0, 34) if tiles_34[x] == 2])
        num_pons = len([x for x in range(0, 34) if tiles_34[x] == 3])

        # for now we don't consider chiitoitsu with less than 5 pair
        if num_pairs < 5:
            return False

        # if we have 5 pairs and tempai, this is obviously not chiitoitsu
        if num_pairs == 5 and self.player.ai.shanten == 0:
            return False

        # for now we won't go for chiitoitsu if we have 5 pairs and pon
        if num_pairs == 5 and num_pons > 0:
            return False

        return True

    def is_tile_suitable(self, tile):
        """
        For chiitoitsu we don't have any limits
        :param tile: 136 tiles format
        :return: True
        """
        return True

    def try_to_call_meld(self, tile, is_kamicha_discard, new_tiles):
        """
        Never meld with chiitoitsu
        :param tile: 136 format tile
        :param is_kamicha_discard: boolean
        :param new_tiles:
        :return: MeldPrint and DiscardOption objects
        """
        return None, None

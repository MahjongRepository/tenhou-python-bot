import utils.decisions_constants as log
from game.ai.strategies.main import BaseStrategy
from mahjong.constants import EAST, SOUTH
from mahjong.tile import TilesConverter
from utils.decisions_logger import MeldPrint


class YakuhaiStrategy(BaseStrategy):
    valued_pairs = None
    has_valued_anko = None

    def __init__(self, strategy_type, player):
        super().__init__(strategy_type, player)

        self.valued_pairs = []
        self.valued_anko = []
        self.has_valued_anko = False
        self.last_chance_calls = []

    def get_open_hand_han(self):
        # kinda rough estimation
        return len(self.valued_anko) + len(self.valued_pairs)

    def should_activate_strategy(self, tiles_136, meld_tile=None):
        """
        We can go for yakuhai strategy if we have at least one yakuhai pair in the hand
        :return: boolean
        """
        result = super(YakuhaiStrategy, self).should_activate_strategy(tiles_136)
        if not result:
            return False

        tiles_34 = TilesConverter.to_34_array(tiles_136)
        player_hand_tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        player_closed_hand_tiles_34 = TilesConverter.to_34_array(self.player.closed_hand)
        self.valued_pairs = [x for x in self.player.valued_honors if player_hand_tiles_34[x] == 2]

        is_double_east_wind = len([x for x in self.valued_pairs if x == EAST]) == 2
        is_double_south_wind = len([x for x in self.valued_pairs if x == SOUTH]) == 2

        self.valued_pairs = list(set(self.valued_pairs))
        self.valued_anko = [x for x in self.player.valued_honors if player_hand_tiles_34[x] >= 3]
        self.has_valued_anko = len(self.valued_anko) >= 1

        opportunity_to_meld_yakuhai = False

        for x in range(0, 34):
            if x in self.valued_pairs and tiles_34[x] - player_hand_tiles_34[x] == 1:
                opportunity_to_meld_yakuhai = True

        has_valued_pair = False

        for pair in self.valued_pairs:
            # we have valued pair in the hand and there are enough tiles
            # in the wall
            if (
                opportunity_to_meld_yakuhai
                or self.player.number_of_revealed_tiles(pair, player_closed_hand_tiles_34) < 4
            ):
                has_valued_pair = True
                break

        # we don't have valuable pair or pon to open our hand
        if not has_valued_pair and not self.has_valued_anko:
            return False

        # let's always open double east
        if is_double_east_wind:
            return True

        # let's open double south if we have a dora in the hand
        # or we have other valuable pairs
        if is_double_south_wind and (self.dora_count_total >= 1 or len(self.valued_pairs) >= 2):
            return True

        #  there are 2+ valuable pairs let's open hand
        if len(self.valued_pairs) >= 2:
            # if we are dealer let's open hand
            if self.player.is_dealer:
                return True

            # if we have 1+ dora in the hand it is fine to open yakuhai
            if self.dora_count_total >= 1:
                return True

        # If we have 2+ dora in the hand let's open hand
        if self.dora_count_total >= 2:
            for x in range(0, 34):
                # we have other pair in the hand
                # so we can open hand for atodzuke
                if player_hand_tiles_34[x] >= 2 and x not in self.valued_pairs:
                    self.go_for_atodzuke = True
            return True

        # If we have 1+ dora in the hand and there is 5+ round step let's open hand
        if self.dora_count_total >= 1 and self.player.round_step > 5:
            return True

        for pair in self.valued_pairs:
            # last chance to get that yakuhai, let's go for it
            if (
                opportunity_to_meld_yakuhai
                and self.player.number_of_revealed_tiles(pair, player_closed_hand_tiles_34) == 3
                and self.player.ai.shanten >= 1
            ):

                if pair not in self.last_chance_calls:
                    self.last_chance_calls.append(pair)

                return True

        # finally check if we need a cheap hand in oorasu - so don't skip first yakujai
        if self.player.ai.placement.is_oorasu and opportunity_to_meld_yakuhai:
            placement = self.player.ai.placement.get_current_placement()
            logger_context = {
                "placement": placement,
            }

            if placement and placement["place"] == 4:
                enough_cost = self.player.ai.placement.get_minimal_cost_needed_considering_west()
                simple_han_scale = [0, 1000, 2000, 3900, 7700, 8000, 12000, 12000]
                num_han = self.get_open_hand_han() + self.dora_count_total
                if num_han >= len(simple_han_scale):
                    # why are we even here?
                    self.player.logger.debug(
                        log.PLACEMENT_MELD_DECISION,
                        "We are 4th in oorasu and have expensive hand, call meld",
                        logger_context,
                    )
                    return True

                # be pessimistic and don't count on direct ron
                hand_cost = simple_han_scale[num_han]
                if hand_cost >= enough_cost:
                    self.player.logger.debug(
                        log.PLACEMENT_MELD_DECISION,
                        "We are 4th in oorasu and our hand can give us 3rd with meld, take it",
                        logger_context,
                    )
                    return True

            if (
                placement
                and placement["place"] == 3
                and placement["diff_with_4th"] < self.player.ai.placement.comfortable_diff
            ):
                self.player.logger.debug(
                    log.PLACEMENT_MELD_DECISION, "We are 3rd in oorasu and want to secure it, take meld", logger_context
                )
                return True

        return False

    def determine_what_to_discard(self, discard_options, hand, open_melds):
        is_open_hand = self.player.is_open_hand

        tiles_34 = TilesConverter.to_34_array(hand)

        valued_pairs = [x for x in self.player.valued_honors if tiles_34[x] == 2]

        # closed pon sets
        valued_pons = [x for x in self.player.valued_honors if tiles_34[x] == 3]
        # open pon sets
        valued_pons += [
            x for x in open_melds if x.type == MeldPrint.PON and x.tiles[0] // 4 in self.player.valued_honors
        ]

        acceptable_options = []
        for item in discard_options:
            if is_open_hand:
                if len(valued_pons) == 0:
                    # don't destroy our only yakuhai pair
                    if len(valued_pairs) == 1 and item.tile_to_discard_34 in valued_pairs:
                        continue
                elif len(valued_pons) == 1:
                    # don't destroy our only yakuhai pon
                    if item.tile_to_discard_34 in valued_pons:
                        continue

                acceptable_options.append(item)

        # we don't have a choice
        if not acceptable_options:
            return discard_options

        preferred_options = []
        for item in acceptable_options:
            # ignore wait without yakuhai yaku if possible
            if is_open_hand and len(valued_pons) == 0 and len(valued_pairs) == 1:
                if item.shanten == 0 and valued_pairs[0] not in item.waiting:
                    continue

            preferred_options.append(item)

        if not preferred_options:
            return acceptable_options

        return preferred_options

    def is_tile_suitable(self, tile):
        """
        For yakuhai we don't have any limits
        :param tile: 136 tiles format
        :return: True
        """
        return True

    def meld_had_to_be_called(self, tile):
        tile //= 4
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        valued_pairs = [x for x in self.player.valued_honors if tiles_34[x] == 2]

        # for big shanten number we don't need to check already opened pon set,
        # because it will improve our hand anyway
        if self.player.ai.shanten < 2:
            for meld in self.player.melds:
                # we have already opened yakuhai pon
                # so we don't need to open hand without shanten improvement
                if self._is_yakuhai_pon(meld):
                    return False

        # if we don't have any yakuhai pon and this is our last chance, we must call this tile
        if tile in self.last_chance_calls:
            return True

        # in all other cases for closed hand we don't need to open hand with special conditions
        if not self.player.is_open_hand:
            return False

        # we have opened the hand already and don't yet have yakuhai pon
        # so we now must get it
        for valued_pair in valued_pairs:
            if valued_pair == tile:
                return True

        return False

    def try_to_call_meld(self, tile, is_kamicha_discard, tiles_136):
        if self.has_valued_anko:
            return super(YakuhaiStrategy, self).try_to_call_meld(tile, is_kamicha_discard, tiles_136)

        tile_34 = tile // 4
        # we will open hand for atodzuke only in the special cases
        if not self.player.is_open_hand and tile_34 not in self.valued_pairs:
            if self.go_for_atodzuke:
                return super(YakuhaiStrategy, self).try_to_call_meld(tile, is_kamicha_discard, tiles_136)

            return None, None

        return super(YakuhaiStrategy, self).try_to_call_meld(tile, is_kamicha_discard, tiles_136)

    def _is_yakuhai_pon(self, meld):
        return meld.type == MeldPrint.PON and meld.tiles[0] // 4 in self.player.valued_honors

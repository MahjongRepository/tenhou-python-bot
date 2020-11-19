import utils.decisions_constants as log
from mahjong.tile import TilesConverter
from mahjong.utils import is_chi, is_honor, is_man, is_pin, is_pon, is_sou, is_terminal, plus_dora, simplify
from utils.decisions_logger import MeldPrint


class BaseStrategy:
    YAKUHAI = 0
    HONITSU = 1
    TANYAO = 2
    FORMAL_TEMPAI = 3
    CHINITSU = 4
    COMMON_OPEN_TEMPAI = 6

    TYPES = {
        YAKUHAI: "Yakuhai",
        HONITSU: "Honitsu",
        TANYAO: "Tanyao",
        FORMAL_TEMPAI: "Formal Tempai",
        CHINITSU: "Chinitsu",
        COMMON_OPEN_TEMPAI: "Common Open Tempai",
    }

    not_suitable_tiles = []
    player = None
    type = None
    # number of shanten where we can start to open hand
    min_shanten = 7
    go_for_atodzuke = False

    dora_count_total = 0
    dora_count_central = 0
    dora_count_not_central = 0
    aka_dora_count = 0
    dora_count_honor = 0

    def __init__(self, strategy_type, player):
        self.type = strategy_type
        self.player = player
        self.go_for_atodzuke = False

    def __str__(self):
        return self.TYPES[self.type]

    def get_open_hand_han(self):
        return 0

    def should_activate_strategy(self, tiles_136, meld_tile=None):
        """
        Based on player hand and table situation
        we can determine should we use this strategy or not.
        :param: tiles_136
        :return: boolean
        """
        self.calculate_dora_count(tiles_136)

        return True

    def can_meld_into_agari(self):
        """
        Is melding into agari allowed with this strategy
        :return: boolean
        """
        # By default, the logic is the following: if we have any
        # non-suitable tiles, we can meld into agari state, because we'll
        # throw them away after meld.
        # Otherwise, there is no point.
        for tile in self.player.tiles:
            if not self.is_tile_suitable(tile):
                return True

        return False

    def is_tile_suitable(self, tile):
        """
        Can tile be used for open hand strategy or not
        :param tile: in 136 tiles format
        :return: boolean
        """
        raise NotImplementedError()

    def determine_what_to_discard(self, discard_options, hand, open_melds):
        first_option = sorted(discard_options, key=lambda x: x.shanten)[0]
        shanten = first_option.shanten

        # for riichi we don't need to discard useful tiles
        if shanten == 0 and not self.player.is_open_hand:
            return discard_options

        # mark all not suitable tiles as ready to discard
        # even if they not should be discarded by uke-ire
        for x in discard_options:
            if not self.is_tile_suitable(x.tile_to_discard_136):
                x.had_to_be_discarded = True

        return discard_options

    def try_to_call_meld(self, tile, is_kamicha_discard, new_tiles):
        """
        Determine should we call a meld or not.
        If yes, it will return MeldPrint object and tile to discard
        :param tile: 136 format tile
        :param is_kamicha_discard: boolean
        :param new_tiles:
        :return: MeldPrint and DiscardOption objects
        """
        if self.player.in_riichi:
            return None, None

        closed_hand = self.player.closed_hand[:]

        # we can't open hand anymore
        if len(closed_hand) == 1:
            return None, None

        # we can't use this tile for our chosen strategy
        if not self.is_tile_suitable(tile):
            return None, None

        discarded_tile = tile // 4
        closed_hand_34 = TilesConverter.to_34_array(closed_hand + [tile])

        combinations = []
        first_index = 0
        second_index = 0
        if is_man(discarded_tile):
            first_index = 0
            second_index = 8
        elif is_pin(discarded_tile):
            first_index = 9
            second_index = 17
        elif is_sou(discarded_tile):
            first_index = 18
            second_index = 26

        if second_index == 0:
            # honor tiles
            if closed_hand_34[discarded_tile] == 3:
                combinations = [[[discarded_tile] * 3]]
        else:
            # to avoid not necessary calculations
            # we can check only tiles around +-2 discarded tile
            first_limit = discarded_tile - 2
            if first_limit < first_index:
                first_limit = first_index

            second_limit = discarded_tile + 2
            if second_limit > second_index:
                second_limit = second_index

            combinations = self.player.ai.hand_divider.find_valid_combinations(
                closed_hand_34, first_limit, second_limit, True
            )

        if combinations:
            combinations = combinations[0]

        possible_melds = []
        for best_meld_34 in combinations:
            # we can call pon from everyone
            if is_pon(best_meld_34) and discarded_tile in best_meld_34:
                if best_meld_34 not in possible_melds:
                    possible_melds.append(best_meld_34)

            # we can call chi only from left player
            if is_chi(best_meld_34) and is_kamicha_discard and discarded_tile in best_meld_34:
                if best_meld_34 not in possible_melds:
                    possible_melds.append(best_meld_34)

        # we can call melds only with allowed tiles
        validated_melds = []
        for meld in possible_melds:
            if (
                self.is_tile_suitable(meld[0] * 4)
                and self.is_tile_suitable(meld[1] * 4)
                and self.is_tile_suitable(meld[2] * 4)
            ):
                validated_melds.append(meld)
        possible_melds = validated_melds

        if not possible_melds:
            return None, None

        chosen_meld_dict = self._find_best_meld_to_open(tile, possible_melds, new_tiles, closed_hand, tile)
        # we didn't find a good discard candidate after open meld
        if not chosen_meld_dict:
            return None, None

        selected_tile = chosen_meld_dict["discard_tile"]
        meld = chosen_meld_dict["meld"]

        shanten = selected_tile.shanten
        had_to_be_called = self.meld_had_to_be_called(tile)
        had_to_be_called = had_to_be_called or selected_tile.had_to_be_discarded

        # each strategy can use their own value to min shanten number
        if shanten > self.min_shanten:
            self.player.logger.debug(
                log.MELD_DEBUG,
                "After meld shanten is too high for our strategy. Abort melding.",
            )
            return None, None

        # sometimes we had to call tile, even if it will not improve our hand
        # otherwise we can call only with improvements of shanten
        if not had_to_be_called and shanten >= self.player.ai.shanten:
            self.player.logger.debug(
                log.MELD_DEBUG,
                "Meld is not improving hand shanten. Abort melding.",
            )
            return None, None

        if not self.validate_meld(chosen_meld_dict):
            self.player.logger.debug(
                log.MELD_DEBUG,
                "Meld is suitable for strategy logic. Abort melding.",
            )
            return None, None

        if not self.should_push_against_threats(chosen_meld_dict):
            self.player.logger.debug(
                log.MELD_DEBUG,
                "Meld is too dangerous to call. Abort melding.",
            )
            return None, None

        return meld, selected_tile

    def should_push_against_threats(self, chosen_meld_dict) -> bool:
        selected_tile = chosen_meld_dict["discard_tile"]

        if selected_tile.shanten <= 1:
            return True

        threats = self.player.ai.defence.get_threatening_players()
        if not threats:
            return True

        # don't open garbage hand against threats
        if selected_tile.shanten >= 3:
            return False

        tile_136 = selected_tile.tile_to_discard_136
        if len(threats) == 1:
            threat_hand_cost = threats[0].get_assumed_hand_cost(tile_136)
            # expensive threat
            # and our hand is not good
            # let's not open this
            if threat_hand_cost >= 7700:
                return False
        else:
            min_threat_hand_cost = min([x.get_assumed_hand_cost(tile_136) for x in threats])
            # 2+ threats
            # and they are not cheap
            # so, let's skip opening of bad hand
            if min_threat_hand_cost >= 5200:
                return False

        return True

    def validate_meld(self, chosen_meld_dict):
        """
        In some cased we want additionally check that meld is suitable to the strategy
        """
        if self.player.is_open_hand:
            return True

        if not self.player.ai.placement.is_oorasu:
            return True

        # don't care about not enough cost if we are the dealer
        if self.player.is_dealer:
            return True

        placement = self.player.ai.placement.get_current_placement()
        if not placement:
            return True

        needed_cost = self.player.ai.placement.get_minimal_cost_needed_considering_west(placement=placement)
        if needed_cost <= 1000:
            return True

        selected_tile = chosen_meld_dict["discard_tile"]
        if selected_tile.ukeire == 0:
            self.player.logger.debug(
                log.MELD_DEBUG, "We need to get out of 4th place, but this meld leaves us with zero ukeire"
            )
            return False

        logger_context = {
            "placement": placement,
            "meld": chosen_meld_dict,
            "needed_cost": needed_cost,
        }

        if selected_tile.shanten == 0:
            if not selected_tile.tempai_descriptor:
                return True

            # tempai has special logger context
            logger_context = {
                "placement": placement,
                "meld": chosen_meld_dict,
                "needed_cost": needed_cost,
                "tempai_descriptor": selected_tile.tempai_descriptor,
            }

            if selected_tile.tempai_descriptor["hand_cost"]:
                hand_cost = selected_tile.tempai_descriptor["hand_cost"]
            else:
                hand_cost = selected_tile.tempai_descriptor["cost_x_ukeire"] / selected_tile.ukeire

            # optimistic condition - direct ron
            if hand_cost * 2 < needed_cost:
                self.player.logger.debug(
                    log.MELD_DEBUG, "No chance to comeback from 4th with this meld, so keep hand closed", logger_context
                )
                return False
        elif selected_tile.shanten == 1:
            if selected_tile.average_second_level_cost is None:
                return True

            # optimistic condition - direct ron
            if selected_tile.average_second_level_cost * 2 < needed_cost:
                self.player.logger.debug(
                    log.MELD_DEBUG, "No chance to comeback from 4th with this meld, so keep hand closed", logger_context
                )
                return False
        else:
            simple_han_scale = [0, 1000, 2000, 3900, 7700, 8000, 12000, 12000]
            num_han = self.get_open_hand_han() + self.dora_count_total
            if num_han < len(simple_han_scale):
                hand_cost = simple_han_scale[num_han]
                # optimistic condition - direct ron
                if hand_cost * 2 < needed_cost:
                    self.player.logger.debug(
                        log.MELD_DEBUG,
                        "No chance to comeback from 4th with this meld, so keep hand closed",
                        logger_context,
                    )
                    return False

        self.player.logger.debug(log.MELD_DEBUG, "This meld should allow us to comeback from 4th", logger_context)
        return True

    def meld_had_to_be_called(self, tile):
        """
        For special cases meld had to be called even if shanten number will not be increased
        :param tile: in 136 tiles format
        :return: boolean
        """
        return False

    def calculate_dora_count(self, tiles_136):
        self.dora_count_central = 0
        self.dora_count_not_central = 0
        self.aka_dora_count = 0

        for tile_136 in tiles_136:
            tile_34 = tile_136 // 4

            dora_count = plus_dora(
                tile_136, self.player.table.dora_indicators, add_aka_dora=self.player.table.has_aka_dora
            )

            if not dora_count:
                continue

            if is_honor(tile_34):
                self.dora_count_not_central += dora_count
                self.dora_count_honor += dora_count
            elif is_terminal(tile_34):
                self.dora_count_not_central += dora_count
            else:
                self.dora_count_central += dora_count

        self.dora_count_central += self.aka_dora_count
        self.dora_count_total = self.dora_count_central + self.dora_count_not_central

    def _find_best_meld_to_open(self, call_tile_136, possible_melds, new_tiles, closed_hand, discarded_tile):
        all_tiles_are_suitable = True
        for tile_136 in closed_hand:
            all_tiles_are_suitable &= self.is_tile_suitable(tile_136)

        final_results = []
        for meld_34 in possible_melds:
            # in order to fully emulate the possible hand with meld, we save original melds state,
            # modify player's melds and then restore original melds state after everything is done
            melds_original = self.player.melds[:]
            tiles_original = self.player.tiles[:]

            tiles = self._find_meld_tiles(closed_hand, meld_34, discarded_tile)
            meld = MeldPrint()
            meld.type = is_chi(meld_34) and MeldPrint.CHI or MeldPrint.PON
            meld.tiles = sorted(tiles)

            self.player.logger.debug(
                log.MELD_HAND, f"Hand: {self._format_hand_for_print(closed_hand, discarded_tile, self.player.melds)}"
            )

            # update player hand state to emulate new situation and choose what to discard
            self.player.tiles = new_tiles[:]
            self.player.add_called_meld(meld)

            selected_tile = self.player.ai.hand_builder.choose_tile_to_discard(after_meld=True)

            # restore original tiles and melds state
            self.player.tiles = tiles_original
            self.player.melds = melds_original

            # we can't find a good discard candidate, so let's skip this
            if not selected_tile:
                self.player.logger.debug(log.MELD_DEBUG, "Can't find discard candidate after meld. Abort melding.")
                continue

            if not all_tiles_are_suitable and self.is_tile_suitable(selected_tile.tile_to_discard_136):
                self.player.logger.debug(
                    log.MELD_DEBUG,
                    "We have tiles in our hand that are not suitable to current strategy, "
                    "but we are going to discard tile that we need. Abort melding.",
                )
                continue

            call_tile_34 = call_tile_136 // 4
            # we can't discard the same tile that we called
            if selected_tile.tile_to_discard_34 == call_tile_34:
                self.player.logger.debug(
                    log.MELD_DEBUG, "We can't discard same tile that we used for meld. Abort melding."
                )
                continue

            # we can't discard tile from the other end of the same ryanmen that we called
            if not is_honor(selected_tile.tile_to_discard_34) and meld.type == MeldPrint.CHI:
                if is_sou(selected_tile.tile_to_discard_34) and is_sou(call_tile_34):
                    same_suit = True
                elif is_man(selected_tile.tile_to_discard_34) and is_man(call_tile_34):
                    same_suit = True
                elif is_pin(selected_tile.tile_to_discard_34) and is_pin(call_tile_34):
                    same_suit = True
                else:
                    same_suit = False

                if same_suit:
                    simplified_meld_0 = simplify(meld.tiles[0] // 4)
                    simplified_meld_1 = simplify(meld.tiles[1] // 4)
                    simplified_call = simplify(call_tile_34)
                    simplified_discard = simplify(selected_tile.tile_to_discard_34)
                    kuikae = False
                    if simplified_discard == simplified_call - 3:
                        kuikae_set = [simplified_call - 1, simplified_call - 2]
                        if simplified_meld_0 in kuikae_set and simplified_meld_1 in kuikae_set:
                            kuikae = True
                    elif simplified_discard == simplified_call + 3:
                        kuikae_set = [simplified_call + 1, simplified_call + 2]
                        if simplified_meld_0 in kuikae_set and simplified_meld_1 in kuikae_set:
                            kuikae = True

                    if kuikae:
                        tile_str = TilesConverter.to_one_line_string(
                            [selected_tile.tile_to_discard_136], print_aka_dora=self.player.table.has_aka_dora
                        )
                        self.player.logger.debug(
                            log.MELD_DEBUG,
                            f"Kuikae discard {tile_str} candidate. Abort melding.",
                        )
                        continue

            final_results.append(
                {
                    "discard_tile": selected_tile,
                    "meld_print": TilesConverter.to_one_line_string([meld_34[0] * 4, meld_34[1] * 4, meld_34[2] * 4]),
                    "meld": meld,
                }
            )

        if not final_results:
            self.player.logger.debug(log.MELD_DEBUG, "There are no good discards after melding.")
            return None

        final_results = sorted(
            final_results,
            key=lambda x: (x["discard_tile"].shanten, -x["discard_tile"].ukeire, x["discard_tile"].valuation),
        )

        self.player.logger.debug(
            log.MELD_PREPARE,
            "Tiles could be used for open meld",
            context=final_results,
        )
        return final_results[0]

    @staticmethod
    def _find_meld_tiles(closed_hand, meld_34, discarded_tile):
        discarded_tile_34 = discarded_tile // 4
        meld_34_copy = meld_34[:]
        closed_hand_copy = closed_hand[:]

        meld_34_copy.remove(discarded_tile_34)

        first_tile = TilesConverter.find_34_tile_in_136_array(meld_34_copy[0], closed_hand_copy)
        closed_hand_copy.remove(first_tile)

        second_tile = TilesConverter.find_34_tile_in_136_array(meld_34_copy[1], closed_hand_copy)
        closed_hand_copy.remove(second_tile)

        tiles = [first_tile, second_tile, discarded_tile]

        return tiles

    def _format_hand_for_print(self, tiles, new_tile, melds):
        tiles_string = TilesConverter.to_one_line_string(tiles, print_aka_dora=self.player.table.has_aka_dora)
        tile_string = TilesConverter.to_one_line_string([new_tile], print_aka_dora=self.player.table.has_aka_dora)
        hand_string = f"{tiles_string} + {tile_string}"
        hand_string += " [{}]".format(
            ", ".join(
                [
                    TilesConverter.to_one_line_string(x.tiles, print_aka_dora=self.player.table.has_aka_dora)
                    for x in melds
                ]
            )
        )
        return hand_string

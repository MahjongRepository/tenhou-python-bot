from typing import Dict

import utils.decisions_constants as log
from game.ai.discard import DiscardOption
from game.ai.placement import Placement
from mahjong.tile import TilesConverter
from mahjong.utils import is_chi, is_honor, is_pair, is_terminal, plus_dora, simplify


class RiichiV2:
    def __init__(self, player):
        self.player = player

    def should_call_riichi(self, discard_option):
        assert discard_option.shanten == 0
        assert not self.player.is_open_hand

        hand_builder = self.player.ai.hand_builder

        riichi_waiting = discard_option.waiting
        # empty waiting can be found in some cases
        if not riichi_waiting:
            self.player.logger.debug(log.RIICHI_SKIP, "No waiting", {"tile": discard_option.tile_print})
            return False

        # save original hand state
        # we will restore it after we have finished our routines
        tiles_original, discards_original = hand_builder.emulate_discard(discard_option)

        should_riichi = False
        count_tiles = hand_builder.count_tiles(riichi_waiting, TilesConverter.to_34_array(self.player.closed_hand))
        if count_tiles == 0:
            # don't call karaten riichi
            self.player.logger.debug(log.RIICHI_SKIP, "No remained tiles", {"tile": discard_option.tile_print})
            should_riichi = False
        else:
            should_continue = True

            # we decide if we should riichi or not before making a discard, hence we check for round step == 0
            first_discard = self.player.round_step == 0
            if first_discard and not self.player.table.meld_was_called:
                self.player.logger.debug(
                    log.RIICHI_CALL, "Daburi! No way we can miss it.", {"tile": discard_option.tile_print}
                )
                should_riichi = True
                should_continue = False

            if should_continue and count_tiles <= 4:
                # check if we can easily improve our hand with going to 1 shanten
                closed_tiles_34 = TilesConverter.to_34_array(tiles_original)
                tiles_34 = TilesConverter.to_34_array(tiles_original)
                for tile_34 in range(34):
                    closed_tiles_34[tile_34] -= 1
                    temp_waiting, shanten = self.player.ai.hand_builder.calculate_waits(
                        closed_tiles_34, tiles_34, use_chiitoitsu=False
                    )
                    closed_tiles_34[tile_34] += 1

                    if temp_waiting and shanten == 1:
                        wait_to_ukeire = dict(
                            zip(
                                temp_waiting,
                                [self.player.ai.hand_builder.count_tiles([x], closed_tiles_34) for x in temp_waiting],
                            )
                        )
                        ukeire = sum(wait_to_ukeire.values())
                        # let's be in dama, we can improve our hand with a lot of tiles
                        if ukeire >= 30:
                            self.player.logger.debug(
                                log.RIICHI_SKIP,
                                "We can improve our hand easily.",
                                {"tile": discard_option.tile_print, "count_tiles": count_tiles, "ukeire": ukeire},
                            )
                            should_riichi = False
                            should_continue = False

            if should_continue:
                if len(riichi_waiting) == 1:
                    should_riichi = self._should_call_riichi_one_sided(discard_option)
                else:
                    should_riichi = self._should_call_riichi_many_sided(discard_option)

        hand_builder.restore_after_emulate_discard(tiles_original, discards_original)

        return should_riichi

    def _should_call_riichi_one_sided(self, discard_option: DiscardOption):
        waiting = discard_option.waiting

        count_tiles = self.player.ai.hand_builder.count_tiles(
            waiting, TilesConverter.to_34_array(self.player.closed_hand)
        )
        waiting = waiting[0]
        hand_value = self.player.ai.estimate_hand_value_or_get_from_cache(waiting, call_riichi=False)
        hand_value_with_riichi = self.player.ai.estimate_hand_value_or_get_from_cache(waiting, call_riichi=True)

        must_riichi = self.player.ai.placement.must_riichi(
            has_yaku=(hand_value.yaku is not None and hand_value.cost is not None),
            num_waits=count_tiles,
            cost_with_riichi=hand_value_with_riichi.cost["main"],
            cost_with_damaten=(hand_value.cost and hand_value.cost["main"] or 0),
        )

        if must_riichi == Placement.MUST_RIICHI:
            self.player.logger.debug(
                log.RIICHI_CALL,
                "Based on placements",
                {
                    "tile": discard_option.tile_print,
                    "has_yaku": (hand_value.yaku is not None and hand_value.cost is not None),
                    "count_tiles": count_tiles,
                    "cost_with_riichi": hand_value_with_riichi.cost["main"],
                    "cost_with_damaten": (hand_value.cost and hand_value.cost["main"] or 0),
                },
            )
            return True

        if must_riichi == Placement.MUST_DAMATEN:
            self.player.logger.debug(
                log.RIICHI_SKIP,
                "Based on placements",
                {
                    "tile": discard_option.tile_print,
                    "has_yaku": (hand_value.yaku is not None and hand_value.cost is not None),
                    "count_tiles": count_tiles,
                    "cost_with_riichi": hand_value_with_riichi.cost["main"],
                    "cost_with_damaten": (hand_value.cost and hand_value.cost["main"] or 0),
                },
            )
            return False

        tiles = self.player.closed_hand[:]
        closed_melds = [x for x in self.player.melds if not x.opened]
        for meld in closed_melds:
            tiles.extend(meld.tiles[:3])

        results, tiles_34 = self.player.ai.hand_builder.divide_hand(tiles, waiting)
        result = results[0]

        closed_tiles_34 = TilesConverter.to_34_array(self.player.closed_hand)

        have_suji, have_kabe = self.player.ai.hand_builder.check_suji_and_kabe(closed_tiles_34, waiting)

        logger_context = {
            "tile": discard_option.tile_print,
            "is_dealer": self.player.is_dealer,
            "round_step": self.player.round_step,
            "count_tiles": count_tiles,
            "have_suji": have_suji,
            "have_kabe": have_kabe,
        }

        # what if we have yaku
        if hand_value.yaku is not None and hand_value.cost is not None:
            min_cost = hand_value.cost["main"]
            logger_context["min_cost"] = min_cost

            # tanki honor is a good wait, let's damaten only if hand is already expensive
            if is_honor(waiting):
                if (self.player.is_dealer and min_cost < 12000) or (not self.player.is_dealer and min_cost < 8000):
                    self.player.logger.debug(log.RIICHI_CALL, "Not expensive honor tanki with yaku", logger_context)
                    return True

                self.player.logger.debug(log.RIICHI_SKIP, "Expensive tanki honor with yaku", logger_context)
                return False

            is_chiitoitsu = len([x for x in result if is_pair(x)]) == 7
            simplified_waiting = simplify(waiting)

            for hand_set in result:
                if waiting not in hand_set:
                    continue

                logger_context["simplified_waiting"] = simplified_waiting

                # tanki wait but not chiitoitsu
                if is_pair(hand_set) and not is_chiitoitsu:
                    return self._decide_to_riichi_or_not_with_tanki_wait_for_hand_with_yaku(
                        count_tiles, simplified_waiting, have_suji, have_kabe, min_cost, logger_context
                    )

                # chiitoitsu hand
                if is_pair(hand_set) and is_chiitoitsu:
                    return self._decide_to_riichi_or_not_for_chiitoitsu_for_hand_with_yaku(
                        count_tiles, simplified_waiting, have_suji, have_kabe, logger_context
                    )

                # 1-sided wait means kanchan or penchan
                if is_chi(hand_set):
                    return self._decide_to_riichi_or_not_with_kanchan_penchan_wait_for_hand_with_yaku(
                        count_tiles, simplified_waiting, have_suji, have_kabe, min_cost, logger_context
                    )

        if logger_context.get("simplified_waiting"):
            del logger_context["simplified_waiting"]
        if logger_context.get("min_cost"):
            del logger_context["min_cost"]

        # what if we don't have yaku
        # our tanki wait is good, let's riichi
        if is_honor(waiting):
            self.player.logger.debug(log.RIICHI_CALL, "Honor tanki without yaku", logger_context)
            return True

        if count_tiles > 1:
            # terminal tanki is ok, too, just should be more than one tile left
            if is_terminal(waiting):
                self.player.logger.debug(log.RIICHI_CALL, "Terminal tanki with 1+ remained tile", logger_context)
                return True

            # whatever dora wait is ok, too, just should be more than one tile left
            if plus_dora(waiting * 4, self.player.table.dora_indicators, add_aka_dora=False) > 0:
                self.player.logger.debug(log.RIICHI_CALL, "Dora wait with 1+ remained tile", logger_context)
                return True

        simplified_waiting = simplify(waiting)

        for hand_set in result:
            if waiting not in hand_set:
                continue

            if is_pair(hand_set):
                # let's not riichi tanki wait without suji-trap or kabe
                if not have_suji and not have_kabe:
                    self.player.logger.debug(
                        log.RIICHI_SKIP, "Tanki wait without yaku and without suji-trap kabe", logger_context
                    )
                    return False

                # let's not riichi tanki on last suit tile if it's early
                if count_tiles == 1 and self.player.round_step < 6:
                    self.player.logger.debug(
                        log.RIICHI_SKIP,
                        "Tanki wait without yaku only one remained tile on the table on early stage",
                        logger_context,
                    )
                    return False

                # let's not riichi tanki 4, 5, 6 if it's early
                if 3 <= simplified_waiting <= 5 and self.player.round_step < 6:
                    self.player.logger.debug(
                        log.RIICHI_SKIP, "Tanki wait without yaku and 4-5-6 wait on early stage", logger_context
                    )
                    return False

            # 1-sided wait means kanchan or penchan
            # let's only riichi this bad wait if
            # it has all 4 tiles available or it
            # it's not too early
            if is_chi(hand_set) and 4 <= simplified_waiting <= 6:
                result = count_tiles == 4 or self.player.round_step >= 6
                reason = result and log.RIICHI_CALL or log.RIICHI_SKIP
                self.player.logger.debug(
                    reason,
                    "Kanchan/penchan without yaku on 4-5-6 wait with 4 remained tiles and on early stage",
                    logger_context,
                )

        self.player.logger.debug(log.RIICHI_CALL, "Tanki/kanchan/penchan wait", logger_context)
        return True

    def _should_call_riichi_many_sided(self, discard_option: DiscardOption) -> bool:
        waiting = discard_option.waiting

        count_tiles = self.player.ai.hand_builder.count_tiles(
            waiting, TilesConverter.to_34_array(self.player.closed_hand)
        )
        hand_costs = []
        hand_costs_with_riichi = []
        waits_with_yaku = 0
        for wait in waiting:
            hand_value = self.player.ai.estimate_hand_value_or_get_from_cache(wait, call_riichi=False)
            if hand_value.error is None:
                hand_costs.append(hand_value.cost["main"])
                if hand_value.yaku is not None and hand_value.cost is not None:
                    waits_with_yaku += 1

            hand_value_with_riichi = self.player.ai.estimate_hand_value_or_get_from_cache(wait, call_riichi=True)
            if hand_value_with_riichi.error is None:
                hand_costs_with_riichi.append(hand_value_with_riichi.cost["main"])

        min_cost = hand_costs and min(hand_costs) or 0
        min_cost_with_riichi = hand_costs_with_riichi and min(hand_costs_with_riichi) or 0

        must_riichi = self.player.ai.placement.must_riichi(
            has_yaku=waits_with_yaku == len(waiting),
            num_waits=count_tiles,
            cost_with_riichi=min_cost_with_riichi,
            cost_with_damaten=min_cost,
        )
        if must_riichi == Placement.MUST_RIICHI:
            self.player.logger.debug(
                log.RIICHI_CALL,
                "Based on placements",
                {
                    "tile": discard_option.tile_print,
                    "has_yaku": waits_with_yaku == len(waiting),
                    "count_tiles": count_tiles,
                    "cost_with_riichi": min_cost_with_riichi,
                    "cost_with_damaten": min_cost,
                },
            )
            return True
        elif must_riichi == Placement.MUST_DAMATEN:
            self.player.logger.debug(
                log.RIICHI_SKIP,
                "Based on placements",
                {
                    "tile": discard_option.tile_print,
                    "has_yaku": waits_with_yaku == len(waiting),
                    "count_tiles": count_tiles,
                    "cost_with_riichi": min_cost_with_riichi,
                    "cost_with_damaten": min_cost,
                },
            )
            return False

        logger_context = {
            "tile": discard_option.tile_print,
            "is_dealer": self.player.is_dealer,
            "round_step": self.player.round_step,
            "count_tiles": count_tiles,
            "len_waiting": len(waiting),
            "min_cost": min_cost,
        }

        # if we have yaku on every wait
        if waits_with_yaku == len(waiting):
            # let's not riichi this bad wait
            if count_tiles <= 2:
                self.player.logger.debug(
                    log.RIICHI_SKIP, "Many waits with yaku has only 2- remained tiles", logger_context
                )
                return False

            # if wait is slightly better, we will riichi only a cheap hand
            if count_tiles <= 4:
                if (self.player.is_dealer and min_cost >= 7700) or (not self.player.is_dealer and min_cost >= 5200):
                    self.player.logger.debug(
                        log.RIICHI_SKIP,
                        "Many waits with yaku has only 4- remained tiles and expensive hand",
                        logger_context,
                    )
                    return False

                self.player.logger.debug(
                    log.RIICHI_CALL, "Many waits with yaku has only 4- remained tiles and cheap hand", logger_context
                )
                return True

            # wait is even better, but still don't call riichi on damaten mangan
            if count_tiles <= 6:
                should_riichi = False
                # if it's early riichi more readily
                if self.player.round_step > 6:
                    if self.player.is_dealer and min_cost >= 11600:
                        should_riichi = True

                    if not self.player.is_dealer and min_cost >= 7700:
                        should_riichi = True
                else:
                    if self.player.is_dealer and min_cost >= 18000:
                        should_riichi = True

                    if not self.player.is_dealer and min_cost >= 12000:
                        should_riichi = True

                if should_riichi:
                    self.player.logger.debug(log.RIICHI_CALL, "Many waits with 6- remained tiles", logger_context)
                    return should_riichi

            # if wait is good we only damaten haneman
            if (self.player.is_dealer and min_cost >= 18000) or (not self.player.is_dealer and min_cost >= 12000):
                self.player.logger.debug(log.RIICHI_SKIP, "Many waits with expensive hand", logger_context)
                return False

        self.player.logger.debug(log.RIICHI_CALL, "Many waits", logger_context)
        return True

    def _decide_to_riichi_or_not_with_tanki_wait_for_hand_with_yaku(
        self,
        count_tiles: int,
        simplified_waiting: int,
        have_suji: bool,
        have_kabe: bool,
        min_cost: float,
        logger_context: Dict,
    ) -> bool:
        # let's not riichi tanki 4, 5, 6
        if 3 <= simplified_waiting <= 5:
            self.player.logger.debug(log.RIICHI_SKIP, "Middle tile tanki", logger_context)
            return False

        # don't riichi tanki wait on 1, 2, 3, 7, 8, 9 if it's only 1 tile
        if count_tiles == 1:
            self.player.logger.debug(log.RIICHI_SKIP, "Only one tile left for tanki wait", logger_context)
            return False

        # don't riichi 2378 tanki if hand has good value
        if simplified_waiting != 0 and simplified_waiting != 8:
            if (self.player.is_dealer and min_cost >= 7700) or (not self.player.is_dealer and min_cost >= 5200):
                self.player.logger.debug(log.RIICHI_SKIP, "Tanki wait with good value", logger_context)
                return False

        # only riichi if we have suji-trap or there is kabe
        if not have_suji and not have_kabe:
            self.player.logger.debug(log.RIICHI_SKIP, "Tanki wait without suji trap or kabe", logger_context)
            return False

        self.player.logger.debug(log.RIICHI_CALL, "Tanki wait", logger_context)
        return True

    def _decide_to_riichi_or_not_for_chiitoitsu_for_hand_with_yaku(
        self, count_tiles: int, simplified_waiting: int, have_suji: bool, have_kabe: bool, logger_context: Dict
    ) -> bool:
        # chiitoitsu on last suit tile is not the best
        if count_tiles == 1:
            self.player.logger.debug(log.RIICHI_SKIP, "Chiitoitsu with one left tile", logger_context)
            return False

        # early riichi on 19 tanki is good
        if (simplified_waiting == 0 or simplified_waiting == 8) and self.player.round_step < 7:
            self.player.logger.debug(log.RIICHI_CALL, "Earlier chiitoitsu on 19 wait", logger_context)
            return True

        # riichi on 19 tanki is good later too if we have 3 tiles to wait for
        if (simplified_waiting == 0 or simplified_waiting == 8) and self.player.round_step < 12 and count_tiles == 3:
            self.player.logger.debug(
                log.RIICHI_CALL, "Middle round chiitoitsu on 19 with 3 remaining waits", logger_context
            )
            return True

        # riichi on 28 tanki is good if we have 3 tiles to wait for
        if (simplified_waiting == 1 or simplified_waiting == 7) and self.player.round_step < 12 and count_tiles == 3:
            self.player.logger.debug(
                log.RIICHI_CALL, "Middle round chiitoitsu on 28 with 3 remaining waits", logger_context
            )
            return True

        # otherwise only riichi if we have suji-trap or there is kabe
        if not have_suji and not have_kabe:
            self.player.logger.debug(log.RIICHI_SKIP, "Chiitoitsu doesn't have suji-trap or kabe", logger_context)
            return False

        self.player.logger.debug(log.RIICHI_CALL, "Chiitoitsu", logger_context)
        return True

    def _decide_to_riichi_or_not_with_kanchan_penchan_wait_for_hand_with_yaku(
        self,
        count_tiles: int,
        simplified_waiting: int,
        have_suji: bool,
        have_kabe: bool,
        min_cost: float,
        logger_context: Dict,
    ) -> bool:
        # let's not riichi kanchan on 4, 5, 6
        if 3 <= simplified_waiting <= 5:
            self.player.logger.debug(log.RIICHI_SKIP, "Kanchan/penchan 4-5-6 wait", logger_context)
            return False

        # if we only have 1 tile to wait for, let's damaten
        if count_tiles == 1:
            self.player.logger.debug(log.RIICHI_SKIP, "Kanchan/penchan only one tile remained", logger_context)
            return False

        # if we have 2 tiles to wait for and hand cost is good without riichi,
        # let's damaten
        if count_tiles == 2:
            if (self.player.is_dealer and min_cost >= 7700) or (not self.player.is_dealer and min_cost >= 5200):
                self.player.logger.debug(
                    log.RIICHI_SKIP, "Kanchan/penchan two tiles remained and hand has good value", logger_context
                )
                return False

        # if we have more than two tiles to wait for and we have kabe or suji - insta riichi
        if count_tiles > 2 and (have_suji or have_kabe):
            self.player.logger.debug(
                log.RIICHI_CALL, "Kanchan/penchan 3+ tiles remained and we have suji-trap or kabe", logger_context
            )
            return True

        # 2 and 8 are good waits but not in every condition
        if simplified_waiting == 1 or simplified_waiting == 7:
            should_riichi = False

            if self.player.round_step < 7:
                if self.player.is_dealer and min_cost < 18000:
                    should_riichi = True

                if not self.player.is_dealer and min_cost < 8000:
                    should_riichi = True

            if self.player.round_step < 12:
                if self.player.is_dealer and min_cost < 12000:
                    should_riichi = True

                if not self.player.is_dealer and min_cost < 5200:
                    should_riichi = True

            if self.player.round_step < 15:
                if self.player.is_dealer and 2000 < min_cost < 7700:
                    should_riichi = True

            if should_riichi:
                self.player.logger.debug(log.RIICHI_CALL, "Kanchan/penchan 2-8 wait", logger_context)
                return should_riichi

        # 3 and 7 are ok waits sometimes too
        if simplified_waiting == 2 or simplified_waiting == 6:
            should_riichi = False

            if self.player.round_step < 7:
                if self.player.is_dealer and min_cost < 12000:
                    should_riichi = True

                if not self.player.is_dealer and min_cost < 5200:
                    should_riichi = True

            if self.player.round_step < 12:
                if self.player.is_dealer and min_cost < 7700:
                    should_riichi = True

                if not self.player.is_dealer and min_cost < 5200:
                    should_riichi = True

            if self.player.round_step < 15:
                if self.player.is_dealer and 2000 < min_cost < 7700:
                    should_riichi = True

            if should_riichi:
                self.player.logger.debug(log.RIICHI_CALL, "Kanchan/penchan 3-7 wait", logger_context)
                return should_riichi

        # otherwise only riichi if we have suji-trap or there is kabe
        if not have_suji and not have_kabe:
            self.player.logger.debug(
                log.RIICHI_SKIP, "Kanchan/penchan and there is no suji-trap or not kabe", logger_context
            )
            return False

        self.player.logger.debug(log.RIICHI_CALL, "Kanchan/penchan", logger_context)
        return True

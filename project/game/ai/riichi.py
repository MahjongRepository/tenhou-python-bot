from game.ai.placement import Placement
from mahjong.tile import TilesConverter
from mahjong.utils import is_chi, is_honor, is_pair, is_terminal, plus_dora, simplify


class Riichi:
    def __init__(self, player):
        self.player = player

    def should_call_riichi(self, discard_option):
        assert discard_option.shanten == 0
        assert not self.player.is_open_hand

        hand_builder = self.player.ai.hand_builder

        waiting = discard_option.waiting
        # empty waiting can be found in some cases
        if not waiting:
            return False

        # save original hand state
        # we will restore it after we have finished our routines
        tiles_original, discards_original = hand_builder.emulate_discard(discard_option)

        count_tiles = hand_builder.count_tiles(waiting, TilesConverter.to_34_array(self.player.closed_hand))
        if count_tiles == 0:
            # don't call karaten riichi
            should_riichi = False
        else:
            # we decide if we should riichi or not before making a discard, hence we check for round step == 0
            first_discard = self.player.round_step == 0
            if first_discard and not self.player.table.meld_was_called:
                # it is daburi!
                should_riichi = True
            else:
                # regular path
                if len(waiting) == 1:
                    should_riichi = self._should_call_riichi_one_sided(waiting)
                else:
                    should_riichi = self._should_call_riichi_many_sided(waiting)

        hand_builder.restore_after_emulate_discard(tiles_original, discards_original)

        return should_riichi

    def _should_call_riichi_one_sided(self, waiting):
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
            return True
        elif must_riichi == Placement.MUST_DAMATEN:
            return False

        tiles = self.player.closed_hand[:]
        closed_melds = [x for x in self.player.melds if not x.opened]
        for meld in closed_melds:
            tiles.extend(meld.tiles[:3])

        results, tiles_34 = self.player.ai.hand_builder.divide_hand(tiles, waiting)
        result = results[0]

        closed_tiles_34 = TilesConverter.to_34_array(self.player.closed_hand)

        have_suji, have_kabe = self.player.ai.hand_builder.check_suji_and_kabe(closed_tiles_34, waiting)

        # what if we have yaku
        if hand_value.yaku is not None and hand_value.cost is not None:
            min_cost = hand_value.cost["main"]

            # tanki honor is a good wait, let's damaten only if hand is already expensive
            if is_honor(waiting):
                if self.player.is_dealer and min_cost < 12000:
                    return True

                if not self.player.is_dealer and min_cost < 8000:
                    return True

                return False

            is_chiitoitsu = len([x for x in result if is_pair(x)]) == 7
            simplified_waiting = simplify(waiting)

            for hand_set in result:
                if waiting not in hand_set:
                    continue

                # tanki wait but not chiitoitsu
                if is_pair(hand_set) and not is_chiitoitsu:
                    # let's not riichi tanki 4, 5, 6
                    if 3 <= simplified_waiting <= 5:
                        return False

                    # don't riichi tanki wait on 1, 2, 3, 7, 8, 9 if it's only 1 tile
                    if count_tiles == 1:
                        return False

                    # don't riichi 2378 tanki if hand has good value
                    if simplified_waiting != 0 and simplified_waiting != 8:
                        if self.player.is_dealer and min_cost >= 7700:
                            return False

                        if not self.player.is_dealer and min_cost >= 5200:
                            return False

                    # only riichi if we have suji-trab or there is kabe
                    if not have_suji and not have_kabe:
                        return False

                    return True

                # tanki wait with chiitoitsu
                if is_pair(hand_set) and is_chiitoitsu:
                    # chiitoitsu on last suit tile is not the best
                    if count_tiles == 1:
                        return False

                    # early riichi on 19 tanki is good
                    if (simplified_waiting == 0 or simplified_waiting == 8) and self.player.round_step < 7:
                        return True

                    # riichi on 19 tanki is good later too if we have 3 tiles to wait for
                    if (
                        (simplified_waiting == 0 or simplified_waiting == 8)
                        and self.player.round_step < 12
                        and count_tiles == 3
                    ):
                        return True

                    # riichi on 28 tanki is good if we have 3 tiles to wait for
                    if (
                        (simplified_waiting == 1 or simplified_waiting == 7)
                        and self.player.round_step < 12
                        and count_tiles == 3
                    ):
                        return True

                    # otherwise only riichi if we have suji-trab or there is kabe
                    if not have_suji and not have_kabe:
                        return False

                    return True

                # 1-sided wait means kanchan or penchan
                if is_chi(hand_set):
                    # let's not riichi kanchan on 4, 5, 6
                    if 3 <= simplified_waiting <= 5:
                        return False

                    # now checking waiting for 2, 3, 7, 8
                    # if we only have 1 tile to wait for, let's damaten
                    if count_tiles == 1:
                        return False

                    # if we have 2 tiles to wait for and hand cost is good without riichi,
                    # let's damaten
                    if count_tiles == 2:
                        if self.player.is_dealer and min_cost >= 7700:
                            return False

                        if not self.player.is_dealer and min_cost >= 5200:
                            return False

                    # if we have more than two tiles to wait for and we have kabe or suji - insta riichi
                    if count_tiles > 2 and (have_suji or have_kabe):
                        return True

                    # 2 and 8 are good waits but not in every condition
                    if simplified_waiting == 1 or simplified_waiting == 7:
                        if self.player.round_step < 7:
                            if self.player.is_dealer and min_cost < 18000:
                                return True

                            if not self.player.is_dealer and min_cost < 8000:
                                return True

                        if self.player.round_step < 12:
                            if self.player.is_dealer and min_cost < 12000:
                                return True

                            if not self.player.is_dealer and min_cost < 5200:
                                return True

                        if self.player.round_step < 15:
                            if self.player.is_dealer and 2000 < min_cost < 7700:
                                return True

                    # 3 and 7 are ok waits sometimes too
                    if simplified_waiting == 2 or simplified_waiting == 6:
                        if self.player.round_step < 7:
                            if self.player.is_dealer and min_cost < 12000:
                                return True

                            if not self.player.is_dealer and min_cost < 5200:
                                return True

                        if self.player.round_step < 12:
                            if self.player.is_dealer and min_cost < 7700:
                                return True

                            if not self.player.is_dealer and min_cost < 5200:
                                return True

                        if self.player.round_step < 15:
                            if self.player.is_dealer and 2000 < min_cost < 7700:
                                return True

                    # otherwise only riichi if we have suji-trab or there is kabe
                    if not have_suji and not have_kabe:
                        return False

                    return True

        # what if we don't have yaku
        # our tanki wait is good, let's riichi
        if is_honor(waiting):
            return True

        if count_tiles > 1:
            # terminal tanki is ok, too, just should be more than one tile left
            if is_terminal(waiting):
                return True

            # whatever dora wait is ok, too, just should be more than one tile left
            if plus_dora(waiting * 4, self.player.table.dora_indicators, add_aka_dora=False) > 0:
                return True

        simplified_waiting = simplify(waiting)

        for hand_set in result:
            if waiting not in hand_set:
                continue

            if is_pair(hand_set):
                # let's not riichi tanki wait without suji-trap or kabe
                if not have_suji and not have_kabe:
                    return False

                # let's not riichi tanki on last suit tile if it's early
                if count_tiles == 1 and self.player.round_step < 6:
                    return False

                # let's not riichi tanki 4, 5, 6 if it's early
                if 3 <= simplified_waiting <= 5 and self.player.round_step < 6:
                    return False

            # 1-sided wait means kanchan or penchan
            # let's only riichi this bad wait if
            # it has all 4 tiles available or it
            # it's not too early
            if is_chi(hand_set) and 4 <= simplified_waiting <= 6:
                return count_tiles == 4 or self.player.round_step >= 6

        return True

    def _should_call_riichi_many_sided(self, waiting):
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
            return True
        elif must_riichi == Placement.MUST_DAMATEN:
            return False

        # if we have yaku on every wait
        if waits_with_yaku == len(waiting):
            # let's not riichi this bad wait
            if count_tiles <= 2:
                return False

            # if wait is slightly better, we will riichi only a cheap hand
            if count_tiles <= 4:
                if self.player.is_dealer and min_cost >= 7700:
                    return False

                if not self.player.is_dealer and min_cost >= 5200:
                    return False

                return True

            # wait is even better, but still don't call riichi on damaten mangan
            if count_tiles <= 6:
                # if it's early riichi more readily
                if self.player.round_step > 6:
                    if self.player.is_dealer and min_cost >= 11600:
                        return False

                    if not self.player.is_dealer and min_cost >= 7700:
                        return False
                else:
                    if self.player.is_dealer and min_cost >= 18000:
                        return False

                    if not self.player.is_dealer and min_cost >= 12000:
                        return False

                return True

            # if wait is good we only damaten haneman
            if self.player.is_dealer and min_cost >= 18000:
                return False

            if not self.player.is_dealer and min_cost >= 12000:
                return False

            return True

        # if we don't have yaku on every wait and it's two-sided or more, we call riichi
        return True

from mahjong.tile import TilesConverter
from mahjong.utils import is_honor, simplify, is_pair, is_chi


class Damaten:

    def __init__(self, player):
        self.player = player

    def should_call_riichi(self):
        # empty waiting can be found in some cases
        if not self.player.ai.waiting:
            return False

        # TODO: always call daburi

        if self.player.ai.in_defence:
            return False

        # don't call karaten riichi
        count_tiles = self.player.ai.count_tiles(self.player.ai.waiting, TilesConverter.to_34_array(self.player.tiles))
        if count_tiles == 0:
            return False

        # first of all let's consider 1-sided waits
        if len(self.player.ai.waiting) == 1:
            waiting = self.player.ai.waiting[0]
            hand_value = self.player.ai.estimate_hand_value(waiting, call_riichi=False)

            tiles = self.player.closed_hand + [waiting * 4]
            closed_melds = [x for x in self.player.melds if not x.opened]
            for meld in closed_melds:
                tiles.extend(meld.tiles[:3])

            tiles_34 = TilesConverter.to_34_array(tiles)

            results = self.player.ai.hand_divider.divide_hand(tiles_34)
            result = results[0]

            # what if we have yaku
            if hand_value.yaku is not None and hand_value.cost is not None:
                min_cost = hand_value.cost['main']

                # tanki honor is a good wait, let's damaten only if hand is already expensive
                if is_honor(waiting):
                    if self.player.is_dealer and min_cost < 12000:
                        return True

                    if not self.player.is_dealer and min_cost < 8000:
                        return True

                    return False

                simplified_waiting = simplify(waiting)

                for hand_set in result:
                    if waiting not in hand_set:
                        continue

                    if is_pair(hand_set):
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

                        # TODO: check for kabe and suji
                        return True

                    # 1-sided wait means kanchan or penchan
                    if is_chi(hand_set):
                        # let's not riichi kanchan on 4, 5, 6
                        if 4 <= simplified_waiting <= 6:
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

                        # TODO: check for kabe and suji
                        return True

            # what if we don't have yaku
            # our tanki wait is good, let's riichi
            if is_honor(waiting):
                return True

            simplified_waiting = simplify(waiting)

            for hand_set in result:
                if not waiting in hand_set:
                    continue

                if is_pair(hand_set):
                    # let's not riichi tanki 4, 5, 6
                    if 3 <= simplified_waiting <= 5:
                        return False

                # 1-sided wait means kanchan or penchan
                if is_chi(hand_set):
                    # let's only riichi this bad wait if
                    # it has all 4 tiles available or it
                    # it's not too early
                    if 4 <= simplified_waiting <= 6:
                        return count_tiles == 4 or self.player.round_step >= 6

            # TODO: implement rest of the logic

            return True

        # now we are looking at two or more sided waits only
        hand_costs = []
        waits_with_yaku = 0
        for waiting in self.player.ai.waiting:
            hand_value = self.player.ai.estimate_hand_value(waiting, call_riichi=False)
            if hand_value.error is None:
                hand_costs.append(hand_value.cost['main'])
                if hand_value.yaku is not None and hand_value.cost is not None:
                    waits_with_yaku += 1

        # if we have yaku on every wait
        if waits_with_yaku == len(self.player.ai.waiting):
            min_cost = min(hand_costs)

            # let's not riichi this bad wait
            if count_tiles <= 2:
                return False

            # if wait is slighly better, we will riichi only a cheap hand
            if count_tiles <= 4:
                if self.player.is_dealer and min_cost >= 7700:
                    return False

                if not self.player.is_dealer and min_cost >= 5200:
                    return False

                return True

            # wait is even better, but still don't call riichi on damaten mangan
            if count_tiles <= 6:
                if self.player.is_dealer and min_cost >= 11600:
                    return False

                if not self.player.is_dealer and min_cost >= 7700:
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

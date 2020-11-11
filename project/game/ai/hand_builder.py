from typing import List

import utils.decisions_constants as log
from game.ai.discard import DiscardOption
from game.ai.helpers.kabe import Kabe
from mahjong.constants import AKA_DORA_LIST
from mahjong.shanten import Shanten
from mahjong.tile import Tile, TilesConverter
from mahjong.utils import is_honor, is_pair, is_tile_strictly_isolated, simplify
from utils.decisions_logger import DecisionsLogger


class HandBuilder:
    player = None
    ai = None

    def __init__(self, player, ai):
        self.player = player
        self.ai = ai

    def discard_tile(self, tiles, closed_hand, melds):
        selected_tile = self.choose_tile_to_discard(tiles, closed_hand, melds)
        return self.process_discard_option(selected_tile, closed_hand)

    def choose_tile_to_discard(self, tiles, closed_hand, melds, after_meld=False):
        """
        Try to find best tile to discard, based on different evaluations
        """
        threatening_players = None

        discard_options, min_shanten = self.find_discard_options(tiles, closed_hand)
        if min_shanten == Shanten.AGARI_STATE:
            min_shanten = min([x.shanten for x in discard_options])

        one_shanten_ukeire2_calculated_beforehand = False
        if self.player.config.FEATURE_DEFENCE_ENABLED:
            # FIXME: this is hacky and takes too much time! refactor
            # we need to calculate ukeire2 beforehand for correct danger calculation
            if self.player.ai.defence.get_threatening_players() and min_shanten != 0:
                for discard_option in discard_options:
                    if discard_option.shanten == 1:
                        self.calculate_second_level_ukeire(discard_option, tiles, melds, after_meld)
                        one_shanten_ukeire2_calculated_beforehand = True

            discard_options, threatening_players = self.player.ai.defence.mark_tiles_danger_for_threats(discard_options)

            if threatening_players:
                DecisionsLogger.debug(log.DEFENCE_THREATENING_ENEMY, "Threats", context=threatening_players)

        DecisionsLogger.debug(log.DISCARD_OPTIONS, "All discard candidates", discard_options)

        tiles_we_can_discard = [x for x in discard_options if x.danger.is_danger_acceptable()]
        if not tiles_we_can_discard:
            # no tiles with acceptable danger - we go betaori
            return self._choose_safest_tile_or_skip_meld(discard_options, after_meld)

        # our strategy can affect discard options
        if self.ai.current_strategy:
            tiles_we_can_discard = self.ai.current_strategy.determine_what_to_discard(
                tiles_we_can_discard, closed_hand, melds
            )

            had_to_be_discarded_tiles = [x for x in tiles_we_can_discard if x.had_to_be_discarded]
            if had_to_be_discarded_tiles:
                # we don't care about effectiveness of tiles that don't suit our strategy,
                # so just choose the safest one
                return self._choose_safest_tile(had_to_be_discarded_tiles)

            # remove needed tiles from discard options
            tiles_we_can_discard = [x for x in tiles_we_can_discard if not x.had_to_be_saved]
            if not tiles_we_can_discard:
                # no acceptable tiles that allow us to keep our strategy - we go betaori
                return self._choose_safest_tile_or_skip_meld(discard_options, after_meld)

        # we check this after strategy checks to allow discarding safe 99 from tempai to get tanyao for example
        min_acceptable_shanten = min([x.shanten for x in tiles_we_can_discard])
        assert min_acceptable_shanten >= min_shanten
        if min_acceptable_shanten > min_shanten:
            # all tiles with acceptable danger increase number of shanten - we just go betaori
            return self._choose_safest_tile_or_skip_meld(discard_options, after_meld)

        # we should have some plan for push when we open our hand, otherwise - don't meld
        if threatening_players and after_meld and min_shanten > 0:
            if not self._find_acceptable_path_to_tempai(tiles_we_can_discard, min_shanten):
                return None

        # by now we have the following:
        # - all discard candidates have acceptable danger
        # - all discard candidates allow us to proceed with our strategy
        tiles_we_can_discard = sorted(tiles_we_can_discard, key=lambda x: (x.shanten, -x.ukeire))
        first_option = tiles_we_can_discard[0]
        assert first_option.shanten == min_shanten
        results_with_same_shanten = [x for x in tiles_we_can_discard if x.shanten == first_option.shanten]

        if first_option.shanten == 0:
            return self._choose_best_discard_in_tempai(tiles, melds, results_with_same_shanten, after_meld)

        if first_option.shanten == 1:
            return self._choose_best_discard_with_1_shanten(
                tiles, melds, results_with_same_shanten, after_meld, one_shanten_ukeire2_calculated_beforehand
            )

        if first_option.shanten == 2 or first_option.shanten == 3:
            return self._choose_best_discard_with_2_3_shanten(
                tiles, melds, closed_hand, results_with_same_shanten, after_meld
            )

        return self._choose_best_discard_with_4_or_more_shanten(closed_hand, results_with_same_shanten)

    def process_discard_option(self, discard_option, closed_hand, force_discard=False):
        DecisionsLogger.debug(log.DISCARD, context=discard_option)

        self.player.in_tempai = discard_option.shanten == 0
        self.ai.waiting = discard_option.waiting
        self.ai.shanten = discard_option.shanten
        self.ai.ukeire = discard_option.ukeire
        self.ai.ukeire_second = discard_option.ukeire_second

        # when we called meld we don't need "smart" discard
        if force_discard:
            return discard_option.find_tile_in_hand(closed_hand)

        last_draw_34 = self.player.last_draw and self.player.last_draw // 4 or None
        if self.player.last_draw not in AKA_DORA_LIST and last_draw_34 == discard_option.tile_to_discard:
            return self.player.last_draw
        else:
            return discard_option.find_tile_in_hand(closed_hand)

    def calculate_shanten_and_decide_hand_structure(self, tiles_34, open_sets_34=None):
        shanten_with_chiitoitsu = self.ai.calculate_shanten_or_get_from_cache(tiles_34, use_chiitoitsu=True)
        shanten_without_chiitoitsu = self.ai.calculate_shanten_or_get_from_cache(tiles_34, use_chiitoitsu=False)
        return self._decide_if_use_chiitoitsu(shanten_with_chiitoitsu, shanten_without_chiitoitsu)

    def calculate_waits(self, tiles_34: List[int], use_chiitoitsu: bool = False):
        previous_shanten = self.ai.calculate_shanten_or_get_from_cache(tiles_34, use_chiitoitsu=use_chiitoitsu)

        waiting = []
        for tile_index in range(0, 34):
            if tiles_34[tile_index] == 4:
                continue

            tiles_34[tile_index] += 1

            skip_isolated_tile = True
            if tiles_34[tile_index] == 4:
                skip_isolated_tile = False
            if use_chiitoitsu and tiles_34[tile_index] == 3:
                skip_isolated_tile = False

            # there is no need to check single isolated tile
            if skip_isolated_tile and is_tile_strictly_isolated(tiles_34, tile_index):
                tiles_34[tile_index] -= 1
                continue

            new_shanten = self.ai.calculate_shanten_or_get_from_cache(tiles_34, use_chiitoitsu=use_chiitoitsu)

            if new_shanten == previous_shanten - 1:
                waiting.append(tile_index)

            tiles_34[tile_index] -= 1

        return waiting, previous_shanten

    def find_discard_options(self, tiles: List[int], closed_hand: List[int]):
        """
        :param tiles: array of tiles in 136 format
        :param closed_hand: array of tiles in 136 format
        :return:
        """
        tiles_34 = TilesConverter.to_34_array(tiles)
        closed_tiles_34 = TilesConverter.to_34_array(closed_hand)
        is_agari = self.ai.agari.is_agari(tiles_34, self.player.meld_34_tiles)

        # we decide beforehand if we need to consider chiitoitsu for all of our possible discards
        min_shanten_with_chiitoitsu = 7
        min_shanten_without_chiitoitsu = 7

        for hand_tile in range(0, 34):
            if not closed_tiles_34[hand_tile]:
                continue

            shanten, use_chiitoitsu = self.calculate_shanten_and_decide_hand_structure(tiles_34)
            if use_chiitoitsu and shanten < min_shanten_with_chiitoitsu:
                min_shanten_with_chiitoitsu = shanten
            elif not use_chiitoitsu and shanten < min_shanten_without_chiitoitsu:
                min_shanten_without_chiitoitsu = shanten

        min_shanten, use_chiitoitsu = self._decide_if_use_chiitoitsu(
            min_shanten_with_chiitoitsu, min_shanten_without_chiitoitsu
        )

        results = []
        for hand_tile in range(0, 34):
            if not closed_tiles_34[hand_tile]:
                continue

            closed_tiles_34[hand_tile] -= 1
            waiting, shanten = self.calculate_waits(closed_tiles_34, use_chiitoitsu=use_chiitoitsu)
            assert shanten >= min_shanten
            closed_tiles_34[hand_tile] += 1

            if waiting:
                wait_to_ukeire = dict(zip(waiting, [self.count_tiles([x], closed_tiles_34) for x in waiting]))
                results.append(
                    DiscardOption(
                        player=self.player,
                        shanten=shanten,
                        tile_to_discard=hand_tile,
                        waiting=waiting,
                        ukeire=sum(wait_to_ukeire.values()),
                        wait_to_ukeire=wait_to_ukeire,
                    )
                )

        if is_agari:
            shanten = Shanten.AGARI_STATE
        else:
            shanten = self.ai.calculate_shanten_or_get_from_cache(tiles_34, use_chiitoitsu=use_chiitoitsu)
            assert shanten >= min_shanten

        return results, shanten

    def count_tiles(self, waiting, tiles_34):
        n = 0
        for tile_34 in waiting:
            n += 4 - self.player.number_of_revealed_tiles(tile_34, tiles_34)
        return n

    def divide_hand(self, tiles, waiting):
        tiles_copy = tiles[:]

        for i in range(0, 4):
            if waiting * 4 + i not in tiles_copy:
                tiles_copy += [waiting * 4 + i]
                break

        tiles_34 = TilesConverter.to_34_array(tiles_copy)

        results = self.player.ai.hand_divider.divide_hand(tiles_34)
        return results, tiles_34

    def check_suji_and_kabe(self, tiles_34, waiting):
        # let's find suji-traps in our discard
        suji_tiles = self.player.ai.suji.find_suji([x.value for x in self.player.discards])
        have_suji = waiting in suji_tiles

        # let's find kabe
        kabe_tiles = self.player.ai.kabe.find_all_kabe(tiles_34)
        have_kabe = False
        for kabe in kabe_tiles:
            if waiting == kabe["tile"] and kabe["type"] == Kabe.STRONG_KABE:
                have_kabe = True
                break

        return have_suji, have_kabe

    def calculate_second_level_ukeire(self, discard_option, tiles, melds, after_meld=False):
        not_suitable_tiles = self.ai.current_strategy and self.ai.current_strategy.not_suitable_tiles or []
        call_riichi = not (self.player.is_open_hand or after_meld)

        # we are going to do manipulations that require player hand and discards to be updated
        # so we save original tiles and discards here and restore it at the end of the function
        player_tiles_original = self.player.tiles[:]
        player_discards_original = self.player.discards[:]

        tile_in_hand = discard_option.find_tile_in_hand(self.player.closed_hand)

        self.player.tiles = tiles[:]
        self.player.discards.append(Tile(tile_in_hand, False))
        self.player.tiles.remove(tile_in_hand)

        sum_tiles = 0
        sum_cost = 0
        average_costs = []
        for wait_34 in discard_option.waiting:
            if self.player.is_open_hand and wait_34 in not_suitable_tiles:
                continue

            closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)
            live_tiles = 4 - self.player.number_of_revealed_tiles(wait_34, closed_hand_34)

            if live_tiles == 0:
                continue

            wait_136 = wait_34 * 4
            self.player.tiles.append(wait_136)

            results, shanten = self.find_discard_options(self.player.tiles, self.player.closed_hand)
            results = [x for x in results if x.shanten == discard_option.shanten - 1]

            # let's take best ukeire here
            if results:
                result_has_atodzuke = False
                if self.player.is_open_hand:
                    best_one = results[0]
                    best_ukeire = 0
                    for result in results:
                        has_atodzuke = False
                        ukeire = 0
                        for wait_34 in result.waiting:
                            if wait_34 in not_suitable_tiles:
                                has_atodzuke = True
                            else:
                                ukeire += result.wait_to_ukeire[wait_34]

                        # let's consider atodzuke waits to be worse than non-atodzuke ones
                        if has_atodzuke:
                            ukeire /= 2

                        # FIXME consider sorting by cost_x_ukeire as well
                        if (ukeire > best_ukeire) or (ukeire >= best_ukeire and not has_atodzuke):
                            best_ukeire = ukeire
                            best_one = result
                            result_has_atodzuke = has_atodzuke
                else:
                    if shanten == 0:
                        # FIXME save cost_x_ukeire to not calculate it twice
                        best_one = sorted(
                            results,
                            key=lambda x: (-x.ukeire, -self._estimate_cost_x_ukeire(x, call_riichi=call_riichi)[0]),
                        )[0]
                    else:
                        best_one = sorted(results, key=lambda x: -x.ukeire)[0]
                    best_ukeire = best_one.ukeire

                sum_tiles += best_ukeire * live_tiles

                # if we are going to have a tempai (on our second level) - let's also count its cost
                if shanten == 0:
                    # temporary update players hand and discards for calculations
                    next_tile_in_hand = best_one.find_tile_in_hand(self.player.closed_hand)
                    tile_for_discard = Tile(next_tile_in_hand, False)
                    self.player.tiles.remove(next_tile_in_hand)
                    self.player.discards.append(tile_for_discard)

                    cost_x_ukeire, _ = self._estimate_cost_x_ukeire(best_one, call_riichi=call_riichi)
                    if best_ukeire != 0:
                        average_costs.append((cost_x_ukeire / (best_ukeire * 4)))
                    # we reduce tile valuation for atodzuke
                    if result_has_atodzuke:
                        cost_x_ukeire /= 2
                    sum_cost += cost_x_ukeire

                    # restore original players hand and discard state
                    self.player.tiles.append(next_tile_in_hand)
                    self.player.discards.remove(tile_for_discard)

            self.player.tiles.remove(wait_136)

        discard_option.ukeire_second = sum_tiles
        if discard_option.shanten == 1:
            discard_option.second_level_cost = sum_cost
            if not average_costs:
                discard_option.average_second_level_cost = 0
            else:
                discard_option.average_second_level_cost = int(sum(average_costs) / len(average_costs))

        # restore original state of player hand and discards
        self.player.tiles = player_tiles_original
        self.player.discards = player_discards_original

    def _decide_if_use_chiitoitsu(self, shanten_with_chiitoitsu, shanten_without_chiitoitsu):
        # if it's late get 1-shanten for chiitoitsu instead of 2-shanten for another hand
        if len(self.player.discards) <= 10:
            border_shanten_without_chiitoitsu = 3
        else:
            border_shanten_without_chiitoitsu = 2

        if (shanten_with_chiitoitsu == 0 and shanten_without_chiitoitsu >= 1) or (
            shanten_with_chiitoitsu == 1 and shanten_without_chiitoitsu >= border_shanten_without_chiitoitsu
        ):
            shanten = shanten_with_chiitoitsu
            use_chiitoitsu = True
        else:
            shanten = shanten_without_chiitoitsu
            use_chiitoitsu = False

        return shanten, use_chiitoitsu

    @staticmethod
    def _default_sorting_rule(x):
        return (
            x.shanten,
            -x.ukeire,
            x.valuation,
        )

    @staticmethod
    def _sorting_rule_for_1_shanten(x):
        return (-x.second_level_cost,) + HandBuilder._sorting_rule_for_1_shanten_no_cost(x)

    @staticmethod
    def _sorting_rule_for_1_shanten_no_cost(x):
        return (
            -x.ukeire_second,
            -x.ukeire,
            x.valuation,
        )

    @staticmethod
    def _sorting_rule_for_2_3_shanten(x):
        return HandBuilder._sorting_rule_for_1_shanten_no_cost(x)

    @staticmethod
    def _sorting_rule_for_2_3_shanten_with_isolated(x, closed_hand_34):
        return (
            -x.ukeire_second,
            -x.ukeire,
            -is_tile_strictly_isolated(closed_hand_34, x.tile_to_discard),
            x.valuation,
        )

    @staticmethod
    def _sorting_rule_for_4_or_more_shanten(x):
        return (
            -x.ukeire,
            x.valuation,
        )

    @staticmethod
    def _sorting_rule_for_betaori(x):
        return (x.danger.get_weighted_danger(),) + HandBuilder._default_sorting_rule(x)

    def _choose_safest_tile_or_skip_meld(self, discard_options, after_meld):
        if after_meld:
            return None

        # we can't discard effective tile from the hand, let's fold
        DecisionsLogger.debug(log.DISCARD_SAFE_TILE, "There are only dangerous tiles. Discard safest tile.")
        return sorted(discard_options, key=self._sorting_rule_for_betaori)[0]

    def _choose_safest_tile(self, discard_options):
        return self._choose_safest_tile_or_skip_meld(discard_options, after_meld=False)

    def _choose_best_tile(self, discard_options, sorting_rule):
        assert discard_options

        threats_present = [x for x in discard_options if x.danger.get_max_danger() != 0]
        if threats_present:
            # try to discard safest tile for calculated ukeire border
            candidate = sorted(discard_options, key=sorting_rule)[0]
            ukeire_border = max(
                [
                    round((candidate.ukeire / 100) * DiscardOption.UKEIRE_DANGER_FILTER_PERCENTAGE),
                    DiscardOption.MIN_UKEIRE_DANGER_BORDER,
                ]
            )

            discard_options_within_borders = sorted(
                [x for x in discard_options if x.ukeire >= x.ukeire - ukeire_border],
                key=lambda x: (x.danger.get_weighted_danger(),) + sorting_rule(x),
            )
        else:
            discard_options_within_borders = discard_options

        DecisionsLogger.debug(log.DISCARD_OPTIONS, "All discard candidates", discard_options_within_borders)

        return discard_options_within_borders[0]

    def _choose_first_option_or_safe_tiles(self, chosen_candidates, all_discard_options, after_meld, sorting_lambda):
        # it looks like everything is fine
        if len(chosen_candidates):
            return self._choose_best_tile(chosen_candidates, sorting_lambda)

        return self._choose_safest_tile_or_skip_meld(all_discard_options, after_meld)

    def _choose_best_tanki_wait(self, discard_desc):
        discard_desc = sorted(discard_desc, key=lambda k: (k["hand_cost"], -k["weighted_danger"]), reverse=True)
        discard_desc = [x for x in discard_desc if x["hand_cost"] != 0]

        # we are guaranteed to have at least one wait with cost by caller logic
        assert len(discard_desc) > 0

        if len(discard_desc) == 1:
            return discard_desc[0]["discard_option"]

        non_furiten_waits = [x for x in discard_desc if not x["is_furiten"]]
        num_non_furiten_waits = len(non_furiten_waits)
        if num_non_furiten_waits == 1:
            return non_furiten_waits[0]["discard_option"]
        elif num_non_furiten_waits > 1:
            discard_desc = non_furiten_waits

        best_discard_desc = [x for x in discard_desc if x["hand_cost"] == discard_desc[0]["hand_cost"]]

        # first of all we choose the most expensive wait
        if len(best_discard_desc) == 1:
            return best_discard_desc[0]["discard_option"]

        best_ukeire = best_discard_desc[0]["discard_option"].ukeire
        diff = best_ukeire - best_discard_desc[1]["discard_option"].ukeire
        # if both tanki waits have the same ukeire
        if diff == 0:
            # case when we have 2 or 3 tiles to wait for
            if best_ukeire == 2 or best_ukeire == 3:
                best_discard_desc = sorted(
                    best_discard_desc,
                    key=lambda k: (TankiWait.tanki_wait_same_ukeire_2_3_prio[k["tanki_type"]], -k["weighted_danger"]),
                    reverse=True,
                )
                return best_discard_desc[0]["discard_option"]

            # case when we have 1 tile to wait for
            if best_ukeire == 1:
                best_discard_desc = sorted(
                    best_discard_desc,
                    key=lambda k: (TankiWait.tanki_wait_same_ukeire_1_prio[k["tanki_type"]], -k["weighted_danger"]),
                    reverse=True,
                )
                return best_discard_desc[0]["discard_option"]

            # should never reach here
            raise AssertionError("Can't chose tanki wait")

        # if one tanki wait has 1 more tile to wait than the other we only choose the latter one if it is
        # a wind or alike and the first one is not
        if diff == 1:
            prio_0 = TankiWait.tanki_wait_diff_ukeire_prio[best_discard_desc[0]["tanki_type"]]
            prio_1 = TankiWait.tanki_wait_diff_ukeire_prio[best_discard_desc[1]["tanki_type"]]
            if prio_1 > prio_0:
                return best_discard_desc[1]["discard_option"]

            return best_discard_desc[0]["discard_option"]

        if diff > 1:
            return best_discard_desc[0]["discard_option"]

        # if everything is the same we just choose the first one
        return best_discard_desc[0]["discard_option"]

    def _is_waiting_furiten(self, tile_34):
        discarded_tiles = [x.value // 4 for x in self.player.discards]
        return tile_34 in discarded_tiles

    def _is_discard_option_furiten(self, discard_option):
        is_furiten = False

        for waiting in discard_option.waiting:
            is_furiten = is_furiten or self._is_waiting_furiten(waiting)

        return is_furiten

    def _choose_best_discard_in_tempai(self, tiles, melds, discard_options, after_meld):
        # first of all we find tiles that have the best hand cost * ukeire value
        call_riichi = not (self.player.is_open_hand or after_meld)

        discard_desc = []
        player_tiles_copy = self.player.tiles[:]
        player_melds_copy = self.player.melds[:]

        closed_tiles_34 = TilesConverter.to_34_array(self.player.closed_hand)

        for discard_option in discard_options:
            tile = discard_option.find_tile_in_hand(self.player.closed_hand)
            # temporary remove discard option to estimate hand value
            self.player.tiles = tiles[:]
            self.player.tiles.remove(tile)
            # temporary replace melds
            self.player.melds = melds[:]
            # for kabe/suji handling
            discarded_tile = Tile(tile, False)
            self.player.discards.append(discarded_tile)

            is_furiten = self._is_discard_option_furiten(discard_option)

            if len(discard_option.waiting) == 1:
                waiting = discard_option.waiting[0]

                cost_x_ukeire, hand_cost = self._estimate_cost_x_ukeire(discard_option, call_riichi)

                # let's check if this is a tanki wait
                results, tiles_34 = self.divide_hand(self.player.tiles, waiting)
                result = results[0]

                tanki_type = None

                is_tanki = False
                for hand_set in result:
                    if waiting not in hand_set:
                        continue

                    if is_pair(hand_set):
                        is_tanki = True

                        if is_honor(waiting):
                            # TODO: differentiate between self honor and honor for all players
                            if waiting in self.player.valued_honors:
                                tanki_type = TankiWait.TANKI_WAIT_ALL_YAKUHAI
                            else:
                                tanki_type = TankiWait.TANKI_WAIT_NON_YAKUHAI
                            break

                        simplified_waiting = simplify(waiting)
                        have_suji, have_kabe = self.check_suji_and_kabe(closed_tiles_34, waiting)

                        # TODO: not sure about suji/kabe priority, so we keep them same for now
                        if 3 <= simplified_waiting <= 5:
                            if have_suji or have_kabe:
                                tanki_type = TankiWait.TANKI_WAIT_456_KABE
                            else:
                                tanki_type = TankiWait.TANKI_WAIT_456_RAW
                        elif 2 <= simplified_waiting <= 6:
                            if have_suji or have_kabe:
                                tanki_type = TankiWait.TANKI_WAIT_37_KABE
                            else:
                                tanki_type = TankiWait.TANKI_WAIT_37_RAW
                        elif 1 <= simplified_waiting <= 7:
                            if have_suji or have_kabe:
                                tanki_type = TankiWait.TANKI_WAIT_28_KABE
                            else:
                                tanki_type = TankiWait.TANKI_WAIT_28_RAW
                        else:
                            if have_suji or have_kabe:
                                tanki_type = TankiWait.TANKI_WAIT_69_KABE
                            else:
                                tanki_type = TankiWait.TANKI_WAIT_69_RAW
                        break

                discard_desc.append(
                    {
                        "discard_option": discard_option,
                        "hand_cost": hand_cost,
                        "cost_x_ukeire": cost_x_ukeire,
                        "is_furiten": is_furiten,
                        "is_tanki": is_tanki,
                        "tanki_type": tanki_type,
                        "max_danger": discard_option.danger.get_max_danger(),
                        "sum_danger": discard_option.danger.get_sum_danger(),
                        "weighted_danger": discard_option.danger.get_weighted_danger(),
                    }
                )
            else:
                cost_x_ukeire, _ = self._estimate_cost_x_ukeire(discard_option, call_riichi)

                discard_desc.append(
                    {
                        "discard_option": discard_option,
                        "hand_cost": None,
                        "cost_x_ukeire": cost_x_ukeire,
                        "is_furiten": is_furiten,
                        "is_tanki": False,
                        "tanki_type": None,
                        "max_danger": discard_option.danger.get_max_danger(),
                        "sum_danger": discard_option.danger.get_sum_danger(),
                        "weighted_danger": discard_option.danger.get_weighted_danger(),
                    }
                )

            # reverse all temporary tile tweaks
            self.player.tiles = player_tiles_copy
            self.player.melds = player_melds_copy
            self.player.discards.remove(discarded_tile)

        discard_desc = sorted(discard_desc, key=lambda k: (-k["cost_x_ukeire"], k["is_furiten"], k["weighted_danger"]))

        # if we don't have any good options, e.g. all our possible waits are karaten
        if discard_desc[0]["cost_x_ukeire"] == 0:
            # we still choose between options that give us tempai, because we may be going to formal tempai
            # with no hand cost
            return self._choose_safest_tile(discard_options)

        num_tanki_waits = len([x for x in discard_desc if x["is_tanki"]])

        # what if all our waits are tanki waits? we need a special handling for that case
        if num_tanki_waits == len(discard_options):
            return self._choose_best_tanki_wait(discard_desc)

        best_discard_desc = [x for x in discard_desc if x["cost_x_ukeire"] == discard_desc[0]["cost_x_ukeire"]]
        best_discard_desc = sorted(best_discard_desc, key=lambda k: (k["is_furiten"], k["weighted_danger"]))

        # if we have several options that give us similar wait
        return best_discard_desc[0]["discard_option"]

    def _choose_best_discard_with_1_shanten(
        self, tiles, melds, discard_options, after_meld, one_shanten_ukeire2_calculated_beforehand
    ):
        discard_options = sorted(discard_options, key=lambda x: (x.shanten, -x.ukeire))
        first_option = discard_options[0]

        # first we filter by ukeire
        ukeire_borders = self._choose_ukeire_borders(
            first_option, DiscardOption.UKEIRE_FIRST_FILTER_PERCENTAGE, "ukeire"
        )
        possible_options = self._filter_list_by_ukeire_borders(discard_options, first_option.ukeire, ukeire_borders)

        # FIXME: hack, sometimes we have already calculated it
        if not one_shanten_ukeire2_calculated_beforehand:
            for x in possible_options:
                self.calculate_second_level_ukeire(x, tiles, melds, after_meld)

        # then we filter by ukeire2
        possible_options = sorted(possible_options, key=self._sorting_rule_for_1_shanten_no_cost)
        possible_options = self._filter_list_by_percentage(
            possible_options, "ukeire_second", DiscardOption.UKEIRE_FIRST_FILTER_PERCENTAGE
        )

        # and finally we sort by main 1-shanten rule
        return self._choose_best_tile(
            sorted(possible_options, key=self._sorting_rule_for_1_shanten),
            self._sorting_rule_for_1_shanten,
        )

    def _choose_best_discard_with_2_3_shanten(self, tiles, melds, closed_hand, discard_options, after_meld):
        discard_options = sorted(discard_options, key=lambda x: (x.shanten, -x.ukeire))
        first_option = discard_options[0]
        closed_hand_34 = TilesConverter.to_34_array(closed_hand)

        # first we filter by ukeire
        ukeire_borders = self._choose_ukeire_borders(
            first_option, DiscardOption.UKEIRE_FIRST_FILTER_PERCENTAGE, "ukeire"
        )
        possible_options = self._filter_list_by_ukeire_borders(discard_options, first_option.ukeire, ukeire_borders)

        for x in possible_options:
            self.calculate_second_level_ukeire(x, tiles, melds, after_meld)

        # then we filter by ukeire 2
        possible_options = sorted(
            possible_options, key=lambda x: self._sorting_rule_for_2_3_shanten_with_isolated(x, closed_hand_34)
        )
        possible_options = self._filter_list_by_percentage(
            possible_options, "ukeire_second", DiscardOption.UKEIRE_SECOND_FILTER_PERCENTAGE
        )

        possible_options = self._try_keep_doras(
            possible_options, "ukeire_second", DiscardOption.UKEIRE_SECOND_FILTER_PERCENTAGE
        )
        assert possible_options

        DecisionsLogger.debug(log.DISCARD_OPTIONS, "Candidates after filtering by ukeire2", context=possible_options)

        return self._choose_best_tile(
            sorted(possible_options, key=lambda x: self._sorting_rule_for_2_3_shanten_with_isolated(x, closed_hand_34)),
            self._sorting_rule_for_2_3_shanten,
        )

    def _choose_best_discard_with_4_or_more_shanten(self, closed_hand, discard_options):
        discard_options = sorted(discard_options, key=lambda x: (x.shanten, -x.ukeire))
        first_option = discard_options[0]

        # we filter by ukeire
        ukeire_borders = self._choose_ukeire_borders(
            first_option, DiscardOption.UKEIRE_FIRST_FILTER_PERCENTAGE, "ukeire"
        )
        possible_options = self._filter_list_by_ukeire_borders(discard_options, first_option.ukeire, ukeire_borders)

        possible_options = sorted(possible_options, key=self._sorting_rule_for_4_or_more_shanten)

        possible_options = self._try_keep_doras(
            possible_options, "ukeire", DiscardOption.UKEIRE_FIRST_FILTER_PERCENTAGE
        )
        assert possible_options

        closed_hand_34 = TilesConverter.to_34_array(closed_hand)
        isolated_tiles = [x for x in possible_options if is_tile_strictly_isolated(closed_hand_34, x.tile_to_discard)]
        # isolated tiles should be discarded first
        if isolated_tiles:
            possible_options = isolated_tiles

        # let's sort tiles by value and let's choose less valuable tile to discard
        return self._choose_best_tile(
            sorted(possible_options, key=self._sorting_rule_for_4_or_more_shanten),
            self._sorting_rule_for_4_or_more_shanten,
        )

    def _try_keep_doras(self, discard_options, ukeire_field, filter_percentage):
        tiles_without_dora = [x for x in discard_options if x.count_of_dora == 0]
        # we have only dora candidates to discard
        if not tiles_without_dora:
            min_dora = min([x.count_of_dora for x in discard_options])
            min_dora_list = [x for x in discard_options if x.count_of_dora == min_dora]
            possible_options = min_dora_list
        else:
            # filter again - this time only tiles without dora
            possible_options = self._filter_list_by_percentage(tiles_without_dora, ukeire_field, filter_percentage)

        return possible_options

    def _find_acceptable_path_to_tempai(self, acceptable_discard_options, shanten):
        # this might be a bit conservative, because in tempai danger borders will be higher, but since
        # we expect that we need to discard a few more dangerous tiles before we get tempai, if we push
        # we can use danger borders for our current shanten number and it all compensates
        acceptable_discard_options_with_same_shanten = [x for x in acceptable_discard_options if x.shanten == shanten]
        # +1 because we need to discard one more tile to get to lower shanten number one more time
        # so if we want to meld and get 1-shanten we should have at least two tiles in hand we can discard
        # that don't increase shanten number
        if len(acceptable_discard_options_with_same_shanten) < shanten + 1:
            # there is no acceptable way for tempai even in theory
            return False

    @staticmethod
    def _filter_list_by_ukeire_borders(discard_options, ukeire, ukeire_borders):
        filteted = []

        for discard_option in discard_options:
            # let's choose tiles that are close to the max ukeire tile
            if discard_option.ukeire >= ukeire - ukeire_borders:
                filteted.append(discard_option)

        return filteted

    @staticmethod
    def _filter_list_by_percentage(items, attribute, percentage):
        filtered_options = []
        first_option = items[0]
        ukeire_borders = round((getattr(first_option, attribute) / 100) * percentage)
        for x in items:
            if getattr(x, attribute) >= getattr(first_option, attribute) - ukeire_borders:
                filtered_options.append(x)
        return filtered_options

    @staticmethod
    def _choose_ukeire_borders(first_option, border_percentage, border_field):
        ukeire_borders = round((getattr(first_option, border_field) / 100) * border_percentage)

        if first_option.shanten == 0 and ukeire_borders < DiscardOption.MIN_UKEIRE_TEMPAI_BORDER:
            ukeire_borders = DiscardOption.MIN_UKEIRE_TEMPAI_BORDER

        if first_option.shanten == 1 and ukeire_borders < DiscardOption.MIN_UKEIRE_SHANTEN_1_BORDER:
            ukeire_borders = DiscardOption.MIN_UKEIRE_SHANTEN_1_BORDER

        if first_option.shanten >= 2 and ukeire_borders < DiscardOption.MIN_UKEIRE_SHANTEN_2_BORDER:
            ukeire_borders = DiscardOption.MIN_UKEIRE_SHANTEN_2_BORDER

        return ukeire_borders

    def _estimate_cost_x_ukeire(self, discard_option, call_riichi):
        cost_x_ukeire_tsumo = 0
        cost_x_ukeire_ron = 0
        hand_cost_tsumo = 0
        hand_cost_ron = 0

        is_furiten = self._is_discard_option_furiten(discard_option)

        for waiting in discard_option.waiting:
            hand_value = self.player.ai.estimate_hand_value_or_get_from_cache(
                waiting, call_riichi=call_riichi, is_tsumo=True
            )
            if hand_value.error is None:
                hand_cost_tsumo = hand_value.cost["main"] + 2 * hand_value.cost["additional"]
                cost_x_ukeire_tsumo += hand_cost_tsumo * discard_option.wait_to_ukeire[waiting]

            if not is_furiten:
                hand_value = self.player.ai.estimate_hand_value_or_get_from_cache(
                    waiting, call_riichi=call_riichi, is_tsumo=False
                )
                if hand_value.error is None:
                    hand_cost_ron = hand_value.cost["main"]
                    cost_x_ukeire_ron += hand_cost_ron * discard_option.wait_to_ukeire[waiting]

        # these are abstract numbers used to compare different waits
        # some don't have yaku, some furiten, etc.
        # so we use an abstract formula of 1 tsumo cost + 3 ron costs
        cost_x_ukeire = cost_x_ukeire_tsumo + 3 * cost_x_ukeire_ron

        if len(discard_option.waiting) == 1:
            hand_cost = hand_cost_tsumo + 3 * hand_cost_ron
        else:
            hand_cost = None

        return cost_x_ukeire, hand_cost


class TankiWait:
    TANKI_WAIT_NON_YAKUHAI = 1
    TANKI_WAIT_SELF_YAKUHAI = 2
    TANKI_WAIT_ALL_YAKUHAI = 3
    TANKI_WAIT_69_KABE = 4
    TANKI_WAIT_69_SUJI = 5
    TANKI_WAIT_69_RAW = 6
    TANKI_WAIT_28_KABE = 7
    TANKI_WAIT_28_SUJI = 8
    TANKI_WAIT_28_RAW = 9
    TANKI_WAIT_37_KABE = 10
    TANKI_WAIT_37_SUJI = 11
    TANKI_WAIT_37_RAW = 12
    TANKI_WAIT_456_KABE = 13
    TANKI_WAIT_456_SUJI = 14
    TANKI_WAIT_456_RAW = 15

    tanki_wait_same_ukeire_2_3_prio = {
        TANKI_WAIT_NON_YAKUHAI: 15,
        TANKI_WAIT_69_KABE: 14,
        TANKI_WAIT_69_SUJI: 14,
        TANKI_WAIT_SELF_YAKUHAI: 13,
        TANKI_WAIT_ALL_YAKUHAI: 12,
        TANKI_WAIT_28_KABE: 11,
        TANKI_WAIT_28_SUJI: 11,
        TANKI_WAIT_37_KABE: 10,
        TANKI_WAIT_37_SUJI: 10,
        TANKI_WAIT_69_RAW: 9,
        TANKI_WAIT_456_KABE: 8,
        TANKI_WAIT_456_SUJI: 8,
        TANKI_WAIT_28_RAW: 7,
        TANKI_WAIT_456_RAW: 6,
        TANKI_WAIT_37_RAW: 5,
    }

    tanki_wait_same_ukeire_1_prio = {
        TANKI_WAIT_NON_YAKUHAI: 15,
        TANKI_WAIT_SELF_YAKUHAI: 14,
        TANKI_WAIT_ALL_YAKUHAI: 13,
        TANKI_WAIT_69_KABE: 12,
        TANKI_WAIT_69_SUJI: 12,
        TANKI_WAIT_28_KABE: 11,
        TANKI_WAIT_28_SUJI: 11,
        TANKI_WAIT_37_KABE: 10,
        TANKI_WAIT_37_SUJI: 10,
        TANKI_WAIT_69_RAW: 9,
        TANKI_WAIT_456_KABE: 8,
        TANKI_WAIT_456_SUJI: 8,
        TANKI_WAIT_28_RAW: 7,
        TANKI_WAIT_456_RAW: 6,
        TANKI_WAIT_37_RAW: 5,
    }

    tanki_wait_diff_ukeire_prio = {
        TANKI_WAIT_NON_YAKUHAI: 1,
        TANKI_WAIT_SELF_YAKUHAI: 1,
        TANKI_WAIT_ALL_YAKUHAI: 1,
        TANKI_WAIT_69_KABE: 1,
        TANKI_WAIT_69_SUJI: 1,
        TANKI_WAIT_28_KABE: 0,
        TANKI_WAIT_28_SUJI: 0,
        TANKI_WAIT_37_KABE: 0,
        TANKI_WAIT_37_SUJI: 0,
        TANKI_WAIT_69_RAW: 0,
        TANKI_WAIT_456_KABE: 0,
        TANKI_WAIT_456_SUJI: 0,
        TANKI_WAIT_28_RAW: 0,
        TANKI_WAIT_456_RAW: 0,
        TANKI_WAIT_37_RAW: 0,
    }

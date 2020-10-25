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
        discard_options, _ = self.find_discard_options(tiles, closed_hand, melds)

        # FIXME: looks kinda hacky and also we calculate second level ukeire twice for some tiles
        # we need to calculate ukeire2 beforehand for correct danger calculation
        for discard_option in discard_options:
            if discard_option.shanten == 1:
                self.calculate_second_level_ukeire(discard_option, tiles, melds)

        discard_options, threatening_players = self.player.ai.defence.mark_tiles_danger_for_threats(discard_options)

        if threatening_players:
            DecisionsLogger.debug(log.DEFENCE_THREATENING_ENEMY, "Threats", context=threatening_players)

        DecisionsLogger.debug(log.DISCARD_OPTIONS, "All discard candidates", discard_options)

        tiles_we_can_discard = [
            x for x in discard_options if x.danger.get_max_danger() <= x.danger.get_min_danger_border()
        ]
        if not tiles_we_can_discard:
            return self._chose_first_option_or_safe_tiles([], discard_options, after_meld, lambda x: ())

        # our strategy can affect discard options
        if self.ai.current_strategy:
            tiles_we_can_discard = self.ai.current_strategy.determine_what_to_discard(
                tiles_we_can_discard, closed_hand, melds
            )

        had_to_be_discarded_tiles = [x for x in tiles_we_can_discard if x.had_to_be_discarded]
        if had_to_be_discarded_tiles:

            def sorting_lambda(x):
                return (x.shanten, -x.ukeire, x.valuation)

            tiles_we_can_discard = sorted(had_to_be_discarded_tiles, key=sorting_lambda)
            return self._chose_first_option_or_safe_tiles(
                tiles_we_can_discard, discard_options, after_meld, sorting_lambda
            )

        # remove needed tiles from discard options
        tiles_we_can_discard = [x for x in tiles_we_can_discard if not x.had_to_be_saved]

        tiles_we_can_discard = sorted(tiles_we_can_discard, key=lambda x: (x.shanten, -x.ukeire))
        first_option = tiles_we_can_discard[0]
        results_with_same_shanten = [x for x in tiles_we_can_discard if x.shanten == first_option.shanten]

        possible_options = [first_option]
        ukeire_borders = self._choose_ukeire_borders(
            first_option, DiscardOption.UKEIRE_FIRST_FILTER_PERCENTAGE, "ukeire"
        )
        for discard_option in results_with_same_shanten:
            # there is no sense to check already chosen tile
            if discard_option.tile_to_discard == first_option.tile_to_discard:
                continue

            # let's choose tiles that are close to the max ukeire tile
            if discard_option.ukeire >= first_option.ukeire - ukeire_borders:
                possible_options.append(discard_option)

        if first_option.shanten in [1, 2, 3]:
            ukeire_field = "ukeire_second"
            for x in possible_options:
                self.calculate_second_level_ukeire(x, tiles, melds)

            possible_options = sorted(possible_options, key=lambda x: (-getattr(x, ukeire_field), x.valuation))
            possible_options = self._filter_list_by_percentage(
                possible_options, ukeire_field, DiscardOption.UKEIRE_FIRST_FILTER_PERCENTAGE
            )
        else:
            ukeire_field = "ukeire"
            possible_options = sorted(possible_options, key=lambda x: (-getattr(x, ukeire_field), x.valuation))

        # only one option - so we choose it
        if len(possible_options) == 1:
            return possible_options[0]

        # tempai state has a special handling
        if first_option.shanten == 0:
            other_tiles_with_same_shanten = [x for x in possible_options if x.shanten == 0]
            return self._choose_best_discard_in_tempai(tiles, melds, other_tiles_with_same_shanten)

        tiles_without_dora = [x for x in possible_options if x.count_of_dora == 0]

        # we have only dora candidates to discard
        if not tiles_without_dora:
            min_dora = min([x.count_of_dora for x in possible_options])
            min_dora_list = [x for x in possible_options if x.count_of_dora == min_dora]

            def sorting_lambda(x):
                return (-getattr(x, ukeire_field), x.valuation)

            return self._chose_first_option_or_safe_tiles(
                sorted(min_dora_list, key=sorting_lambda),
                discard_options,
                after_meld,
                sorting_lambda,
            )

        # only one option - so we choose it
        if len(tiles_without_dora) == 1:
            return tiles_without_dora[0]

        # 1-shanten hands have special handling - we can consider future hand cost here
        if first_option.shanten == 1:

            def sorting_lambda(x):
                return (-x.second_level_cost, -x.ukeire_second, x.valuation)

            return self._chose_first_option_or_safe_tiles(
                sorted(tiles_without_dora, key=sorting_lambda),
                discard_options,
                after_meld,
                sorting_lambda,
            )

        if first_option.shanten == 2 or first_option.shanten == 3:
            filtered_options = self._filter_list_by_percentage(
                tiles_without_dora, ukeire_field, DiscardOption.UKEIRE_SECOND_FILTER_PERCENTAGE
            )
        # we should also consider borders for 3+ shanten hands
        else:
            best_option_without_dora = tiles_without_dora[0]
            ukeire_borders = self._choose_ukeire_borders(
                best_option_without_dora, DiscardOption.UKEIRE_SECOND_FILTER_PERCENTAGE, ukeire_field
            )
            filtered_options = []
            for discard_option in tiles_without_dora:
                val = getattr(best_option_without_dora, ukeire_field) - ukeire_borders
                if getattr(discard_option, ukeire_field) >= val:
                    filtered_options.append(discard_option)

        DecisionsLogger.debug(log.DISCARD_OPTIONS, "Candidates after filtering by ukeire2", context=possible_options)

        closed_hand_34 = TilesConverter.to_34_array(closed_hand)
        isolated_tiles = [x for x in filtered_options if is_tile_strictly_isolated(closed_hand_34, x.tile_to_discard)]
        # isolated tiles should be discarded first
        if isolated_tiles:

            def sorting_lambda(x):
                return (x.valuation,)

            # let's sort tiles by value and let's choose less valuable tile to discard
            return self._chose_first_option_or_safe_tiles(
                sorted(isolated_tiles, key=sorting_lambda),
                discard_options,
                after_meld,
                sorting_lambda,
            )

        # there are no isolated tiles or we don't care about them
        # let's discard tile with greater ukeire/ukeire2
        def sorting_lambda(x):
            return (-getattr(x, ukeire_field), x.valuation)

        filtered_options = sorted(filtered_options, key=sorting_lambda)
        first_option = self._chose_first_option_or_safe_tiles(
            filtered_options, discard_options, after_meld, sorting_lambda
        )

        other_tiles_with_same_ukeire = [
            x for x in filtered_options if getattr(x, ukeire_field) == getattr(first_option, ukeire_field)
        ]

        # it will happen with shanten=1, all tiles will have ukeire_second == 0
        # or in tempai we can have several tiles with same ukeire
        if other_tiles_with_same_ukeire:

            def sorting_lambda(x):
                return (x.valuation,)

            return self._chose_first_option_or_safe_tiles(
                sorted(other_tiles_with_same_ukeire, key=sorting_lambda),
                discard_options,
                after_meld,
                sorting_lambda,
            )

        # we have only one candidate to discard with greater ukeire
        return first_option

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

    def calculate_shanten(self, tiles_34, open_sets_34=None):
        shanten_with_chiitoitsu = self.ai.shanten_calculator.calculate_shanten(tiles_34, open_sets_34, chiitoitsu=True)
        shanten_without_chiitoitsu = self.ai.shanten_calculator.calculate_shanten(
            tiles_34, open_sets_34, chiitoitsu=False
        )

        if (shanten_with_chiitoitsu == 0 and shanten_without_chiitoitsu >= 1) or (
            shanten_with_chiitoitsu == 1 and shanten_without_chiitoitsu >= 3
        ):
            shanten = shanten_with_chiitoitsu
            use_chiitoitsu = True
        else:
            shanten = shanten_without_chiitoitsu
            use_chiitoitsu = False

        return shanten, use_chiitoitsu

    def calculate_waits(self, tiles_34, open_sets_34=None):
        """
        :param tiles_34: array of tiles in 34 formant, 13 of them (this is important)
        :param open_sets_34: array of array with tiles in 34 format
        :return: array of waits in 34 format and number of shanten
        """
        shanten, use_chiitoitsu = self.calculate_shanten(tiles_34, open_sets_34)

        waiting = []
        for j in range(0, 34):
            if tiles_34[j] == 4:
                continue

            tiles_34[j] += 1

            key = "{},{},{}".format(
                "".join([str(x) for x in tiles_34]), ";".join([str(x) for x in open_sets_34]), use_chiitoitsu and 1 or 0
            )

            if key in self.ai.hand_cache:
                new_shanten = self.ai.hand_cache[key]
            else:
                new_shanten = self.ai.shanten_calculator.calculate_shanten(
                    tiles_34, open_sets_34, chiitoitsu=use_chiitoitsu
                )
                self.ai.hand_cache[key] = new_shanten

            if new_shanten == shanten - 1:
                waiting.append(j)

            tiles_34[j] -= 1

        return waiting, shanten

    def find_discard_options(self, tiles, closed_hand, melds=None):
        """
        :param tiles: array of tiles in 136 format
        :param closed_hand: array of tiles in 136 format
        :param melds:
        :return:
        """
        if melds is None:
            melds = []

        open_sets_34 = [x.tiles_34 for x in melds]

        tiles_34 = TilesConverter.to_34_array(tiles)
        closed_tiles_34 = TilesConverter.to_34_array(closed_hand)
        is_agari = self.ai.agari.is_agari(tiles_34, self.player.meld_34_tiles)

        results = []
        for hand_tile in range(0, 34):
            if not closed_tiles_34[hand_tile]:
                continue

            tiles_34[hand_tile] -= 1
            waiting, shanten = self.calculate_waits(tiles_34, open_sets_34)
            tiles_34[hand_tile] += 1

            if waiting:
                wait_to_ukeire = dict(zip(waiting, [self.count_tiles([x], closed_tiles_34) for x in waiting]))
                results.append(
                    DiscardOption(
                        player=self.player,
                        shanten=shanten,
                        tile_to_discard=hand_tile,
                        waiting=waiting,
                        ukeire=self.count_tiles(waiting, closed_tiles_34),
                        wait_to_ukeire=wait_to_ukeire,
                    )
                )

        if is_agari:
            shanten = Shanten.AGARI_STATE
        else:
            shanten, _ = self.calculate_shanten(tiles_34, open_sets_34)

        return results, shanten

    def count_tiles(self, waiting, tiles_34):
        n = 0
        for tile_34 in waiting:
            n += 4 - self.player.number_of_revealed_tiles(tile_34, tiles_34)
        return n

    def divide_hand(self, tiles, waiting):
        tiles_copy = tiles.copy()

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

    def calculate_second_level_ukeire(self, discard_option, tiles, melds):
        not_suitable_tiles = self.ai.current_strategy and self.ai.current_strategy.not_suitable_tiles or []
        call_riichi = not self.player.is_open_hand

        # we are going to do manipulations that require player hand to be updated
        # so we save original tiles here and restore it at the end of the function
        player_tiles_original = self.player.tiles.copy()

        tile_in_hand = discard_option.find_tile_in_hand(self.player.closed_hand)

        self.player.tiles = tiles.copy()
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

            results, shanten = self.find_discard_options(self.player.tiles, self.player.closed_hand, melds)
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

                        if (ukeire > best_ukeire) or (ukeire >= best_ukeire and not has_atodzuke):
                            best_ukeire = ukeire
                            best_one = result
                            result_has_atodzuke = has_atodzuke
                else:
                    best_one = sorted(results, key=lambda x: -x.ukeire)[0]
                    best_ukeire = best_one.ukeire

                sum_tiles += best_ukeire * live_tiles

                # if we are going to have a tempai (on our second level) - let's also count its cost
                if shanten == 0:
                    next_tile_in_hand = best_one.find_tile_in_hand(self.player.closed_hand)
                    self.player.tiles.remove(next_tile_in_hand)
                    cost_x_ukeire, _ = self._estimate_cost_x_ukeire(best_one, call_riichi=call_riichi)
                    if best_ukeire != 0:
                        average_costs.append((cost_x_ukeire / (best_ukeire * 4)))
                    # we reduce tile valuation for atodzuke
                    if result_has_atodzuke:
                        cost_x_ukeire /= 2
                    sum_cost += cost_x_ukeire
                    self.player.tiles.append(next_tile_in_hand)

            self.player.tiles.remove(wait_136)

        discard_option.ukeire_second = sum_tiles
        if discard_option.shanten == 1:
            discard_option.second_level_cost = sum_cost
            if not average_costs:
                discard_option.average_second_level_cost = 0
            else:
                discard_option.average_second_level_cost = int(sum(average_costs) / len(average_costs))

        # restore original state of player hand
        self.player.tiles = player_tiles_original

    def _chose_first_option_or_safe_tiles(self, chosen_candidates, all_discard_options, after_meld, sorting_lambda):
        # it looks like everything is fine
        if len(chosen_candidates):
            # try to discard safest tile for calculated ukeire border
            candidate = chosen_candidates[0]
            ukeire_border = max(
                [
                    round((candidate.ukeire / 100) * DiscardOption.UKEIRE_DANGER_FILTER_PERCENTAGE),
                    DiscardOption.MIN_UKEIRE_DANGER_BORDER,
                ]
            )

            options_to_chose = sorted(
                [x for x in chosen_candidates if x.ukeire >= x.ukeire - ukeire_border],
                key=lambda x: (x.danger.get_max_danger(),) + sorting_lambda(x),
            )

            DecisionsLogger.debug(log.DISCARD_OPTIONS, "All discard candidates", options_to_chose)

            return options_to_chose[0]
        # we don't want to open hand in that case
        elif after_meld:
            return None

        # we can't discard effective tile from the hand, let's fold
        DecisionsLogger.debug(log.DISCARD_SAFE_TILE, "There are only dangerous tiles. Discard safest tile.")
        return sorted(all_discard_options, key=lambda x: (x.danger.get_max_danger(),) + sorting_lambda(x))[0]

    def _choose_best_tanki_wait(self, discard_desc):
        discard_desc = sorted(discard_desc, key=lambda k: (k["hand_cost"], -k["max_danger"]), reverse=True)

        # we are always choosing between exactly two tanki waits
        assert len(discard_desc) == 2

        discard_desc = [x for x in discard_desc if x["hand_cost"] != 0]

        # we are guaranteed to have at least one wait with cost by caller logic
        assert len(discard_desc) > 0

        if len(discard_desc) == 1:
            return discard_desc[0]["discard_option"]

        # if not 1 then 2
        assert len(discard_desc) == 2

        num_furiten_waits = len([x for x in discard_desc if x["is_furiten"]])
        # if we choose tanki, we always prefer non-furiten wait over furiten one, no matter what the cost is
        if num_furiten_waits == 1:
            return [x for x in discard_desc if not x["is_furiten"]][0]["discard_option"]

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
                    key=lambda k: (TankiWait.tanki_wait_same_ukeire_2_3_prio[k["tanki_type"]], -k["max_danger"]),
                    reverse=True,
                )
                return best_discard_desc[0]["discard_option"]

            # case when we have 1 tile to wait for
            if best_ukeire == 1:
                best_discard_desc = sorted(
                    best_discard_desc,
                    key=lambda k: (TankiWait.tanki_wait_same_ukeire_1_prio[k["tanki_type"]], -k["max_danger"]),
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

    def _choose_best_discard_in_tempai(self, tiles, melds, discard_options):
        # first of all we find tiles that have the best hand cost * ukeire value
        call_riichi = not self.player.is_open_hand

        discard_desc = []
        player_tiles_copy = self.player.tiles.copy()
        player_melds_copy = self.player.melds.copy()

        closed_tiles_34 = TilesConverter.to_34_array(self.player.closed_hand)

        for discard_option in discard_options:
            tile = discard_option.find_tile_in_hand(self.player.closed_hand)
            # temporary remove discard option to estimate hand value
            self.player.tiles = tiles.copy()
            self.player.tiles.remove(tile)
            # temporary replace melds
            self.player.melds = melds.copy()
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
                    }
                )

            # reverse all temporary tile tweaks
            self.player.tiles = player_tiles_copy
            self.player.melds = player_melds_copy
            self.player.discards.remove(discarded_tile)

        discard_desc = sorted(
            discard_desc, key=lambda k: (k["cost_x_ukeire"], not k["is_furiten"], -k["max_danger"]), reverse=True
        )

        # if we don't have any good options, e.g. all our possible waits ara karaten
        if discard_desc[0]["cost_x_ukeire"] == 0:
            return sorted(discard_options, key=lambda x: (-x.danger.get_max_danger(), x.valuation))[0]

        num_tanki_waits = len([x for x in discard_desc if x["is_tanki"]])

        # what if all our waits are tanki waits? we need a special handling for that case
        if num_tanki_waits == len(discard_options):
            return self._choose_best_tanki_wait(discard_desc)

        best_discard_desc = [x for x in discard_desc if x["cost_x_ukeire"] == discard_desc[0]["cost_x_ukeire"]]
        best_discard_desc = sorted(best_discard_desc, key=lambda k: (-k["max_danger"]))

        # we only have one best option based on ukeire and cost, nothing more to do here
        if len(best_discard_desc) == 1:
            return best_discard_desc[0]["discard_option"]

        # if we have several options that give us similar wait
        return best_discard_desc[0]["discard_option"]

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
            hand_value = self.player.ai.estimate_hand_value(waiting, call_riichi=call_riichi, is_tsumo=True)
            if hand_value.error is None:
                hand_cost_tsumo = hand_value.cost["main"] + 2 * hand_value.cost["additional"]
                cost_x_ukeire_tsumo += hand_cost_tsumo * discard_option.wait_to_ukeire[waiting]

            if not is_furiten:
                hand_value = self.player.ai.estimate_hand_value(waiting, call_riichi=call_riichi, is_tsumo=False)
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

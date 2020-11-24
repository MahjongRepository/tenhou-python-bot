import utils.decisions_constants as log
from mahjong.tile import TilesConverter


class PlacementHandler:
    def __init__(self, player):
        self.player = player
        self.table = player.table

    def get_allowed_danger_modifier(self) -> int:
        placement = self.get_current_placement()
        placement_evaluation = self._get_placement_evaluation(placement)

        if placement_evaluation == Placement.VERY_COMFORTABLE_FIRST:
            if self.is_late_round:
                self.player.logger.debug(
                    log.PLACEMENT_DANGER_MODIFIER,
                    "Very comfortable first and late round",
                    {"placement": placement, "placement_evaluation": placement_evaluation},
                )
                return Placement.NO_RISK_DANGER_MODIFIER

            self.player.logger.debug(
                log.PLACEMENT_DANGER_MODIFIER,
                "Very comfortable first and NOT late round",
                {"placement": placement, "placement_evaluation": placement_evaluation},
            )
            return Placement.MODERATE_DANGER_MODIFIER

        if placement_evaluation == Placement.COMFORTABLE_FIRST:
            if self.is_late_round:
                self.player.logger.debug(
                    log.PLACEMENT_DANGER_MODIFIER,
                    "Comfortable first and late round",
                    {"placement": placement, "placement_evaluation": placement_evaluation},
                )
                return Placement.MODERATE_DANGER_MODIFIER

        return Placement.DEFAULT_DANGER_MODIFIER

    # TODO: different logic for tournament games
    def must_riichi(self, has_yaku, num_waits, cost_with_riichi, cost_with_damaten) -> int:
        # now we only change our decisions for oorasu
        if not self.is_oorasu:
            return Placement.DEFAULT_RIICHI_DECISION

        placement = self.get_current_placement()
        if not placement:
            return Placement.DEFAULT_RIICHI_DECISION

        placement_evaluation = self._get_placement_evaluation(placement)

        logger_context = {
            "placement": placement,
            "placement_evaluation": placement_evaluation,
            "has_yaku": has_yaku,
            "num_waits": num_waits,
            "cost_with_riichi": cost_with_riichi,
            "cost_with_damaten": cost_with_damaten,
            "round_step": self.player.round_step,
        }

        if placement["place"] == 1:
            if has_yaku:
                self.player.logger.debug(log.PLACEMENT_RIICHI_OR_DAMATEN, "1st place, has yaku", logger_context)
                return Placement.MUST_DAMATEN

            # no yaku but we can just sit here and chill
            if placement_evaluation >= Placement.VERY_COMFORTABLE_FIRST:
                self.player.logger.debug(
                    log.PLACEMENT_RIICHI_OR_DAMATEN, "1st place, very comfortable first", logger_context
                )
                return Placement.MUST_DAMATEN

            if placement_evaluation >= Placement.COMFORTABLE_FIRST:
                # just chill
                if num_waits < 6 or self.player.round_step > 11:
                    self.player.logger.debug(
                        log.PLACEMENT_RIICHI_OR_DAMATEN,
                        "1st place, comfortable first, late round, < 6 waits",
                        logger_context,
                    )
                    return Placement.MUST_DAMATEN

        if placement["place"] == 2:
            if cost_with_damaten < placement["diff_with_1st"] <= cost_with_riichi * 2:
                if placement["diff_with_4th"] >= Placement.COMFORTABLE_DIFF_FOR_RISK:
                    self.player.logger.debug(
                        log.PLACEMENT_RIICHI_OR_DAMATEN, "2st place, we are good to risk", logger_context
                    )
                    return Placement.MUST_RIICHI

        # general rule for 2nd and 3rd places:
        if (placement["place"] == 2 or placement["place"] == 3) and has_yaku:
            # we can play more greedy on second place hoping for tsumo, ippatsu or uras
            # moreover riichi cost here is a minimal one
            if placement["place"] == 2:
                if placement["diff_with_4th"] <= 1000:
                    multiplier = 2
                else:
                    multiplier = 4
            else:
                multiplier = 2

            if (
                placement["diff_with_next_up"] > cost_with_riichi * multiplier
                and placement["diff_with_next_down"] <= 1000
            ):
                self.player.logger.debug(log.PLACEMENT_RIICHI_OR_DAMATEN, "not 4st place and has yaku", logger_context)
                return Placement.MUST_DAMATEN

        if placement["place"] == 4:
            # TODO: consider going for better hand
            if cost_with_damaten < placement["diff_with_3rd"]:
                self.player.logger.debug(log.PLACEMENT_RIICHI_OR_DAMATEN, "4st place, let's riichi", logger_context)
                return Placement.MUST_RIICHI

        return Placement.DEFAULT_RIICHI_DECISION

    def should_call_win(self, cost, is_tsumo, enemy_seat):
        # we currently don't support win skipping for tsumo
        if is_tsumo:
            return True

        # never skip win if we are the dealer
        if self.player.is_dealer:
            return True

        placement = self.get_current_placement()
        if not placement:
            return True

        needed_cost = self.get_minimal_cost_needed(placement=placement)
        if needed_cost == 0:
            return True

        # currently we don't support logic other than for 4th place
        assert self.player == self.table.get_players_sorted_by_scores()[3]
        first_place = self.table.get_players_sorted_by_scores()[0]
        third_place = self.table.get_players_sorted_by_scores()[2]

        num_players_over_30000 = len([x for x in self.table.players if x.scores >= 30000])
        direct_hit_cost = cost["main"] + cost["main_bonus"]
        if enemy_seat == third_place.seat:
            covered_cost = direct_hit_cost * 2 + cost["kyoutaku_bonus"]
        else:
            covered_cost = cost["total"]

        logger_context = {
            "placement": placement,
            "needed_cost": needed_cost,
            "covered_cost": covered_cost,
            "is_tsumo": is_tsumo,
            "closest_enemy_seat": third_place.seat,
            "enemy_seat_ron": enemy_seat,
            "num_players_over_30000": num_players_over_30000,
        }

        if not self.is_west_4:
            # check if we can make it to the west round
            if num_players_over_30000 == 0:
                self.player.logger.debug(log.AGARI, "Decided to take ron when no enemies have 30k", logger_context)
                return True

            if num_players_over_30000 == 1:
                if enemy_seat == first_place.seat:
                    if first_place.scores < 30000 + direct_hit_cost:
                        self.player.logger.debug(
                            log.AGARI, "Decided to take ron from first place, so no enemies have 30k", logger_context
                        )
                        return True

        if covered_cost < needed_cost:
            self.player.logger.debug(log.AGARI, "Decided to skip ron", logger_context)
            return False

        self.player.logger.debug(log.AGARI, "Decided to take ron for better placement", logger_context)
        return True

    def get_minimal_cost_needed(self, placement=None):
        if not self.is_oorasu:
            return 0

        if not placement:
            placement = self.get_current_placement()
            if not placement:
                return 0

        if placement["place"] == 4:
            third_place = self.table.get_players_sorted_by_scores()[2]

            extra = 0
            if self.player.first_seat > third_place.first_seat:
                extra = 100

            return placement["diff_with_next_up"] + extra

        return 0

    def get_minimal_cost_needed_considering_west(self, placement=None) -> int:
        minimal_cost = self.get_minimal_cost_needed(placement)
        if not minimal_cost:
            return 0

        if not placement:
            placement = self.get_current_placement()

        if placement["place"] != 4:
            return minimal_cost

        num_players_over_30000 = len([x for x in self.player.table.players if x.scores >= 30000])
        if num_players_over_30000 == 0:
            return 1000

        if num_players_over_30000 == 1:
            minimal_cost = min(minimal_cost, self.player.table.get_players_sorted_by_scores()[0].scores - 30000)

        return minimal_cost

    def get_current_placement(self):
        if not self.points_initialized:
            return None

        players_by_points = self.table.get_players_sorted_by_scores()
        current_place = players_by_points.index(self.player)

        return {
            "place": current_place + 1,
            "points": self.player.scores,
            "diff_with_1st": abs(self.player.scores - players_by_points[0].scores),
            "diff_with_2nd": abs(self.player.scores - players_by_points[1].scores),
            "diff_with_3rd": abs(self.player.scores - players_by_points[2].scores),
            "diff_with_4th": abs(self.player.scores - players_by_points[3].scores),
            "diff_with_next_up": abs(self.player.scores - players_by_points[max(0, current_place - 1)].scores),
            "diff_with_next_down": abs(self.player.scores - players_by_points[min(3, current_place + 1)].scores),
        }

    def _get_placement_evaluation(self, placement) -> int:
        if not placement:
            return Placement.NEUTRAL

        if placement["place"] == 1 and placement["points"] >= Placement.COMFORTABLE_POINTS:
            assert placement["diff_with_2nd"] >= 0
            if placement["diff_with_2nd"] >= Placement.VERY_COMFORTABLE_DIFF:
                return Placement.VERY_COMFORTABLE_FIRST

            if placement["diff_with_2nd"] >= self.comfortable_diff:
                return Placement.COMFORTABLE_FIRST

        return Placement.NEUTRAL

    def must_push(self, threats, tile_136, num_shanten, tempai_cost=0) -> bool:
        if not self.is_oorasu:
            return False

        if not threats:
            return False

        placement = self.get_current_placement()
        if not placement:
            return False

        logger_context = {
            "tile": TilesConverter.to_one_line_string([tile_136]),
            "shanten": num_shanten,
            "tempai_cost": tempai_cost,
            "placement": placement,
        }

        # always push if we are 4th - nothing to lose
        if placement["place"] == 4:
            # TODO: more subtle rules are possible for rare situations
            self.player.logger.debug(log.PLACEMENT_PUSH_DECISION, "We are 4th in oorasu and must push", logger_context)
            return True

        # don't force push with 2 or more shanten if we are not 4th
        if num_shanten > 1:
            return False

        # if there are several threats let's follow our usual rules and otherwise hope that other player wins
        if len(threats) > 1:
            return False

        # here we know there is exactly one threat
        threat = threats[0]
        players_by_points = self.table.get_players_sorted_by_scores()
        fourth_place = players_by_points[3]
        diff_with_4th = placement["diff_with_4th"]

        if placement["place"] == 3:
            # 4th place is not a threat so we don't fear his win
            if threat.enemy != fourth_place:
                return False

            # it's not _must_ to push against dealer, let's decide considering other factors
            if fourth_place.is_dealer:
                return False

            if num_shanten == 0 and self.player.round_step < 10:
                # enemy player is gonna get us with tsumo mangan, let's attack if it's early
                if diff_with_4th < self.comfortable_diff:
                    self.player.logger.debug(
                        log.PLACEMENT_PUSH_DECISION,
                        "We are 3rd in oorasu and must push in early game to secure 3rd place",
                        logger_context,
                    )
                    return True
            else:
                if diff_with_4th < Placement.RYUKOKU_MINIMUM_DIFF:
                    self.player.logger.debug(
                        log.PLACEMENT_PUSH_DECISION,
                        "We are 3rd in oorasu and must push to secure 3rd place",
                        logger_context,
                    )
                    return True

            return False

        if placement["place"] == 2:
            if threat.enemy == fourth_place:
                if diff_with_4th < Placement.COMFORTABLE_DIFF_FOR_RISK + self.table_bonus_direct:
                    return False

            if placement["diff_with_3rd"] < self.comfortable_diff:
                return False

            if num_shanten == 0:
                # we will push if we can get 1st with this hand with not much risk
                if placement["diff_with_1st"] <= tempai_cost + self.table_bonus_indirect:
                    self.player.logger.debug(
                        log.PLACEMENT_PUSH_DECISION, "We are 2nd in oorasu and must push to reach 1st", logger_context
                    )
                    return True
            else:
                if placement["diff_with_1st"] <= tempai_cost + self.table_bonus_indirect:
                    self.player.logger.debug(
                        log.PLACEMENT_PUSH_DECISION, "We are 2nd in oorasu and must push to reach 1st", logger_context
                    )
                    return True

            return False

        if placement["place"] == 1:
            second_place = players_by_points[1]
            if threat.enemy != second_place:
                return False

            if placement["diff_with_3rd"] < self.comfortable_diff:
                return False

            if num_shanten == 0 and self.player.round_step < 10:
                if placement["diff_with_2nd"] < self.comfortable_diff:
                    self.player.logger.debug(
                        log.PLACEMENT_PUSH_DECISION,
                        "We are 1st in oorasu and must push in early game to secure 1st",
                        logger_context,
                    )
                    return True
            else:
                if placement["diff_with_2nd"] <= Placement.RYUKOKU_MINIMUM_DIFF:
                    self.player.logger.debug(
                        log.PLACEMENT_PUSH_DECISION, "We are 1st in oorasu and must push to secure 1st", logger_context
                    )
                    return True

            return False

        # actually should never get here, but let's leave it in case we modify this code
        return False

    @property
    def comfortable_diff(self) -> int:
        if self.player.is_dealer:
            base = Placement.COMFORTABLE_DIFF_DEALER
        else:
            base = Placement.COMFORTABLE_DIFF_NON_DEALER

        bonus = self.table_bonus_tsumo

        return base + bonus

    @property
    def table_bonus_direct(self) -> int:
        return self.table.count_of_riichi_sticks * 1000 + self.table.count_of_honba_sticks * 600

    @property
    def table_bonus_tsumo(self) -> int:
        return self.table.count_of_riichi_sticks * 1000 + self.table.count_of_honba_sticks * 400

    @property
    def table_bonus_indirect(self) -> int:
        return self.table.count_of_riichi_sticks * 1000 + self.table.count_of_honba_sticks * 300

    @property
    def points_initialized(self):
        if [x for x in self.table.get_players_sorted_by_scores() if x.scores is None]:
            return False
        return True

    @property
    def is_oorasu(self):
        # TODO: consider tonpu
        return self.table.round_wind_number >= 7

    @property
    def is_west_4(self):
        # TODO: consider tonpu
        return self.table.round_wind_number == 11

    @property
    def is_late_round(self):
        # TODO: consider tonpu
        return self.table.round_wind_number >= 6


class DummyPlacementHandler(PlacementHandler):
    """
    Use this class in config if you want to disable placement logic for bot
    """

    def get_allowed_danger_modifier(self) -> int:
        return Placement.DEFAULT_DANGER_MODIFIER

    def must_riichi(self, has_yaku, num_waits, cost_with_riichi, cost_with_damaten) -> int:
        return Placement.DEFAULT_RIICHI_DECISION

    def _get_placement_evaluation(self, placement) -> int:
        return Placement.NEUTRAL

    def should_call_win(self, cost, is_tsumo, enemy_seat):
        return True

    def get_minimal_cost_needed(self, placement=None) -> int:
        return 0

    def get_minimal_cost_needed_considering_west(self, placement=None) -> int:
        return 0

    def must_push(self, threats, tile_136, num_shanten, tempai_cost=0) -> bool:
        return False

    @property
    def comfortable_diff(self) -> int:
        return 0


class Placement:
    # TODO: account for honbas and riichi sticks on the table
    VERY_COMFORTABLE_DIFF = 24100
    COMFORTABLE_DIFF_FOR_RISK = 18100

    COMFORTABLE_DIFF_DEALER = 12100
    COMFORTABLE_DIFF_NON_DEALER = 10100

    COMFORTABLE_POINTS = 38000

    RYUKOKU_MINIMUM_DIFF = 4000

    # player position in the game
    # must go in ascending order from bad to good, so we can use <, > operators with them
    NEUTRAL = 0
    COMFORTABLE_FIRST = 1
    VERY_COMFORTABLE_FIRST = 2

    # riichi definitions
    DEFAULT_RIICHI_DECISION = 0
    MUST_RIICHI = 1
    MUST_DAMATEN = 2

    # danger modifier
    NO_RISK_DANGER_MODIFIER = -3
    MODERATE_DANGER_MODIFIER = -2
    DEFAULT_DANGER_MODIFIER = 0

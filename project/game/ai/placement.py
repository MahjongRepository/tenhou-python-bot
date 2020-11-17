import utils.decisions_constants as log


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
            if cost_with_damaten < placement["diff_with_1st"] <= cost_with_riichi:
                if placement["diff_with_4th"] >= Placement.COMFORTABLE_DIFF_FOR_RISK:
                    self.player.logger.debug(
                        log.PLACEMENT_RIICHI_OR_DAMATEN, "2st place, we are good to risk", logger_context
                    )
                    return Placement.MUST_RIICHI

        # TODO: special rules for 3rd place
        if placement["place"] == 4:
            # TODO: consider going for better hand
            if cost_with_damaten < placement["diff_with_3rd"]:
                self.player.logger.debug(log.PLACEMENT_RIICHI_OR_DAMATEN, "4st place, let's riichi", logger_context)
                return Placement.MUST_RIICHI

        # general rule:
        if placement["place"] != 4 and has_yaku:
            if placement["diff_with_next_up"] > cost_with_riichi * 2 and placement["diff_with_next_down"] <= 1000:
                self.player.logger.debug(log.PLACEMENT_RIICHI_OR_DAMATEN, "not 4st place and has yaku", logger_context)
                return Placement.MUST_DAMATEN

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

    def _get_placement_evaluation(self, placement) -> int:
        if not placement:
            return Placement.NEUTRAL

        if placement["place"] == 1 and placement["points"] >= Placement.COMFORTABLE_POINTS:
            assert placement["diff_with_2nd"] >= 0
            if placement["diff_with_2nd"] >= Placement.VERY_COMFORTABLE_DIFF:
                return Placement.VERY_COMFORTABLE_FIRST

            if placement["diff_with_2nd"] >= Placement.COMFORTABLE_DIFF:
                return Placement.COMFORTABLE_FIRST

        return Placement.NEUTRAL

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
        return Placement.NO_RISK_DANGER_MODIFIER

    def must_riichi(self, has_yaku, num_waits, cost_with_riichi, cost_with_damaten) -> int:
        return Placement.DEFAULT_RIICHI_DECISION

    def _get_placement_evaluation(self, placement) -> int:
        return Placement.NEUTRAL

    def should_call_win(self, cost, is_tsumo, enemy_seat):
        return True

    def get_minimal_cost_needed(self) -> int:
        return 0

    def get_minimal_cost_needed_considering_west(self) -> int:
        return 0


class Placement:
    # TODO: account for honbas and riichi sticks on the table
    VERY_COMFORTABLE_DIFF = 24100
    COMFORTABLE_DIFF_FOR_RISK = 18100
    COMFORTABLE_DIFF = 12100
    COMFORTABLE_POINTS = 38000

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

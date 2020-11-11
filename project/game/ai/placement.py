class PlacementHandler:
    def __init__(self, player):
        self.player = player
        self.table = player.table

    def get_allowed_danger_modifier(self) -> int:
        placement_evaluation = self.get_placement_evaluation(self.get_current_placement())

        if placement_evaluation == Placement.VERY_COMFORTABLE_FIRST:
            if self.is_late_round:
                return -3

            return -2

        if placement_evaluation == Placement.VERY_COMFORTABLE_FIRST:
            if self.is_late_round:
                return -2

        return 0

    # TODO: different logic for tournament games
    def must_riichi(self, has_yaku, num_waits, cost_with_riichi, cost_with_damaten):
        # now we only change our decisions for oorasu
        if not self.is_oorasu:
            return Placement.DEFAULT_RIICHI_DECISION

        placement = self.get_current_placement()
        if not placement:
            return Placement.DEFAULT_RIICHI_DECISION

        placement_evaluation = self.get_placement_evaluation(placement)

        if placement["place"] == 1:
            if has_yaku:
                return Placement.MUST_DAMATEN

            # no yaku but we can just sit here and chill
            if placement_evaluation >= Placement.VERY_COMFORTABLE_FIRST:
                return Placement.MUST_DAMATEN

            if placement_evaluation >= Placement.COMFORTABLE_FIRST:
                # just chill
                if num_waits < 6 or self.player.round_step > 11:
                    return Placement.MUST_DAMATEN

        if placement["place"] == 2:
            if cost_with_damaten < placement["diff_with_1st"] <= cost_with_riichi:
                if placement["diff_with_4th"] >= Placement.COMFORTABLE_DIFF_FOR_RISK:
                    return Placement.MUST_RIICHI

        # TODO: special rules for 3rd place
        if placement["place"] == 4:
            # TODO: consider going for better hand
            if cost_with_damaten < placement["diff_with_3rd"]:
                return Placement.MUST_RIICHI

        # general rule:
        if placement["place"] != 4 and has_yaku:
            if placement["diff_with_next_up"] > cost_with_riichi * 2 and placement["diff_with_next_down"] <= 1000:
                return Placement.MUST_DAMATEN

        return Placement.DEFAULT_RIICHI_DECISION

    def get_placement_evaluation(self, placement):
        if not placement:
            return Placement.NEUTRAL

        if placement["place"] == 1:
            assert placement["diff_with_2nd"] >= 0
            if placement["diff_with_2nd"] >= Placement.VERY_COMFORTABLE_DIFF:
                return Placement.VERY_COMFORTABLE_FIRST

            if placement["diff_with_2nd"] >= Placement.COMFORTABLE_FIRST:
                return Placement.COMFORTABLE_FIRST

        return Placement.NEUTRAL

    def get_current_placement(self):
        if not self.points_initialized:
            return None

        players_by_points = self.table.get_players_sorted_by_scores()
        current_place = players_by_points.index(self.player)

        return {
            "place": current_place + 1,
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
    def is_late_round(self):
        # TODO: consider tonpu
        return self.table.round_wind_number >= 6


class Placement:
    # TODO: account for honbas and riichi sticks on the table
    VERY_COMFORTABLE_DIFF = 24100
    COMFORTABLE_DIFF_FOR_RISK = 18100
    COMFORTABLE_DIFF = 12100

    # player position in the game
    # must go in ascending order from bad to good, so we can use <, > operators with them
    NEUTRAL = 0
    COMFORTABLE_FIRST = 1
    VERY_COMFORTABLE_FIRST = 2

    # riichi definitions
    DEFAULT_RIICHI_DECISION = 0
    MUST_RIICHI = 1
    MUST_DAMATEN = 2

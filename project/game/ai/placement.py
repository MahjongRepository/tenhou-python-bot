class PlacementHandler:
    def __init__(self, player):
        self.player = player
        self.table = player.table

    def get_allowed_danger_modifier(self) -> int:
        placement = self.get_placement_evaluation()

        if placement == Placement.VERY_COMFORTABLE_FIRST:
            if self.table.round_wind_number >= 6:
                return -3

            return -2

        if placement == Placement.VERY_COMFORTABLE_FIRST:
            if self.table.round_wind_number >= 6:
                return -2

        return 0

    def get_placement_evaluation(self):
        players_by_points = self.table.get_players_sorted_by_scores()
        player_with_max_points = players_by_points[0]
        second_place = players_by_points[1]

        # in case scores were not inited (by tests or whatever)
        if [x for x in players_by_points if x.scores is None]:
            return Placement.NEUTRAL

        if self.player == player_with_max_points:
            assert self.player.scores >= second_place.scores
            if self.player.scores - second_place.scores >= Placement.VERY_COMFORTABLE_FIRST_THRESHOLD:
                return Placement.VERY_COMFORTABLE_FIRST

            if self.player.scores - second_place.scores >= Placement.COMFORTABLE_FIRST:
                return Placement.COMFORTABLE_FIRST

        return Placement.NEUTRAL


class Placement:
    VERY_COMFORTABLE_FIRST_THRESHOLD = 25000
    COMFORTABLE_FIRST_THRESHOLD = 13000

    # player position in the game
    NEUTRAL = 0
    COMFORTABLE_FIRST = 1
    VERY_COMFORTABLE_FIRST = 2

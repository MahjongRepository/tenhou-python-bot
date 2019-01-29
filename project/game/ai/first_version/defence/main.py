from mahjong.tile import TilesConverter
from mahjong.utils import is_honor

from game.ai.first_version.helpers.defence import TileDanger
from game.ai.first_version.defence.enemy_analyzer import EnemyAnalyzer


class DefenceHandler:
    player = None
    _analyzed_enemies = None

    def __init__(self, player):
        self.player = player
        self._analyzed_enemies = None

    def calculate_tiles_danger(self, discard_candidates, enemy):
        closed_hand_34 = TilesConverter.to_34_array(self.player.closed_hand)

        for discard_option in discard_candidates:
            tile_34 = discard_option.tile_to_discard

            # special rules for honor
            if is_honor(tile_34):
                total_tiles = self.player.total_tiles(tile_34, closed_hand_34)

                if total_tiles == 3:
                    self._update_discard_candidate(
                        tile_34,
                        discard_candidates,
                        enemy.player.seat,
                        TileDanger.HONOR_THIRD
                    )

            # genbutsu
            if tile_34 in enemy.player.all_safe_tiles:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy.player.seat,
                    TileDanger.GENBUTSU
                )

            # safe tiles that can be safe based on the table situation
            if enemy.total_possible_forms_for_tile(tile_34) == 0:
                self._update_discard_candidate(
                    tile_34,
                    discard_candidates,
                    enemy.player.seat,
                    TileDanger.IMPOSSIBLE_WAIT
                )

        return discard_candidates

    def check_threat_and_mark_tiles_danger(self, discard_candidates):
        threatening_players = self._get_threatening_players()

        # we don't have a threat
        # so we can continue to build a hand as usual
        if not threatening_players:
            return discard_candidates, False

        tiles_that_we_can_discard = []
        if len(threatening_players) == 1:
            enemy = threatening_players[0]
            discard_candidates = self.calculate_tiles_danger(discard_candidates, enemy)

            enemy_assumed_hand_cost = enemy.assumed_hand_cost
            enemy_number_of_unverified_suji = enemy.number_of_unverified_suji
            danger_coefficient = (10 - enemy_number_of_unverified_suji) * 5

            for discard_candidate in discard_candidates:
                if discard_candidate.danger.get_total_danger(enemy.player.seat) == 0:
                    tiles_that_we_can_discard.append(discard_candidate)
                    continue

                # FIXME remove it when real tests will be implemented
                tiles_that_we_can_discard.append(discard_candidate)

                # FIXME add real value
                our_hand_cost = 1000

        # FIXME special rules for multiple threats

        return tiles_that_we_can_discard, True

    @property
    def analyzed_enemies(self):
        if self._analyzed_enemies:
            return self._analyzed_enemies

        self._analyzed_enemies = [EnemyAnalyzer(enemy) for enemy in self.player.ai.enemy_players]
        return self._analyzed_enemies

    def _get_threatening_players(self):
        result = []
        for player in self.analyzed_enemies:
            if player.is_threatening:
                result.append(player)
        return result

    def _update_discard_candidate(self, tile_34, discard_candidates, player, danger):
        for discard_candidate in discard_candidates:
            if discard_candidate.tile_to_discard == tile_34:
                discard_candidate.danger.set_danger(player, danger)

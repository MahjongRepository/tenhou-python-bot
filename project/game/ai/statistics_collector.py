from mahjong.utils import is_honor, plus_dora, simplify
from utils.decisions_logger import MeldPrint


class StatisticsCollector:
    @staticmethod
    def collect_stat_for_enemy_riichi_hand_cost(tile_136, enemy, main_player):
        tile_34 = tile_136 // 4

        riichi_discard = [x for x in enemy.discards if x.riichi_discard]
        if riichi_discard:
            assert len(riichi_discard) == 1
            riichi_discard = riichi_discard[0]
        else:
            # FIXME: it happens when user called riichi and we are trying to decide to we need to open hand on
            # riichi tile or not. We need to process this situation correctly.
            riichi_discard = enemy.discards[-1]

        riichi_called_on_step = enemy.discards.index(riichi_discard) + 1

        total_dora_in_game = len(enemy.table.dora_indicators) * 4 + (3 * int(enemy.table.has_aka_dora))
        visible_tiles = enemy.table.revealed_tiles_136 + main_player.closed_hand
        visible_dora_tiles = sum(
            [plus_dora(x, enemy.table.dora_indicators, add_aka_dora=enemy.table.has_aka_dora) for x in visible_tiles]
        )
        live_dora_tiles = total_dora_in_game - visible_dora_tiles
        assert live_dora_tiles >= 0, "Live dora tiles can't be less than 0"

        number_of_kan_in_enemy_hand = 0
        number_of_dora_in_enemy_kan_sets = 0
        number_of_yakuhai_enemy_kan_sets = 0
        for meld in enemy.melds:
            # if he is in riichi he can only have closed kan
            assert meld.type == MeldPrint.KAN and not meld.opened

            number_of_kan_in_enemy_hand += 1

            for tile in meld.tiles:
                number_of_dora_in_enemy_kan_sets += plus_dora(
                    tile, enemy.table.dora_indicators, add_aka_dora=enemy.table.has_aka_dora
                )

            tile_meld_34 = meld.tiles[0] // 4
            if tile_meld_34 in enemy.valued_honors:
                number_of_yakuhai_enemy_kan_sets += 1

        number_of_other_player_kan_sets = 0
        for other_player in enemy.table.players:
            if other_player.seat == enemy.seat:
                continue

            for meld in other_player.melds:
                if meld.type == MeldPrint.KAN or meld.type == MeldPrint.SHOUMINKAN:
                    number_of_other_player_kan_sets += 1

        tile_category = ""
        # additional danger for tiles that could be used for tanyao
        if not is_honor(tile_34):
            # +1 here to make it more readable
            simplified_tile = simplify(tile_34) + 1

            if simplified_tile in [4, 5, 6]:
                tile_category = "middle"

            if simplified_tile in [2, 3, 7, 8]:
                tile_category = "edge"

            if simplified_tile in [1, 9]:
                tile_category = "terminal"
        else:
            tile_category = "honor"
            if tile_34 in enemy.valued_honors:
                tile_category = "valuable_honor"

        return {
            "is_dealer": enemy.is_dealer and 1 or 0,
            "riichi_called_on_step": riichi_called_on_step,
            "current_enemy_step": len(enemy.discards),
            "wind_number": main_player.table.round_wind_number,
            "scores": enemy.scores,
            "is_tsumogiri_riichi": riichi_discard.is_tsumogiri and 1 or 0,
            "is_oikake_riichi": enemy.is_oikake_riichi and 1 or 0,
            "is_oikake_riichi_against_dealer_riichi_threat": enemy.is_oikake_riichi_against_dealer_riichi_threat
            and 1
            or 0,
            "is_riichi_against_open_hand_threat": enemy.is_riichi_against_open_hand_threat and 1 or 0,
            "number_of_kan_in_enemy_hand": number_of_kan_in_enemy_hand,
            "number_of_dora_in_enemy_kan_sets": number_of_dora_in_enemy_kan_sets,
            "number_of_yakuhai_enemy_kan_sets": number_of_yakuhai_enemy_kan_sets,
            "number_of_other_player_kan_sets": number_of_other_player_kan_sets,
            "live_dora_tiles": live_dora_tiles,
            "tile_plus_dora": plus_dora(tile_136, enemy.table.dora_indicators, add_aka_dora=enemy.table.has_aka_dora),
            "tile_category": tile_category,
            "discards_before_riichi_34": ";".join([str(x.value // 4) for x in enemy.discards[:riichi_called_on_step]]),
        }

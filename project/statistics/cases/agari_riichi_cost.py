from statistics.cases.main import MainCase


class AgariRiichiCostCase(MainCase):
    CSV_HEADER = [
        "is_dealer",
        "riichi_called_on_step",
        "current_enemy_step",
        "wind_number",
        "scores",
        "is_tsumogiri_riichi",
        "is_oikake_riichi",
        "is_oikake_riichi_against_dealer_riichi_threat",
        "is_riichi_against_open_hand_threat",
        "number_of_kan_in_enemy_hand",
        "number_of_dora_in_enemy_kan_sets",
        "number_of_yakuhai_enemy_kan_sets",
        "number_of_other_player_kan_sets",
        "live_dora_tiles",
        "tile_plus_dora",
        "tile_category",
        "discards_before_riichi_34",
        "predicted_cost",
        "lobby",
        "log_id",
        "win_tile_34",
        "original_cost",
    ]

    def _filter_rounds(self, log_id, parsed_rounds):
        """
        Find rounds where was agari riichi without tsumo and without ippatsu.
        """
        results = []
        lobby = None
        for round_data in parsed_rounds:
            for tag in round_data:
                if self.parser.is_start_game_tag(tag):
                    lobby = self.parser.parse_lobby(tag)
                    # we don't want to get stat from ippan for now
                    if lobby == "ippan":
                        return []

                # in old logs riichi was called without step attribute
                # which makes it is hard to parse
                # so let's just skip these logs for now
                if self.parser.is_riichi_tag(tag) and "step" not in tag:
                    return []

                if not self.parser.is_agari_tag(tag):
                    continue

                if "yaku=" not in tag:
                    continue

                yaku_list = [int(x) for x in self.parser.get_attribute_content(tag, "yaku").split(",")[::2]]

                # we are looking for riichi hands only
                if 1 not in yaku_list:
                    continue

                # we don't want to check hand cost for ippatsu or tsumo situations
                if 2 in yaku_list or 0 in yaku_list:
                    continue

                original_cost = int(self.parser.get_attribute_content(tag, "ten").split(",")[1])
                results.append(
                    {
                        "lobby": lobby,
                        "log_id": log_id,
                        "agari_position": int(self.parser.get_attribute_content(tag, "who")),
                        "player_position": int(self.parser.get_attribute_content(tag, "fromWho")),
                        "win_tile_34": int(self.parser.get_attribute_content(tag, "machi")) // 4,
                        "original_cost": original_cost,
                        "round_data": round_data,
                    }
                )

        return results

    def _collect_statistics(self, filtered_result):
        """
        Statistics that we want to collect:
        - On Riichi. Round step number when riichi was called
        - On Riichi. Wind number
        - On Riichi. Enemy scores
        - On Riichi. Was it tsumogiri riichi or not
        - On Riichi. Was it dealer riichi or not
        - On Riichi. Was it first riichi or not
        - On Riichi. Was it called against dealer riichi threat or not
        - On Riichi. Was it called against open hand threat or not (threat == someone opened dora pon)
        - On Riichi. Discards before the riichi
        - On Agari. Riichi hand cost
        - On Agari. Round step number
        - On Agari. Number of kan sets in riichi hand
        - On Agari. Number of kan sets on the table
        - On Agari. Number of live dora
        - On Agari. Win tile (34 format)
        - On Agari. Win tile category (terminal, edge 2378, middle 456, honor, valuable honor)
        - On Agari. Is win tile dora or not
        """
        agari_seat = self.reproducer._normalize_position(
            filtered_result["agari_position"], filtered_result["player_position"]
        )

        stat = self.reproducer.play_round(
            filtered_result["round_data"],
            filtered_result["player_position"],
            context={
                "action": "agari_riichi_cost",
                "agari_seat": agari_seat,
            },
        )

        if not stat:
            return None

        del filtered_result["round_data"]
        del filtered_result["player_position"]
        del filtered_result["agari_position"]

        stat.update(filtered_result)

        return stat

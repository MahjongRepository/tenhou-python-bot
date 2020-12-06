from statistics.cases.main import MainCase

from game.ai.defence.enemy_analyzer import EnemyAnalyzer


class AgariRiichiCostCase(MainCase):
    def _filter_rounds(self, log_id, parsed_rounds):
        """
        Find rounds where was agari riichi without tsumo and without ippatsu.
        """
        results = []
        for round_data in parsed_rounds:
            for tag in round_data:
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
                        "log_id": log_id,
                        "agari_position": int(self.parser.get_attribute_content(tag, "who")),
                        "player_position": int(self.parser.get_attribute_content(tag, "fromWho")),
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
        - On Riichi. Was it called against open hand threat or not (threat == someone opened dora pon)
        - On Agari. Riichi hand cost
        - On Agari. Round step number
        - On Agari. Number of kan sets in riichi hand
        - On Agari. Number of kan sets on the table
        - On Agari. Number of visible dora on the table
        - On Agari. Win tile (34 format)
        - On Agari. Win tile category (terminal, edge 2378, middle 456, honor, valuable honor)
        """
        self.reproducer.play_round(
            filtered_result["round_data"],
            filtered_result["player_position"],
            needed_tile=None,
            action="end",
            tile_number_to_stop=None,
        )

        agari_position = self.reproducer._normalize_position(
            filtered_result["agari_position"], filtered_result["player_position"]
        )

        del filtered_result["round_data"]
        del filtered_result["player_position"]
        del filtered_result["agari_position"]

        stat = self.reproducer.table.player.stat_collection["riichi_hand_cost"][agari_position]
        stat.update(filtered_result)
        stat["rounded_original_cost"] = self._round_riichi_cost(stat["original_cost"], stat["is_dealer"])
        return stat

    def _round_riichi_cost(self, original_cost, is_dealer):
        if is_dealer:
            scale = EnemyAnalyzer.RIICHI_DEALER_COST_SCALE
        else:
            scale = EnemyAnalyzer.RIICHI_COST_SCALE
        return min(scale, key=lambda x: abs(x - original_cost))

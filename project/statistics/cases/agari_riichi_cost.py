from statistics.cases.main import MainCase


class AgariRiichiCostCase(MainCase):
    def _filter_rounds(self, parsed_rounds):
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

                results.append(round_data)

        return results

    def _collect_statistics(self, round_data):
        """
        Statistics that we want to collect:
        - On Riichi. Round step number when riichi was called
        - On Riichi. Was it tsumogiri riichi or not
        - On Riichi. Was it dealer riichi or not
        - On Riichi. Was it first riichi or not
        - On Riichi. Was it called against open hand threat or not (threat == someone opened dora pon)
        - On Agari. Riichi hand cost
        - On Agari. Number of kan sets in riichi hand
        - On Agari. Number of kan sets on the table
        - On Agari. Number of visible dora on the table
        - On Agari. Win tile (34 format)
        - On Agari. Win tile category (terminal, middle 2-8, honor, valuable honor)
        """
        return {}

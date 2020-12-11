import re
from typing import List


class LogParser:
    def split_log_to_game_rounds(self, log_content: str) -> List[List[str]]:
        """
        XML parser was really slow here,
        so I built simple parser to separate log content on tags (grouped by rounds)
        """
        tag_start = 0
        rounds = []
        tag = None

        current_round_tags = []
        for x in range(0, len(log_content)):
            if log_content[x] == ">":
                tag = log_content[tag_start : x + 1]
                tag_start = x + 1

            # not useful tags
            skip_tags = ["SHUFFLE", "TAIKYOKU", "mjloggm"]
            if tag and any([x in tag for x in skip_tags]):
                tag = None

            # new hand was started
            if self.is_init_tag(tag) and current_round_tags:
                rounds.append(current_round_tags)
                current_round_tags = []

            # the end of the game
            if tag and "owari" in tag:
                rounds.append(current_round_tags)

            if tag:
                if self.is_init_tag(tag):
                    # we dont need seed information
                    # it appears in old logs format
                    find = re.compile(r'shuffle="[^"]*"')
                    tag = find.sub("", tag)

                # add processed tag to the round
                current_round_tags.append(tag)
                tag = None

        return rounds

    def get_attribute_content(self, tag: str, attribute_name: str):
        result = re.findall(r'{}="([^"]*)"'.format(attribute_name), tag)
        return result and result[0] or None

    def comma_separated_string_to_ints(self, string: str):
        return [int(x) for x in string.split(",")]

    def is_init_tag(self, tag):
        return tag and "INIT" in tag

    def is_agari_tag(self, tag):
        return tag and "AGARI" in tag

    def is_start_game_tag(self, tag):
        return tag and "<GO" in tag

    def is_riichi_tag(self, tag):
        return tag and "<REACH" in tag

    def parse_lobby(self, tag):
        game_rule_temp = int(self.get_attribute_content(tag, "type"))
        rule = bin(game_rule_temp).replace("0b", "")
        rule = rule.zfill(8)
        result = None
        if rule[0] == "0" and rule[2] == "0":
            result = "ippan"
        if rule[0] == "1" and rule[2] == "0":
            result = "joukyuu"
        if rule[0] == "0" and rule[2] == "1":
            result = "tokujou"
        if rule[0] == "1" and rule[2] == "1":
            result = "houhou"
        return result

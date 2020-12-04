from statistics.db import load_logs_from_db
from statistics.log_parser import LogParser

from tqdm import tqdm


class Statistics:
    def __init__(self, db_path: str, limit: int, offset: int):
        self.db_path = db_path
        self.limit = limit
        self.offset = offset
        self.parser = LogParser()

    def calculate_statistics(self):
        logs = load_logs_from_db(self.db_path, offset=self.offset, limit=self.limit)
        progress_bar = tqdm(logs, position=1)
        for log in progress_bar:
            parsed_rounds = self.parser.split_log_to_game_rounds(log["log_content"])
            self.find_riichi_hands(parsed_rounds)

    def find_riichi_hands(self, parsed_rounds):
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

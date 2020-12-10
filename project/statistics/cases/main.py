import csv
import logging
import os
from pathlib import Path
from statistics.db import get_total_logs_count, load_logs_from_db
from statistics.log_parser import LogParser

from reproducer import TenhouLogReproducer
from tqdm import tqdm

logger = logging.getLogger("stat")


class MainCase:
    def __init__(self, db_path: str, stats_output_folder: str):
        self.db_path = db_path
        self.stats_output_folder = stats_output_folder

        self.parser = LogParser()
        self.reproducer = TenhouLogReproducer(None, None, logging.getLogger())

    def prepare_statistics(self):
        limit = 10000
        total_logs_count = get_total_logs_count(self.db_path)
        total_steps = int(total_logs_count / limit) + 1

        progress_bar = tqdm(range(total_steps), position=2)
        for step in progress_bar:
            offset = step * limit
            progress_bar.set_description(f"{offset} - {offset + limit}")

            logs = load_logs_from_db(self.db_path, offset=offset, limit=limit)

            results = []
            for log in tqdm(logs, position=1):
                parsed_rounds = self.parser.split_log_to_game_rounds(log["log_content"])
                results.extend(self._filter_rounds(log["log_id"], parsed_rounds))

            collected_statistics = []
            for filtered_result in tqdm(results, position=0):
                try:
                    result = self._collect_statistics(filtered_result)
                    if result:
                        collected_statistics.append(result)
                except Exception:
                    logger.error(f"Error in statistics calculation for {filtered_result['log_id']}")

            csv_file_name = f"{Path(self.db_path).name}_{offset}_{offset + limit}.csv"
            regular_csv_file_path = os.path.join(self.stats_output_folder, csv_file_name)
            dealer_csv_file_path = os.path.join(self.stats_output_folder, f"dealer_{csv_file_name}")

            with open(regular_csv_file_path, "w") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=collected_statistics[0].keys())
                writer.writeheader()
                for data in collected_statistics:
                    if data["is_dealer"]:
                        continue
                    writer.writerow(data)

            with open(dealer_csv_file_path, "w") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=collected_statistics[0].keys())
                writer.writeheader()
                for data in collected_statistics:
                    if not data["is_dealer"]:
                        continue
                    writer.writerow(data)

    def _filter_rounds(self, log_id, parsed_rounds):
        return []

    def _collect_statistics(self, filtered_result):
        return {}

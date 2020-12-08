import csv
import logging
import os
from pathlib import Path
from statistics.db import load_logs_from_db
from statistics.log_parser import LogParser

from reproducer import TenhouLogReproducer
from tqdm import tqdm

logger = logging.getLogger("stat")


class MainCase:
    def __init__(self, db_path: str, stats_output_folder: str, limit: int, offset: int):
        self.db_path = db_path
        self.limit = limit
        self.offset = offset

        self.csv_file_name = f"{Path(db_path).name}_{offset}_{offset + limit}.csv"
        self.regular_csv_file_path = os.path.join(stats_output_folder, self.csv_file_name)
        self.dealer_csv_file_path = os.path.join(stats_output_folder, f"dealer_{self.csv_file_name}")

        self.parser = LogParser()
        self.reproducer = TenhouLogReproducer(None, None, logging.getLogger())

    def prepare_statistics(self):
        logger.info("Loading data from DB...")
        logs = load_logs_from_db(self.db_path, offset=self.offset, limit=self.limit)

        logger.info("Parsing logs...")
        results = []
        for log in tqdm(logs):
            parsed_rounds = self.parser.split_log_to_game_rounds(log["log_content"])
            results.extend(self._filter_rounds(log["log_id"], parsed_rounds))

        logger.info(f"Found {len(results)} rounds.")
        logger.info("Collecting statistics...")

        collected_statistics = []
        for filtered_result in tqdm(results):
            try:
                collected_statistics.append(self._collect_statistics(filtered_result))
            except Exception:
                logger.error(f"Error in statistics calculation for {filtered_result['log_id']}")

        logger.info("Saving regular player statistics...")
        with open(self.regular_csv_file_path, "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=collected_statistics[0].keys())
            writer.writeheader()
            for data in collected_statistics:
                if data["is_dealer"]:
                    continue
                writer.writerow(data)

        logger.info("Saving dealer statistics...")
        with open(self.dealer_csv_file_path, "w") as csv_file:
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

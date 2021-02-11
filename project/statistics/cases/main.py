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
    def __init__(self, db_path: str, stats_output_folder: str):
        self.db_path = db_path
        self.stats_output_folder = stats_output_folder

        self.parser = LogParser()
        self.reproducer = TenhouLogReproducer(None, None, logging.getLogger())

    def prepare_statistics(self):
        logger.info("Loading all logs from DB and unarchiving them...")

        limit = 10000000000000
        logs = load_logs_from_db(self.db_path, limit, offset=0)
        logger.info(f"Loaded {len(logs)} logs")

        results = []
        for log in tqdm(logs, position=1, desc="Parsing xml to tag arrays..."):
            parsed_rounds = self.parser.split_log_to_game_rounds(log["log_content"])
            results.extend(self._filter_rounds(log["log_id"], parsed_rounds))

        collected_statistics = []
        for filtered_result in tqdm(results, position=0, desc="Processing tag arrays..."):
            try:
                result = self._collect_statistics(filtered_result)
                if result:
                    collected_statistics.append(result)
            except Exception:
                logger.error(f"Error in statistics calculation for {filtered_result['log_id']}")

        csv_file_name = f"{Path(self.db_path).name}.csv"
        data_csv = os.path.join(self.stats_output_folder, csv_file_name)

        if collected_statistics:
            with open(data_csv, "w") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=collected_statistics[0].keys())
                writer.writeheader()
                for data in collected_statistics:
                    writer.writerow(data)

    def _filter_rounds(self, log_id, parsed_rounds):
        return []

    def _collect_statistics(self, filtered_result):
        return {}

import logging
from statistics.db import load_logs_from_db
from statistics.log_parser import LogParser

from reproducer import TenhouLogReproducer
from tqdm import tqdm

logger = logging.getLogger("stat")


class MainCase:
    def __init__(self, db_path: str, limit: int, offset: int):
        self.db_path = db_path
        self.limit = limit
        self.offset = offset

        self.parser = LogParser()
        self.reproducer = TenhouLogReproducer(None, None, logging.getLogger())

    def prepare_statistics(self):
        logger.info("Loading data from DB...")
        logs = load_logs_from_db(self.db_path, offset=self.offset, limit=self.limit)

        logger.info("Parsing logs...")
        results = []
        for log in tqdm(logs, position=1):
            parsed_rounds = self.parser.split_log_to_game_rounds(log["log_content"])
            results.extend(self._filter_rounds(log["log_id"], parsed_rounds))

        logger.info(f"Found {len(results)} rounds.")
        logger.info("Collecting statistics...")

        collected_statistics = []
        for filtered_result in tqdm(results, position=1):
            collected_statistics.append(self._collect_statistics(filtered_result))

        logger.info("Saving statistics...")

    def _filter_rounds(self, log_id, parsed_rounds):
        return []

    def _collect_statistics(self, filtered_result):
        return {}

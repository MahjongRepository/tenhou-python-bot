import logging
import os
from optparse import OptionParser
from statistics.cases.agari_riichi_cost import AgariRiichiCostCase

from utils.logger import DATE_FORMAT, LOG_FORMAT

stats_output_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "statistics", "output")
if not os.path.exists(stats_output_folder):
    os.mkdir(stats_output_folder)


def main():
    _set_up_bots_battle_game_logger()

    parser = OptionParser()
    parser.add_option("-p", "--db_path", type="string", help="Path to sqlite database with logs")
    parser.add_option("-l", "--limit", type="int")
    parser.add_option("-o", "--offset", type="int")
    opts, _ = parser.parse_args()

    case = AgariRiichiCostCase(opts.db_path, stats_output_folder, opts.limit, opts.offset)

    case.prepare_statistics()


def _set_up_bots_battle_game_logger():
    logger = logging.getLogger("stat")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    ch.setFormatter(formatter)

    logger.addHandler(ch)


if __name__ == "__main__":
    main()

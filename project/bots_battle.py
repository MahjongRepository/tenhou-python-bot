import datetime
import itertools
import logging
import os
import random
from optparse import OptionParser

import game.bots_battle
from game.bots_battle.battle_config import BattleConfig
from game.bots_battle.game_manager import GameManager
from game.bots_battle.local_client import LocalClient
from tqdm import trange
from utils.logger import DATE_FORMAT, LOG_FORMAT
from utils.settings_handler import settings

logger = logging.getLogger("game")

battle_results_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "battle_results")
if not os.path.exists(battle_results_folder):
    os.mkdir(battle_results_folder)


def main(number_of_games, print_logs):
    seeds = []
    seed_file = "seeds.txt"
    if os.path.exists(seed_file):
        with open(seed_file, "r") as f:
            seeds = f.read().split("\n")
            seeds = [int(x.strip()) for x in seeds if x.strip()]

    replays_directory = os.path.join(battle_results_folder, "replays")
    if not os.path.exists(replays_directory):
        os.mkdir(replays_directory)

    possible_configurations = list(itertools.combinations(BattleConfig.CLIENTS_CONFIGS, 4))
    assert len(BattleConfig.CLIENTS_CONFIGS) == 12
    assert len(possible_configurations) == 495

    chosen_configuration = 0
    for i in trange(number_of_games):
        if i < len(seeds):
            seed_value = seeds[i]
        else:
            seed_value = random.getrandbits(64)

        replay_name = GameManager.generate_replay_name()

        clients = [
            LocalClient(possible_configurations[chosen_configuration][x](), print_logs, replay_name, i)
            for x in range(0, 4)
        ]
        manager = GameManager(clients, replays_directory, replay_name)

        try:
            game.bots_battle.game_manager.shuffle_seed = lambda: seed_value
            manager.play_game()
        except Exception as e:
            manager.replay.save_failed_log()
            logger.error(f"Hanchan seed={seed_value} crashed", exc_info=e)

        chosen_configuration += 1
        if chosen_configuration == len(possible_configurations):
            chosen_configuration = 0


def _set_up_bots_battle_game_logger():
    logs_directory = os.path.join(battle_results_folder, "logs")
    if not os.path.exists(logs_directory):
        os.mkdir(logs_directory)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_name = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}.log"
    fh = logging.FileHandler(os.path.join(logs_directory, file_name), encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    logger = logging.getLogger("game")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)


if __name__ == "__main__":
    _set_up_bots_battle_game_logger()

    parser = OptionParser()
    parser.add_option(
        "-g",
        "--games",
        type="int",
        default=1,
        help="Number of games to play",
    )
    parser.add_option(
        "--logs",
        action="store_true",
        help="Enable logs for bots, use it only for debug, not for live games",
    )
    opts, _ = parser.parse_args()

    settings.FIVE_REDS = True
    settings.OPEN_TANYAO = True
    settings.PRINT_LOGS = False

    if opts.logs:
        settings.PRINT_LOGS = True

    main(opts.games, opts.logs)

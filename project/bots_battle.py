import datetime
import logging
import os
from optparse import OptionParser
from random import random

import game.bots_battle
from game.bots_battle.battle_config import BattleConfig
from game.bots_battle.game_manager import GameManager
from game.bots_battle.local_client import LocalClient
from tqdm import trange
from utils.logger import DATE_FORMAT, LOG_FORMAT

logger = logging.getLogger("game")

battle_results_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "battle_results")
if not os.path.exists(battle_results_folder):
    os.mkdir(battle_results_folder)


def main(number_of_games):
    seeds = []
    seed_file = "seeds.txt"
    if os.path.exists(seed_file):
        with open(seed_file, "r") as f:
            seeds = f.read().split("\n")
            seeds = [float(x.strip()) for x in seeds if x.strip()]

    replays_directory = os.path.join(battle_results_folder, "replays")
    if not os.path.exists(replays_directory):
        os.mkdir(replays_directory)

    clients = [LocalClient(BattleConfig.CLIENTS_CONFIGS[x]()) for x in range(0, 4)]
    manager = GameManager(clients, replays_directory)

    total_results = {}
    for client in clients:
        total_results[client.id] = {
            "name": client.player.name,
            "positions": [],
            "played_rounds": 0,
            "lose_rounds": 0,
            "win_rounds": 0,
            "riichi_rounds": 0,
            "called_rounds": 0,
            "average_place": 0,
            "win_rate": 0,
            "riichi_rate": 0,
            "call_rate": 0,
            "feed_rate": 0,
        }

    for i in trange(number_of_games):
        if i < len(seeds):
            seed_value = seeds[i]
        else:
            seed_value = random()

        try:
            game.bots_battle.game_manager.shuffle_seed = lambda: seed_value

            result = manager.play_game(total_results)

            clients = sorted(clients, key=lambda i: i.player.scores, reverse=True)
            for client in clients:
                player = client.player

                total_result_client = total_results[client.id]
                total_result_client["positions"].append(player.position)
                total_result_client["played_rounds"] += result["played_rounds"]
        except Exception as e:
            logger.error(f"Hanchan seed={seed_value} crashed", exc_info=e)

    # recalculate stat values
    for item in total_results.values():
        if not item["positions"]:
            continue

        played_rounds = item["played_rounds"]
        lose_rounds = item["lose_rounds"]
        win_rounds = item["win_rounds"]
        riichi_rounds = item["riichi_rounds"]
        called_rounds = item["called_rounds"]

        item["average_place"] = sum(item["positions"]) / len(item["positions"])
        item["feed_rate"] = (lose_rounds / played_rounds) * 100
        item["win_rate"] = (win_rounds / played_rounds) * 100
        item["riichi_rate"] = (riichi_rounds / played_rounds) * 100
        item["call_rate"] = (called_rounds / played_rounds) * 100

    calculated_clients = sorted(total_results.values(), key=lambda i: i["average_place"])

    logger.info("Final results:")
    for item in calculated_clients:
        results = [
            f"{item['name']:8}",
            f"{item['average_place']:6.2f}",
            "win",
            f"{item['win_rate']:6.2f}%",
            "feed",
            f"{item['feed_rate']:6.2f}%",
            "riichi",
            f"{item['riichi_rate']:6.2f}%",
            "call",
            f"{item['call_rate']:6.2f}%",
        ]
        logger.info(" ".join(results))


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
    opts, _ = parser.parse_args()

    main(opts.games)

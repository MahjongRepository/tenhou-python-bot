import logging
from optparse import OptionParser
from random import random

import game.bots_battle
from game.bots_battle.battle_config import BattleConfig
from game.bots_battle.game_manager import GameManager
from game.bots_battle.local_client import LocalClient
from terminaltables import AsciiTable
from tqdm import trange
from utils.logger import DATE_FORMAT, LOG_FORMAT

logger = logging.getLogger("game")


def main(number_of_games):
    clients = [LocalClient(BattleConfig.CLIENTS_CONFIGS[x]()) for x in range(0, 4)]
    manager = GameManager(clients)

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
        }

    for i in trange(number_of_games):
        try:
            logger.info(f"Hanchan #{i + 1}")

            if i < len(BattleConfig.SEEDS):
                seed_value = BattleConfig.SEEDS[i]
            else:
                seed_value = random()

            game.bots_battle.game_manager.shuffle_seed = lambda: seed_value

            result = manager.play_game(total_results)

            table_data = [
                ["Position", "Player", "Scores"],
            ]

            clients = sorted(clients, key=lambda i: i.player.scores, reverse=True)
            for client in clients:
                player = client.player
                table_data.append([player.position, player.name, "{0:,d}".format(int(player.scores))])

                total_result_client = total_results[client.id]
                total_result_client["positions"].append(player.position)
                total_result_client["played_rounds"] += result["played_rounds"]

            table = AsciiTable(table_data)
            print(table.table)
        except Exception as e:
            logger.error(f"Hanchan #{i + 1} crashed.", exc_info=e)

    table_data = [
        ["Player", "Average place", "Win rate", "Feed rate", "Riichi rate", "Call rate"],
    ]

    # recalculate stat values
    for item in total_results.values():
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

    for item in calculated_clients:
        table_data.append(
            [
                item["name"],
                format(item["average_place"], ".2f"),
                format(item["win_rate"], ".2f") + "%",
                format(item["feed_rate"], ".2f") + "%",
                format(item["riichi_rate"], ".2f") + "%",
                format(item["call_rate"], ".2f") + "%",
            ]
        )

    table = AsciiTable(table_data)
    print(table.table)


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        "-g",
        "--games",
        type="int",
        default=1,
        help="Number of games to play",
    )
    opts, _ = parser.parse_args()

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger = logging.getLogger("game")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    main(opts.games)

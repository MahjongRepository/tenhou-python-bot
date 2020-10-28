import logging
from random import random

import game.bots_battle
from game.bots_battle.game_manager import GameManager
from game.bots_battle.local_client import LocalClient
from terminaltables import AsciiTable
from tqdm import trange
from utils.logger import DATE_FORMAT, LOG_FORMAT

TOTAL_GAMES = 1

logger = logging.getLogger("game")


def main():
    # initial seed
    random_value = random()
    game.bots_battle.game_manager.shuffle_seed = lambda: random_value

    clients = [LocalClient() for _ in range(0, 4)]
    manager = GameManager(clients)

    total_results = {}
    for client in clients:
        total_results[client.id] = {
            "name": client.player.name,
            "version": "v{}".format(client.player.ai.version),
            "positions": [],
            "played_rounds": 0,
            "lose_rounds": 0,
            "win_rounds": 0,
            "riichi_rounds": 0,
            "called_rounds": 0,
        }

    for x in trange(TOTAL_GAMES):
        logger.info("Hanchan #{0}".format(x + 1))

        result = manager.play_game(total_results)

        table_data = [
            ["Position", "Player", "AI", "Scores"],
        ]

        clients = sorted(clients, key=lambda i: i.player.scores, reverse=True)
        for client in clients:
            player = client.player
            table_data.append(
                [player.position, player.name, "v{0}".format(player.ai.version), "{0:,d}".format(int(player.scores))]
            )

            total_result_client = total_results[client.id]
            total_result_client["positions"].append(player.position)
            total_result_client["played_rounds"] += result["played_rounds"]

        table = AsciiTable(table_data)
        print(table.table)

        # rebuild seed value
        random_value = random()
        game.bots_battle.game_manager.shuffle_seed = lambda: random_value

    table_data = [
        ["Player", "AI", "Average place", "Win rate", "Feed rate", "Riichi rate", "Call rate"],
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
                item["version"],
                format(item["average_place"], ".2f"),
                format(item["win_rate"], ".2f") + "%",
                format(item["feed_rate"], ".2f") + "%",
                format(item["riichi_rate"], ".2f") + "%",
                format(item["call_rate"], ".2f") + "%",
            ]
        )

    logger.info(f"Final results: {table_data}")
    table = AsciiTable(table_data)
    print(table.table)


if __name__ == "__main__":
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
    logger = logging.getLogger("game")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    main()

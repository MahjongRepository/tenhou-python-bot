# -*- coding: utf-8 -*-
"""
Script to run local bots battle
"""
from random import random

from terminaltables import AsciiTable
from tqdm import trange

import game.game_manager
from game.game_manager import GameManager
from mahjong.client import Client

TOTAL_HANCHANS = 100


def main():
    # let's load three bots with old logic
    # and one copy with new logic
    clients = [Client(use_previous_ai_version=True) for _ in range(0, 3)]
    clients += [Client(use_previous_ai_version=False)]
    # clients = [Client(use_previous_ai_version=False) for _ in range(0, 4)]
    manager = GameManager(clients)

    total_results = {}
    for client in clients:
        total_results[client.id] = {
            'name': client.player.name,
            'version': 'v{}'.format(client.player.ai.version),
            'positions': [],
            'played_rounds': 0,
            'lose_rounds': 0,
            'win_rounds': 0,
            'riichi_rounds': 0,
            'called_rounds': 0,
        }

    for x in trange(TOTAL_HANCHANS):
        game.game_manager.shuffle_seed = lambda: random()
        # yes, I know about tqdm.write
        # but it didn't work properly for our case
        print('\n')
        print('Hanchan #{0}'.format(x + 1))

        result = manager.play_game(total_results)

        table_data = [
            ['Position', 'Player', 'AI', 'Scores'],
        ]

        clients = sorted(clients, key=lambda i: i.player.scores, reverse=True)
        for client in clients:
            player = client.player
            table_data.append([
                player.position,
                player.name,
                'v{0}'.format(player.ai.version),
                '{0:,d}'.format(int(player.scores))
            ])

            total_result_client = total_results[client.id]
            total_result_client['positions'].append(player.position)
            total_result_client['played_rounds'] += result['played_rounds']

        table = AsciiTable(table_data)
        print(table.table)
        print('')

    print('\n')

    table_data = [
        ['Player', 'AI', 'Average place', 'Win rate', 'Feed rate', 'Riichi rate', 'Call rate'],
    ]

    # recalculate stat values
    for item in total_results.values():
        played_rounds = item['played_rounds']
        lose_rounds = item['lose_rounds']
        win_rounds = item['win_rounds']
        riichi_rounds = item['riichi_rounds']
        called_rounds = item['called_rounds']

        item['average_place'] = sum(item['positions']) / len(item['positions'])
        item['feed_rate'] = (lose_rounds / played_rounds) * 100
        item['win_rate'] = (win_rounds / played_rounds) * 100
        item['riichi_rate'] = (riichi_rounds / played_rounds) * 100
        item['call_rate'] = (called_rounds / played_rounds) * 100

    calculated_clients = sorted(total_results.values(), key=lambda i: i['average_place'])

    for item in calculated_clients:
        table_data.append([
            item['name'],
            item['version'],
            format(item['average_place'], '.2f'),
            format(item['win_rate'], '.2f') + '%',
            format(item['feed_rate'], '.2f') + '%',
            format(item['riichi_rate'], '.2f') + '%',
            format(item['call_rate'], '.2f') + '%',
        ])

    print('Final results:')
    table = AsciiTable(table_data)
    print(table.table)


if __name__ == '__main__':
    main()

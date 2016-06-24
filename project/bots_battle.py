# -*- coding: utf-8 -*-
import logging
from time import sleep

from terminaltables import AsciiTable
from tqdm import trange

from game.game_manager import GameManager
from mahjong.client import Client

TOTAL_HANCHANS = 3

def main():
    # enable it for manual testing
    logger = logging.getLogger('game')
    logger.disabled = True

    clients = [Client() for _ in range(0, 4)]
    manager = GameManager(clients)

    total_results = {}
    x = 1
    for client in clients:
        total_results[client.id] = {
            'name': client.player.name,
            'version': client.player.ai.version,
            'positions': [1, x],
            'played_rounds': 0
        }
        x += 1

    for x in trange(TOTAL_HANCHANS):
        # yes, I know about tqdm.write
        # but it didn't work properly for our case
        print('\n')
        print('Hanchan #{0}'.format(x + 1))

        result = manager.play_game()
        sleep(2)

        table_data = [
            ['Position', 'Player', 'AI', 'Scores'],
        ]

        clients = sorted(clients, key=lambda i: i.player.scores, reverse=True)
        for client in clients:
            player = client.player
            table_data.append([player.position,
                               player.name,
                               'v{0}'.format(player.ai.version),
                               int(player.scores)])

            total_result_client = total_results[client.id]
            total_result_client['positions'].append(player.position)
            total_result_client['played_rounds'] = result['played_rounds']

        table = AsciiTable(table_data)
        print(table.table)
        print('')

    print('\n')

    table_data = [
        ['Player', 'AI', 'Played rounds', 'Average place'],
    ]

    # recalculate stat values
    for item in total_results.values():
        played_rounds = item['played_rounds']
        item['average_place'] = sum(item['positions']) / len(item['positions'])

    calculated_clients = sorted(total_results.values(), key=lambda i: i['average_place'])

    for item in calculated_clients:
        table_data.append([
            item['name'],
            item['version'],
            item['played_rounds'],
            item['average_place']
        ])

    print('Final results:')
    table = AsciiTable(table_data)
    print(table.table)


if __name__ == '__main__':
    main()

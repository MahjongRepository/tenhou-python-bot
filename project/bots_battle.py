# -*- coding: utf-8 -*-
import logging

from game.game_manager import GameManager
from mahjong.client import Client


def main():
    # enable it for manual testing
    logger = logging.getLogger('game')
    logger.disabled = True

    clients = [Client() for _ in range(0, 4)]
    manager = GameManager(clients)

    for x in range(1, 3):
        print('Hanchan #{0}'.format(x))
        manager.play_game()
        players = manager.players_sorted_by_scores()
        for player in players:
            print(player)
        print('')


if __name__ == '__main__':
    main()

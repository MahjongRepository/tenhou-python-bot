# -*- coding: utf-8 -*-
import os

replays_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data')
if not os.path.exists(replays_directory):
    os.mkdir(replays_directory)


class Replay(object):
    replays_directory = ''
    replay_name = ''
    tags = []
    clients = []

    def __init__(self, clients):
        self.replays_directory = replays_directory
        self.clients = clients

    def init_game(self, seed):
        raise NotImplemented()

    def end_game(self):
        raise NotImplemented()

    def init_round(self, dealer, round_number, honba_sticks, riichi_sticks, dora):
        raise NotImplemented()

    def draw(self, who, tile):
        raise NotImplemented()

    def discard(self, who, tile):
        raise NotImplemented()

    def riichi(self, who, step):
        raise NotImplemented()

    def open_meld(self, meld):
        raise NotImplemented()

    def retake(self, tempai_players, honba_sticks, riichi_sticks):
        raise NotImplemented()

    def win(self, who, from_who, win_tile, honba_sticks, riichi_sticks, han, fu, cost, yaku_list, dora, ura_dora):
        raise NotImplemented()

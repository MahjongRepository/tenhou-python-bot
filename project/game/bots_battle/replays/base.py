# -*- coding: utf-8 -*-
import os

replays_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "data")
if not os.path.exists(replays_directory):
    os.mkdir(replays_directory)


class Replay(object):
    replays_directory = ""
    replay_name = ""
    tags = []
    clients = []

    def __init__(self, replay_name, clients):
        self.replays_directory = replays_directory
        self.replay_name = replay_name
        self.clients = clients

    def init_game(self, seed):
        raise NotImplementedError()

    def end_game(self):
        raise NotImplementedError()

    def init_round(self, dealer, round_number, honba_sticks, riichi_sticks, dora):
        raise NotImplementedError()

    def draw(self, who, tile):
        raise NotImplementedError()

    def discard(self, who, tile):
        raise NotImplementedError()

    def riichi(self, who, step):
        raise NotImplementedError()

    def open_meld(self, meld):
        raise NotImplementedError()

    def retake(self, tempai_players, honba_sticks, riichi_sticks):
        raise NotImplementedError()

    def win(self, who, from_who, win_tile, honba_sticks, riichi_sticks, han, fu, cost, yaku_list, dora, ura_dora):
        raise NotImplementedError()

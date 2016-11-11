# -*- coding: utf-8 -*-
import json

import os
import time

replays_directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
if not os.path.exists(replays_directory):
    os.mkdir(replays_directory)


class Replay(object):
    replay_name = ''
    tags = []

    def init_game(self):
        self.tags = []
        self.replay_name = '{}.json'.format(int(time.time()))

    def end_game(self, clients):
        self.tags.append({
            'tag': 'end',
            'scores': [x.player.scores for x in clients]
        })

        with open(os.path.join(replays_directory, self.replay_name), 'w') as f:
            f.write(json.dumps(self.tags))

    def init_round(self, clients, seed, dora_indicators, dealer):
        self.tags.append({
            'tag': 'init',
            'seed': seed,
            'dora': dora_indicators,
            'dealer': dealer,
            'players': [{
                            'seat': x.seat,
                            'name': x.player.name,
                            'scores': x.player.scores,
                            'tiles': x.player.tiles
                        } for x in clients]
        })

    def draw(self, who, tile):
        self.tags.append({
            'tag': 'draw',
            'who': who,
            'tile': tile
        })

    def discard(self, who, tile):
        self.tags.append({
            'tag': 'discard',
            'who': who,
            'tile': tile
        })

    def riichi(self, who, step):
        self.tags.append({
            'tag': 'riichi',
            'who': who,
            'step': step
        })

    def open_meld(self, who, meld_type, tiles):
        self.tags.append({
            'tag': 'meld',
            'who': who,
            'type': meld_type,
            'tiles': tiles
        })

    def retake(self, tempai_players):
        self.tags.append({
            'tag': 'retake',
            'tempai_players': tempai_players,
        })

    def win(self, who, from_who, han, fu, scores, yaku):
        self.tags.append({
            'tag': 'win',
            'who': who,
            'from_who': from_who,
            'han': han,
            'fu': fu,
            'scores': scores,
            'yaku': yaku,
        })

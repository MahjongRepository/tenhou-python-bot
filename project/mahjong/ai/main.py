# -*- coding: utf-8 -*-
import random

from mahjong.ai.agari import Agari
from mahjong.ai.base import BaseAI
from mahjong.ai.shanten import Shanten
from mahjong.tile import TilesConverter


class MainAI(BaseAI):
    version = '0.0.6'

    agari = None
    shanten = None
    defence = None

    def __init__(self, table, player):
        super(MainAI, self).__init__(table, player)

        self.agari = Agari()
        self.shanten = Shanten()
        self.defence = Defence(table)

    def discard_tile(self):
        results, shanten = self.calculate_outs()

        if shanten == 0:
            self.player.in_tempai = True

        # we are win!
        if shanten == Shanten.AGARI_STATE:
            return Shanten.AGARI_STATE

        # Disable defence for now
        # if self.defence.go_to_defence_mode():
        #     self.player.in_tempai = False
        #     tile_in_hand = self.defence.calculate_safe_tile_against_riichi()
        #     if we wasn't able to find a safe tile, let's discard a random one
        #     if not tile_in_hand:
        #         tile_in_hand = self.player.tiles[random.randrange(len(self.player.tiles) - 1)]
        # else:
        #     tile34 = results[0]['discard']
        #     tile_in_hand = TilesConverter.find_34_tile_in_136_array(tile34, self.player.tiles)

        tile34 = results[0]['discard']
        tile_in_hand = TilesConverter.find_34_tile_in_136_array(tile34, self.player.tiles)

        return tile_in_hand

    def calculate_outs(self):
        tiles = TilesConverter.to_34_array(self.player.tiles)

        shanten = self.shanten.calculate_shanten(tiles)
        # win
        if shanten == Shanten.AGARI_STATE:
            return [], shanten

        raw_data = {}
        for i in range(0, 34):
            if not tiles[i]:
                continue

            tiles[i] -= 1

            raw_data[i] = []
            for j in range(0, 34):
                if i == j or tiles[j] >= 4:
                    continue

                tiles[j] += 1
                if self.shanten.calculate_shanten(tiles) == shanten - 1:
                    raw_data[i].append(j)
                tiles[j] -= 1

            tiles[i] += 1

            if raw_data[i]:
                raw_data[i] = {'tile': i, 'tiles_count': self.count_tiles(raw_data[i], tiles), 'waiting': raw_data[i]}

        results = []
        tiles = TilesConverter.to_34_array(self.player.tiles)
        for tile in range(0, len(tiles)):
            if tile in raw_data and raw_data[tile] and raw_data[tile]['tiles_count']:
                item = raw_data[tile]

                waiting = []

                for item2 in item['waiting']:
                    waiting.append(item2)

                results.append({
                    'discard': item['tile'],
                    'waiting': waiting,
                    'tiles_count': item['tiles_count']
                })

        # if we have character and honor candidates to discard with same tiles count,
        # we need to discard honor tile first
        results = sorted(results, key=lambda x: (x['tiles_count'], x['discard']), reverse=True)

        return results, shanten

    def count_tiles(self, raw_data, tiles):
        n = 0
        for i in range(0, len(raw_data)):
            n += 4 - tiles[raw_data[i]]
        return n


class Defence(object):
    table = None

    def __init__(self, table):
        self.table = table

    def go_to_defence_mode(self):
        """
        The method is decides should main player go to the defence mode or not
        :return: true|false
        """
        main_player = self.table.get_main_player()
        result = False

        # if we are in riichi, we can't defence
        if main_player.in_riichi:
            return False

        for player in self.table.players:
            if player.seat == main_player.seat:
                continue

            if player.in_riichi:
                result = True

        return result

    def calculate_safe_tile_against_riichi(self):
        player_tiles = self.table.get_main_player().tiles
        # tiles that were discarded after riichi or
        # discarded by player in riichi
        # for better experience we need to detect the safe tiles for different players
        safe_tiles = []
        for player in self.table.players:
            safe_tiles += player.safe_tiles
            if player.in_riichi:
                safe_tiles += player.discards

        player_tiles_34 = TilesConverter.to_34_array(player_tiles)
        safe_tiles_34 = TilesConverter.to_34_array(safe_tiles)

        safe_tile = None
        # let's try to find a safe tile in our main player hand
        for i in range(0, len(safe_tiles_34)):
            if safe_tiles_34[i] > 0 and player_tiles_34[i] > 0:
                return TilesConverter.find_34_tile_in_136_array(i, player_tiles)

        return safe_tile


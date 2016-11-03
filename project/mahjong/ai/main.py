# -*- coding: utf-8 -*-
from mahjong.ai.agari import Agari
from mahjong.ai.base import BaseAI
from mahjong.ai.defence import Defence
from mahjong.ai.shanten import Shanten
from mahjong.constants import HAKU, CHUN, HATSU
from mahjong.hand import HandDivider
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_pin, is_honor, is_chi, is_pon, is_man


class MainAI(BaseAI):
    version = '0.1.0'

    agari = None
    shanten = None
    defence = None
    hand_divider = None
    previous_shanten = 7

    yakuhai_strategy = False

    def __init__(self, table, player):
        super(MainAI, self).__init__(table, player)

        self.agari = Agari()
        self.shanten = Shanten()
        self.defence = Defence(table)
        self.hand_divider = HandDivider()
        self.previous_shanten = 7
        self.yakuhai_strategy = False

    def erase_state(self):
        self.yakuhai_strategy = False

    def discard_tile(self):
        results, shanten = self.calculate_outs(self.player.tiles, self.player.closed_hand)
        self.previous_shanten = shanten

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

    def calculate_outs(self, tiles, closed_hand):
        """
        :param tiles: array of tiles in 136 format
        :param closed_hand: array of tiles in 136 format
        :return:
        """
        tiles_34 = TilesConverter.to_34_array(tiles)
        closed_tiles_34 = TilesConverter.to_34_array(closed_hand)
        shanten = self.shanten.calculate_shanten(tiles_34)

        # win
        if shanten == Shanten.AGARI_STATE:
            return [], shanten

        raw_data = {}
        for i in range(0, 34):
            if not tiles_34[i]:
                continue

            if not closed_tiles_34[i]:
                continue

            tiles_34[i] -= 1

            raw_data[i] = []
            for j in range(0, 34):
                if i == j or tiles_34[j] >= 4:
                    continue

                tiles_34[j] += 1
                if self.shanten.calculate_shanten(tiles_34) == shanten - 1:
                    raw_data[i].append(j)
                tiles_34[j] -= 1

            tiles_34[i] += 1

            if raw_data[i]:
                raw_data[i] = {
                    'tile': i,
                    'tiles_count': self.count_tiles(raw_data[i], tiles_34),
                    'waiting': raw_data[i]
                }

        results = []
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        for tile in range(0, len(tiles_34)):
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

    def try_to_call_meld(self, tile, enemy_seat):
        """
        Determine should we call a meld or not.
        If yes, it will add tile to the player's hand and will return Meld object
        :param tile: 136 format tile
        :param enemy_seat: 1, 2, 3
        :return: meld and tile to discard after called open set
        """
        closed_hand = self.player.closed_hand[:]

        # we opened all our hand
        if len(closed_hand) == 1:
            return None, None

        self.determine_open_hand_strategy()

        tiles_34 = TilesConverter.to_34_array(closed_hand)
        discarded_tile = tile // 4
        # previous player
        is_kamicha_discard = self.player.seat - 1 == enemy_seat or self.player.seat == 0 and enemy_seat == 3

        new_tiles = self.player.tiles[:] + [tile]
        outs_results, shanten = self.calculate_outs(new_tiles, closed_hand)

        if self.yakuhai_strategy:
            # pon of honor tiles
            if is_honor(discarded_tile) and tiles_34[discarded_tile] == 2:
                first_tile = TilesConverter.find_34_tile_in_136_array(discarded_tile, closed_hand)
                # we need to remove tile from array, to not find it again for second tile
                closed_hand.remove(first_tile)
                second_tile = TilesConverter.find_34_tile_in_136_array(discarded_tile, closed_hand)
                tiles = [
                    first_tile,
                    second_tile,
                    tile
                ]

                meld = Meld()
                meld.who = self.player.seat
                meld.from_who = enemy_seat
                meld.type = Meld.PON
                meld.tiles = tiles

                tile_34 = outs_results[0]['discard']
                tile_to_discard = TilesConverter.find_34_tile_in_136_array(tile_34, self.player.tiles)

                return meld, tile_to_discard

            # tile will decrease the count of shanten in hand
            # so let's call opened set with it
            if shanten < self.previous_shanten:
                closed_hand_34 = TilesConverter.to_34_array(closed_hand + [tile])

                if is_man(discarded_tile):
                    combinations = self.hand_divider.find_valid_combinations(closed_hand_34, 0, 8, True)
                elif is_pin(discarded_tile):
                    combinations = self.hand_divider.find_valid_combinations(closed_hand_34, 9, 17, True)
                else:
                    combinations = self.hand_divider.find_valid_combinations(closed_hand_34, 18, 26, True)

                if combinations:
                    combinations = combinations[0]

                possible_melds = []
                for combination in combinations:
                    # we can call pon from everyone
                    if is_pon(combination) and discarded_tile in combination:
                        if combination not in possible_melds:
                            possible_melds.append(combination)

                    # we can call chi only from left player
                    if is_chi(combination) and is_kamicha_discard and discarded_tile in combination:
                        if combination not in possible_melds:
                            possible_melds.append(combination)

                if len(possible_melds):
                    # TODO add logic to find best meld
                    combination = possible_melds[0]
                    meld_type = is_chi(combination) and Meld.CHI or Meld.PON

                    combination.remove(discarded_tile)
                    first_tile = TilesConverter.find_34_tile_in_136_array(combination[0], closed_hand)
                    # we need to remove tile from array, to not find it again for second tile
                    closed_hand.remove(first_tile)
                    second_tile = TilesConverter.find_34_tile_in_136_array(combination[1], closed_hand)
                    tiles = [
                        first_tile,
                        second_tile,
                        tile
                    ]

                    meld = Meld()
                    meld.who = self.player.seat
                    meld.from_who = enemy_seat
                    meld.type = meld_type
                    meld.tiles = sorted(tiles)

                    tile_34 = outs_results[0]['discard']
                    tile_to_discard = TilesConverter.find_34_tile_in_136_array(tile_34, self.player.tiles)

                    return meld, tile_to_discard

        return None, None

    def determine_open_hand_strategy(self):
        if self._switch_to_yakuhai_strategy():
            self.yakuhai_strategy = True

    def _switch_to_yakuhai_strategy(self):
        """
        Determine can we switch to yakuhai strategy or not
        We can do it if we have valued pair in hand
        :return: boolean
        """
        valued_tiles = [CHUN, HAKU, HATSU, self.player.table.round_wind, self.player.player_wind]
        tiles_34 = TilesConverter.to_34_array(self.player.tiles)
        return any([tiles_34[x] == 2 for x in valued_tiles])

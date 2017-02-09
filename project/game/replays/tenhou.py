# -*- coding: utf-8 -*-
import os
import time

from game.replays.base import Replay
from mahjong.meld import Meld


class TenhouReplay(Replay):

    def init_game(self):
        self.tags = []
        self.replay_name = '{}.log'.format(int(time.time()))

        self.tags.append('<mjloggm ver="2.3">')
        self.tags.append('<SHUFFLE seed="test" ref=""/>')
        self.tags.append('<GO type="1" lobby="0"/>')

        self.tags.append('<UN n0="{}" n1="{}" n2="{}" n3="{}" dan="20,20,20,20" '
                         'rate="2421.00,2437.00,2368.00,2569.00" sx="F,F,F,F"/>'.format(self.clients[0].player.name,
                                                                                        self.clients[1].player.name,
                                                                                        self.clients[2].player.name,
                                                                                        self.clients[3].player.name))

        self.tags.append('<TAIKYOKU oya="0"/>')

    def end_game(self):
        self.tags.append('</mjloggm>')

        with open(os.path.join(self.replays_directory, self.replay_name), 'w') as f:
            f.write(''.join(self.tags))

    def init_round(self, dealer, round_number, honba_sticks, riichi_sticks, dora):
        self.tags.append('<INIT seed="{},{},{},0,0,{}" ten="{}" oya="{}" '
                         'hai0="{}" hai1="{}" hai2="{}" hai3="{}"/>'
                         .format(round_number,
                                 honba_sticks,
                                 riichi_sticks,
                                 dora,
                                 self._players_scores(),
                                 dealer,
                                 ','.join([str(x) for x in self.clients[0].player.tiles]),
                                 ','.join([str(x) for x in self.clients[1].player.tiles]),
                                 ','.join([str(x) for x in self.clients[2].player.tiles]),
                                 ','.join([str(x) for x in self.clients[3].player.tiles])))

    def draw(self, who, tile):
        letters = ['T', 'U', 'V', 'W']
        self.tags.append('<{}{}/>'.format(letters[who], tile))

    def discard(self, who, tile):
        letters = ['D', 'E', 'F', 'G']
        self.tags.append('<{}{}/>'.format(letters[who], tile))

    def riichi(self, who, step):
        if step == 1:
            self.tags.append('<REACH who="{}" step="1"/>'.format(who))
        else:
            self.tags.append('<REACH who="{}" ten="{}" step="2"/>'.format(who, self._players_scores()))

    def open_meld(self, meld):
        self.tags.append('<N who="{}" m="{}" />'.format(meld.who, self._encode_meld(meld)))

    def retake(self, tempai_players, honba_sticks, riichi_sticks):
        hands = ''
        for seat in sorted(tempai_players):
            hands += 'hai{}="{}" '.format(seat, ','.join(str(x) for x in self.clients[seat].player.closed_hand))

        scores_results = []
        if len(tempai_players) > 0 and len(tempai_players) != 4:
            for client in self.clients:
                scores = int(client.player.scores // 100)
                if client.seat in tempai_players:
                    sign = '+'
                    scores_to_pay = int(30 / len(tempai_players))
                else:
                    sign = '-'
                    scores_to_pay = int(30 / (4 - len(tempai_players)))
                scores_results.append('{},{}{}'.format(scores, sign, scores_to_pay))
        else:
            for client in self.clients:
                scores = int(client.player.scores // 100)
                scores_results.append('{},0'.format(scores))

        self.tags.append('<RYUUKYOKU ba="{},{}" sc="{}" {}/>'.format(
            honba_sticks,
            riichi_sticks,
            ','.join(scores_results),
            hands))

    def win(self, who, from_who, win_tile, honba_sticks, riichi_sticks, han, fu, cost, yaku_list, dora, ura_dora):
        han_key = self.clients[who].player.closed_hand and 'closed' or 'open'
        scores = []
        for client in self.clients:
            # tsumo lose
            if from_who == who and client.seat != who:
                if client.player.is_dealer:
                    payment = cost['main'] + honba_sticks * 100
                else:
                    payment = cost['additional'] + honba_sticks * 100
                scores.append('{},-{}'.format(int(client.player.scores // 100), int(payment // 100)))
            # tsumo win
            elif client.seat == who and client.seat == from_who:
                if client.player.is_dealer:
                    payment = cost['main'] * 3
                else:
                    payment = cost['main'] + cost['additional'] * 2
                payment += honba_sticks * 300 + riichi_sticks * 1000
                scores.append('{},+{}'.format(int(client.player.scores // 100), int(payment // 100)))
            # ron win
            elif client.seat == who:
                payment = cost['main'] + honba_sticks * 300 + riichi_sticks * 1000
                scores.append('{},+{}'.format(int(client.player.scores // 100), int(payment // 100)))
            # ron lose
            elif client.seat == from_who:
                payment = cost['main'] + honba_sticks * 300
                scores.append('{},-{}'.format(int(client.player.scores // 100), int(payment // 100)))
            else:
                scores.append('{},0'.format(int(client.player.scores // 100)))

        yaku_string = ','.join(['{},{}'.format(x.id, x.han[han_key]) for x in yaku_list])
        self.tags.append('<AGARI ba="{},{}" hai="{}" machi="{}" ten="{},{},0" yaku="{}" doraHai="{}" '
                         'doraHaiUra="{}" who="{}" fromWho="{}" sc="{}" />'
                         .format(honba_sticks,
                                 riichi_sticks,
                                 ','.join([str(x) for x in self.clients[who].player.tiles]),
                                 win_tile,
                                 fu,
                                 cost['main'],
                                 yaku_string,
                                 ','.join([str(x) for x in dora]),
                                 ','.join([str(x) for x in ura_dora]),
                                 who,
                                 from_who,
                                 ','.join(scores)
                                 ))

    def _players_scores(self):
        return '{},{},{},{}'.format(int(self.clients[0].player.scores // 100),
                                    int(self.clients[1].player.scores // 100),
                                    int(self.clients[2].player.scores // 100),
                                    int(self.clients[3].player.scores // 100))

    def _encode_meld(self, meld):
        if meld.type == Meld.CHI:
            return self._encode_chi(meld)
        if meld.type == Meld.PON:
            return self._encode_pon(meld)
        return ''

    def _encode_chi(self, meld):
        result = []

        tiles = sorted(meld.tiles[:])
        base = int(tiles[0] / 4)

        called = tiles.index(meld.called_tile)
        base_and_called = int(((base // 9) * 7 + base % 9) * 3) + called
        result.append(self._to_binary_string(base_and_called))

        # chi format
        result.append('0')

        t0 = tiles[0] - base * 4
        t1 = tiles[1] - 4 - base * 4
        t2 = tiles[2] - 8 - base * 4

        result.append(self._to_binary_string(t2, 2))
        result.append(self._to_binary_string(t1, 2))
        result.append(self._to_binary_string(t0, 2))

        # it was a chi
        result.append('1')

        offset = self._from_who_offset(meld.who, meld.from_who)
        result.append(self._to_binary_string(offset, 2))

        # convert bytes to int
        result = int(''.join(result), 2)

        return str(result)

    def _encode_pon(self, meld):
        result = []

        tiles = sorted(meld.tiles[:])
        base = int(tiles[0] / 4)

        called = tiles.index(meld.called_tile)
        base_and_called = base * 3 + called
        result.append(self._to_binary_string(base_and_called))

        # just zero for format
        result.append('00')

        delta_array = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]
        delta = []
        for x in range(0, 3):
            delta.append(tiles[x] - base * 4)
        delta_index = delta_array.index(delta)
        result.append(self._to_binary_string(delta_index, 2))

        # not a chankan
        result.append('0')

        # pon
        result.append('1')

        # not a chi
        result.append('0')

        offset = self._from_who_offset(meld.who, meld.from_who)
        result.append(self._to_binary_string(offset, 2))

        # convert bytes to int
        result = int(''.join(result), 2)
        return str(result)

    def _to_binary_string(self, number, size=None):
        result = bin(number).replace('0b', '')
        # some bytes had to be with a fixed size
        if size and len(result) < size:
            while len(result) < size:
                result = '0' + result
        return result

    def _from_who_offset(self, who, from_who):
        result = from_who - who
        if result < 0:
            result += 4
        return result

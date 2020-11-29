# -*- coding: utf-8 -*-
import os

from game.bots_battle.replays.base import Replay
from mahjong.meld import Meld


class TenhouReplay(Replay):
    def init_game(self, seed):
        self.tags = []

        self.tags.append('<mjloggm ver="2.3">')
        self.tags.append('<SHUFFLE seed="{}" ref=""/>'.format(seed))
        self.tags.append('<GO type="1" lobby="0"/>')

        self.tags.append(
            '<UN n0="{}" n1="{}" n2="{}" n3="{}" dan="20,20,20,20" '
            'rate="2421.00,2437.00,2368.00,2569.00" sx="F,F,F,F"/>'.format(
                self.clients[0].player.name,
                self.clients[1].player.name,
                self.clients[2].player.name,
                self.clients[3].player.name,
            )
        )

        self.tags.append('<TAIKYOKU oya="0"/>')

    def end_game(self):
        self.tags[-1] = self.tags[-1].replace("/>", "")
        self.tags[-1] += 'owari="{}" />'.format(self._calculate_final_scores_and_uma())

        self.tags.append("</mjloggm>")

        self.save_log_file()

    def save_log_file(self, prefix=""):
        with open(os.path.join(self.replays_directory, prefix + self.replay_name), "w") as f:
            f.write("".join(self.tags))

    def save_failed_log(self):
        """
        When bot crashed we want to finish replay to be able reproduce crash
        """
        self.tags.append('<RYUUKYOKU owari="" />')
        self.tags.append("</mjloggm>")
        self.save_log_file(prefix="failed_")

    def init_round(self, dealer, round_number, honba_sticks, riichi_sticks, dora):
        self.tags.append(
            '<INIT seed="{},{},{},0,0,{}" ten="{}" oya="{}" '
            'hai0="{}" hai1="{}" hai2="{}" hai3="{}"/>'.format(
                round_number,
                honba_sticks,
                riichi_sticks,
                dora,
                self._players_scores(),
                dealer,
                ",".join([str(x) for x in self.clients[0].player.tiles]),
                ",".join([str(x) for x in self.clients[1].player.tiles]),
                ",".join([str(x) for x in self.clients[2].player.tiles]),
                ",".join([str(x) for x in self.clients[3].player.tiles]),
            )
        )

    def draw(self, who, tile):
        letters = ["T", "U", "V", "W"]
        self.tags.append("<{}{}/>".format(letters[who], tile))

    def discard(self, who, tile):
        letters = ["D", "E", "F", "G"]
        self.tags.append("<{}{}/>".format(letters[who], tile))

    def riichi(self, who, step):
        if step == 1:
            self.tags.append('<REACH who="{}" step="1"/>'.format(who))
        else:
            self.tags.append('<REACH who="{}" ten="{}" step="2"/>'.format(who, self._players_scores()))

    def open_meld(self, meld):
        self.tags.append('<N who="{}" m="{}" />'.format(meld.who, self._encode_meld(meld)))

    def retake(self, tempai_players, honba_sticks, riichi_sticks):
        hands = ""
        for seat in sorted(tempai_players):
            hands += 'hai{}="{}" '.format(seat, ",".join(str(x) for x in self.clients[seat].player.closed_hand))

        scores_results = []
        if len(tempai_players) > 0 and len(tempai_players) != 4:
            for client in self.clients:
                scores = int(client.player.scores // 100)
                if client.seat in tempai_players:
                    sign = "+"
                    scores_to_pay = int(30 / len(tempai_players))
                else:
                    sign = "-"
                    scores_to_pay = int(30 / (4 - len(tempai_players)))
                scores_results.append("{},{}{}".format(scores, sign, scores_to_pay))
        else:
            for client in self.clients:
                scores = int(client.player.scores // 100)
                scores_results.append("{},0".format(scores))

        self.tags.append(
            '<RYUUKYOKU ba="{},{}" sc="{}" {}/>'.format(honba_sticks, riichi_sticks, ",".join(scores_results), hands)
        )

    def abortive_retake(self, reason, honba_sticks, riichi_sticks):
        scores = "{},0,{},0,{},0,{},0".format(
            int(self.clients[0].player.scores // 100),
            int(self.clients[1].player.scores // 100),
            int(self.clients[2].player.scores // 100),
            int(self.clients[3].player.scores // 100),
        )

        self.tags.append(
            '<RYUUKYOKU type="{}" ba="{},{}" sc="{}"/>'.format(reason, honba_sticks, riichi_sticks, scores)
        )

    def win(self, who, from_who, win_tile, honba_sticks, riichi_sticks, han, fu, cost, yaku_list, dora, ura_dora):
        winner = self.clients[who].player
        scores = []
        for client in self.clients:
            # tsumo lose
            if from_who == who and client.seat != who:
                if client.player.is_dealer:
                    payment = cost["main"] + honba_sticks * 100
                else:
                    payment = cost["additional"] + honba_sticks * 100
                scores.append("{},-{}".format(int(client.player.scores // 100), int(payment // 100)))
            # tsumo win
            elif client.seat == who and client.seat == from_who:
                if client.player.is_dealer:
                    payment = cost["main"] * 3
                else:
                    payment = cost["main"] + cost["additional"] * 2
                payment += honba_sticks * 300 + riichi_sticks * 1000
                scores.append("{},+{}".format(int(client.player.scores // 100), int(payment // 100)))
            # ron win
            elif client.seat == who:
                payment = cost["main"] + honba_sticks * 300 + riichi_sticks * 1000
                scores.append("{},+{}".format(int(client.player.scores // 100), int(payment // 100)))
            # ron lose
            elif client.seat == from_who:
                payment = cost["main"] + honba_sticks * 300
                scores.append("{},-{}".format(int(client.player.scores // 100), int(payment // 100)))
            else:
                scores.append("{},0".format(int(client.player.scores // 100)))

        # tsumo
        if who == from_who:
            if winner.is_dealer:
                payment = cost["main"] * 3
            else:
                payment = cost["main"] + cost["additional"] * 2
        # ron
        else:
            payment = cost["main"]

        melds = []
        if winner.is_open_hand:
            for meld in winner.melds:
                melds.append(self._encode_meld(meld))
        melds = ",".join(melds)

        yaku_string = ",".join(
            ["{},{}".format(x.tenhou_id, winner.is_open_hand and x.han_open or x.han_closed) for x in yaku_list]
        )
        self.tags.append(
            '<AGARI ba="{},{}" hai="{}" machi="{}" m="{}" ten="{},{},0" yaku="{}" doraHai="{}" '
            'doraHaiUra="{}" who="{}" fromWho="{}" sc="{}" />'.format(
                honba_sticks,
                riichi_sticks,
                ",".join([str(x) for x in winner.closed_hand]),
                win_tile,
                melds,
                fu,
                payment,
                yaku_string,
                ",".join([str(x) for x in dora]),
                ",".join([str(x) for x in ura_dora]),
                who,
                from_who,
                ",".join(scores),
            )
        )

    def add_new_dora(self, dora_indicator):
        self.tags.append(f'<DORA hai="{dora_indicator}" />')

    def _players_scores(self):
        return "{},{},{},{}".format(
            int(self.clients[0].player.scores // 100),
            int(self.clients[1].player.scores // 100),
            int(self.clients[2].player.scores // 100),
            int(self.clients[3].player.scores // 100),
        )

    def _encode_meld(self, meld):
        if meld.type == Meld.CHI:
            return self._encode_chi(meld)
        if meld.type == Meld.PON:
            return self._encode_pon(meld)
        if meld.type == Meld.SHOUMINKAN:
            return self._encode_pon(meld, is_shouminkan=True)
        if meld.type == Meld.KAN:
            return self._encode_kan(meld)
        return ""

    def _encode_kan(self, meld):
        result = []

        tiles = sorted(meld.tiles[:])
        base = int(tiles[0] / 4)

        called = tiles.index(meld.called_tile)
        base_and_called = int(base * 4) + called
        result.append(self._to_binary_string(base_and_called))

        result.extend(["0", "0", "0", "0", "0", "0"])

        offset = self._from_who_offset(meld.who, meld.from_who)
        result.append(self._to_binary_string(offset, 2))

        # convert bites to int
        result = int("".join(result), 2)
        return str(result)

    def _encode_chi(self, meld):
        result = []

        tiles = sorted(meld.tiles[:])
        base = int(tiles[0] / 4)

        called = tiles.index(meld.called_tile)
        base_and_called = int(((base // 9) * 7 + base % 9) * 3) + called
        result.append(self._to_binary_string(base_and_called))

        # chi format
        result.append("0")

        t0 = tiles[0] - base * 4
        t1 = tiles[1] - 4 - base * 4
        t2 = tiles[2] - 8 - base * 4

        result.append(self._to_binary_string(t2, 2))
        result.append(self._to_binary_string(t1, 2))
        result.append(self._to_binary_string(t0, 2))

        # it was a chi
        result.append("1")

        offset = self._from_who_offset(meld.who, meld.from_who)
        result.append(self._to_binary_string(offset, 2))

        # convert bites to int
        result = int("".join(result), 2)

        return str(result)

    def _encode_pon(self, meld, is_shouminkan=False):
        result = []

        tiles = sorted(meld.tiles[:])
        base = int(tiles[0] / 4)

        called = tiles.index(meld.called_tile)
        base_and_called = base * 3 + called
        result.append(self._to_binary_string(base_and_called))

        # just zero for format
        result.append("00")

        delta_array = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]
        delta = []
        for x in range(0, 3):
            delta.append(tiles[x] - base * 4)
        delta_index = delta_array.index(delta)

        # not 100% sure that it is correct
        if is_shouminkan:
            delta_index = 2

        delta_bits = self._to_binary_string(delta_index, 2)
        result.append(delta_bits)

        # kan flag
        if is_shouminkan:
            result.append("1")
        else:
            result.append("0")

        # pon flag
        if is_shouminkan:
            result.append("0")
        else:
            result.append("1")

        # not a chi
        result.append("0")

        offset = self._from_who_offset(meld.who, meld.from_who)
        result.append(self._to_binary_string(offset, 2))

        # convert bites to int
        result = int("".join(result), 2)
        return str(result)

    def _to_binary_string(self, number, size=None):
        result = bin(number).replace("0b", "")
        # some bites had to be with a fixed size
        if size and len(result) < size:
            while len(result) < size:
                result = "0" + result
        return result

    def _from_who_offset(self, who, from_who):
        result = from_who - who
        if result < 0:
            result += 4
        return result

    def _calculate_final_scores_and_uma(self):
        data = []
        for client in self.clients:
            data.append({"position": None, "seat": client.seat, "uma": 0, "scores": client.player.scores})

        data = sorted(data, key=lambda x: (-x["scores"], x["seat"]))
        for x in range(0, len(data)):
            data[x]["position"] = x + 1

        uma_list = [20000, 10000, -10000, -20000]
        for item in data:
            x = item["scores"] - 30000 + uma_list[item["position"] - 1]

            # 10000 oka bonus for the first place
            if item["position"] == 1:
                x += 10000

            item["uma"] = round(x / 1000)
            item["scores"] = round(item["scores"] / 100)

        data = sorted(data, key=lambda x: x["seat"])
        results = []
        for item in data:
            results.append("{},{}".format(item["scores"], item["uma"]))

        return ",".join(results)

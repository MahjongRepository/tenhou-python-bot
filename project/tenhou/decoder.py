import re
from urllib.parse import unquote

from utils.decisions_logger import MeldPrint


class TenhouDecoder:
    RANKS = [
        "新人",
        "9級",
        "8級",
        "7級",
        "6級",
        "5級",
        "4級",
        "3級",
        "2級",
        "1級",
        "初段",
        "二段",
        "三段",
        "四段",
        "五段",
        "六段",
        "七段",
        "八段",
        "九段",
        "十段",
        "天鳳位",
    ]

    def parse_hello_string(self, message):
        rating_string = ""
        new_rank_message = ""

        if "PF4=" in message:
            rating_string = self.get_attribute_content(message, "PF4")

        if "nintei" in message:
            new_rank_message = unquote(self.get_attribute_content(message, "nintei"))

        return rating_string, new_rank_message

    def parse_initial_values(self, message):
        """
        Six element list:
            - Round number,
            - Number of honba sticks,
            - Number of riichi sticks,
            - First dice minus one,
            - Second dice minus one,
            - Dora indicator.
        """

        seed = self.get_attribute_content(message, "seed").split(",")
        seed = [int(i) for i in seed]

        round_wind_number = seed[0]
        count_of_honba_sticks = seed[1]
        count_of_riichi_sticks = seed[2]
        dora_indicator = seed[5]
        dealer = int(self.get_attribute_content(message, "oya"))

        scores = self.get_attribute_content(message, "ten").split(",")
        scores = [int(i) for i in scores]

        return {
            "round_wind_number": round_wind_number,
            "count_of_honba_sticks": count_of_honba_sticks,
            "count_of_riichi_sticks": count_of_riichi_sticks,
            "dora_indicator": dora_indicator,
            "dealer": dealer,
            "scores": scores,
        }

    def parse_initial_hand(self, message):
        tiles = self.get_attribute_content(message, "hai")
        tiles = [int(i) for i in tiles.split(",")]
        return tiles

    def parse_final_scores_and_uma(self, message):
        data = self.get_attribute_content(message, "owari")
        data = [float(i) for i in data.split(",")]

        # start at the beginning at take every second item (even)
        scores = data[::2]
        # start at second item and take every second item (odd)
        uma = data[1::2]

        return {"scores": scores, "uma": uma}

    def parse_names_and_ranks(self, message):
        ranks = self.get_attribute_content(message, "dan")
        # reconnection tag like '<UN n3="%4B%61%61%76%69" />'
        if not ranks:
            return None

        ranks = [int(i) for i in ranks.split(",")]

        return [
            {
                "seat": 0,
                "name": unquote(self.get_attribute_content(message, "n0")),
                "rank": TenhouDecoder.RANKS[ranks[0]],
            },
            {
                "seat": 1,
                "name": unquote(self.get_attribute_content(message, "n1")),
                "rank": TenhouDecoder.RANKS[ranks[1]],
            },
            {
                "seat": 2,
                "name": unquote(self.get_attribute_content(message, "n2")),
                "rank": TenhouDecoder.RANKS[ranks[2]],
            },
            {
                "seat": 3,
                "name": unquote(self.get_attribute_content(message, "n3")),
                "rank": TenhouDecoder.RANKS[ranks[3]],
            },
        ]

    def parse_log_link(self, message):
        seat = int(self.get_attribute_content(message, "oya"))
        seat = (4 - seat) % 4
        game_id = self.get_attribute_content(message, "log")
        return game_id, seat

    def parse_tile(self, message):
        # tenhou format: <t23/>, <e23/>, <f23 t="4"/>, <f23/>, <g23/>
        result = re.match(r"^<[tefgEFGTUVWD]+\d*", message).group()
        return int(result[2:])

    def parse_table_state_after_reconnection(self, message):
        players = []
        for x in range(0, 4):
            player = {"discards": [], "melds": []}

            discard_attr = "kawa{}".format(x)
            if discard_attr in message:
                discards = self.get_attribute_content(message, discard_attr)
                discards = [int(x) for x in discards.split(",")]

                was_riichi = 255 in discards
                if was_riichi:
                    discards.remove(255)

                player["discards"] = discards

            melds_attr = "m{}".format(x)
            if melds_attr in message:
                melds = self.get_attribute_content(message, melds_attr)
                melds = [int(x) for x in melds.split(",")]
                for item in melds:
                    meld_message = '<N who="{}" m="{}" />'.format(x, item)
                    meld = self.parse_meld(meld_message)
                    player["melds"].append(meld)

            players.append(player)

        for player in players:
            for meld in player["melds"]:
                players[meld.from_who]["discards"].append(meld.called_tile)

        return players

    def parse_dora_indicator(self, message):
        return int(self.get_attribute_content(message, "hai"))

    def parse_who_called_riichi(self, message):
        return int(self.get_attribute_content(message, "who"))

    def parse_go_tag(self, message):
        return int(self.get_attribute_content(message, "type"))

    def parse_meld(self, message):
        data = int(self.get_attribute_content(message, "m"))

        meld = MeldPrint()
        meld.who = int(self.get_attribute_content(message, "who"))
        # 'from_who' is encoded relative the the 'who', so we want
        # to convert it to be relative to our player
        meld.from_who = ((data & 0x3) + meld.who) % 4

        if data & 0x4:
            self.parse_chi(data, meld)
        elif data & 0x18:
            self.parse_pon(data, meld)
        elif data & 0x20:
            self.parse_nuki(data, meld)
        else:
            self.parse_kan(data, meld)

        return meld

    def parse_chi(self, data, meld):
        meld.type = MeldPrint.CHI
        t0, t1, t2 = (data >> 3) & 0x3, (data >> 5) & 0x3, (data >> 7) & 0x3
        base_and_called = data >> 10
        base = base_and_called // 3
        called = base_and_called % 3
        base = (base // 7) * 9 + base % 7
        meld.tiles = [t0 + 4 * (base + 0), t1 + 4 * (base + 1), t2 + 4 * (base + 2)]
        meld.called_tile = meld.tiles[called]

    def parse_pon(self, data, meld):
        t4 = (data >> 5) & 0x3
        t0, t1, t2 = ((1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2))[t4]
        base_and_called = data >> 9
        base = base_and_called // 3
        called = base_and_called % 3
        if data & 0x8:
            meld.type = MeldPrint.PON
            meld.tiles = [t0 + 4 * base, t1 + 4 * base, t2 + 4 * base]
            meld.called_tile = meld.tiles[called]
        else:
            meld.type = MeldPrint.SHOUMINKAN
            meld.tiles = [t0 + 4 * base, t1 + 4 * base, t2 + 4 * base, t4 + 4 * base]
            meld.called_tile = meld.tiles[3]

    def parse_kan(self, data, meld):
        base_and_called = data >> 8
        base = base_and_called // 4
        meld.type = MeldPrint.KAN
        meld.tiles = [4 * base, 1 + 4 * base, 2 + 4 * base, 3 + 4 * base]
        called = base_and_called % 4
        meld.called_tile = meld.tiles[called]
        # to mark closed\opened kans
        meld.opened = meld.who != meld.from_who

    def parse_nuki(self, data, meld):
        meld.type = MeldPrint.NUKI
        meld.tiles = [data >> 8]

    def get_attribute_content(self, message, attribute_name):
        result = re.findall(r'{}="([^"]*)"'.format(attribute_name), message)
        return result and result[0] or None

    def is_discarded_tile_message(self, message):
        if "<GO" in message:
            return False

        if "<FURITEN" in message:
            return False

        match_discard = re.match(r"^<[efgEFG]+\d*", message)
        if match_discard:
            return True

        return False

    def is_opened_set_message(self, message):
        return "<N who=" in message

    def get_enemy_seat(self, message):
        player_sign = message.lower()[1]
        if player_sign == "e":
            player_seat = 1
        elif player_sign == "f":
            player_seat = 2
        else:
            player_seat = 3

        return player_seat

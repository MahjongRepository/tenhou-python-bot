import json
import os
import re
import sys
from optparse import OptionParser

import requests
from game.table import Table
from mahjong.constants import DISPLAY_WINDS
from mahjong.tile import TilesConverter
from mahjong.utils import find_isolated_tile_indices
from tenhou.decoder import TenhouDecoder
from utils.decisions_logger import MeldPrint
from utils.logger import set_up_logging


class TenhouLogReproducer:
    """
    The way to debug bot decisions that it made in real tenhou.net games
    """

    def __init__(self, log_id, file_path, logger):
        self.decoder = TenhouDecoder()
        self.logger = logger
        self.table = None

        log_content = None
        if log_id:
            log_content = self._download_log_content(log_id)
        elif file_path:
            with open(file_path, "r") as f:
                log_content = f.read()

        self.rounds = []
        if log_content:
            self.rounds = self._parse_rounds(log_content)

    def print_meta_info(self):
        meta_information = {"players": [], "game_rounds": []}
        for round_item in self.rounds:
            for tag in round_item:
                if "<UN" in tag:
                    players = self.decoder.parse_names_and_ranks(tag)
                    if players:
                        meta_information["players"] = self.decoder.parse_names_and_ranks(tag)

                if "INIT" in tag:
                    init_values = self.decoder.parse_initial_values(tag)
                    meta_information["game_rounds"].append(
                        {
                            "wind": init_values["round_wind_number"] + 1,
                            "honba": init_values["count_of_honba_sticks"],
                            "round_start_scores": init_values["scores"],
                        }
                    )

        return meta_information

    def play_round(self, round_content, player_position, needed_tile, action, tile_number_to_stop):
        draw_tags = ["T", "U", "V", "W"]
        discard_tags = ["D", "E", "F", "G"]

        player_draw = draw_tags[player_position]

        player_draw_regex = re.compile(r"^<[{}]+\d*".format("".join(player_draw)))
        discard_regex = re.compile(r"^<[{}]+\d*".format("".join(discard_tags)))

        draw_regex = re.compile(r"^<[{}]+\d*".format("".join(draw_tags)))
        last_draws = {0: None, 1: None, 2: None, 3: None}

        self.table = Table()
        # TODO get this info from log content
        self.table.has_aka_dora = True
        self.table.has_open_tanyao = True
        self.table.player.init_logger(self.logger)

        players = {}
        for round_item in self.rounds:
            for tag in round_item:
                if "<UN" in tag:
                    players_temp = self.decoder.parse_names_and_ranks(tag)
                    if players_temp:
                        for x in players_temp:
                            players[x["seat"]] = x

        draw_tile_seen_number = 0
        enemy_discard_seen_number = 0
        for tag in round_content:
            if player_draw_regex.match(tag) and "UN" not in tag:
                tile = self.decoder.parse_tile(tag)
                self.table.count_of_remaining_tiles -= 1

                # is it time to stop reproducing?
                found_tile = TilesConverter.to_one_line_string([tile]) == needed_tile
                if action == "draw" and found_tile:
                    draw_tile_seen_number += 1
                    if draw_tile_seen_number == tile_number_to_stop:
                        self.logger.info("Stop on player draw")
                        return self._process_draw_action(tile)

                if action == "end":
                    # discard tag and next agari tag
                    next_next_tag_index = round_content.index(tag) + 2
                    next_next_tag = round_content[next_next_tag_index]
                    if self._is_agari(next_next_tag):
                        return self._process_draw_action(tile)

                    # closed kan and agari tag
                    next_next_tag_index = round_content.index(tag) + 3
                    if next_next_tag_index > len(round_content):
                        next_next_tag_index = len(round_content)
                    next_next_tag = round_content[next_next_tag_index]
                    if self._is_agari(next_next_tag):
                        return self._process_draw_action(tile)

                self.table.player.draw_tile(tile)

            if "INIT" in tag:
                values = self.decoder.parse_initial_values(tag)

                shifted_scores = []
                for x in range(0, 4):
                    shifted_scores.append(values["scores"][self._normalize_position(player_position, x)])

                self.table.init_round(
                    values["round_wind_number"],
                    values["count_of_honba_sticks"],
                    values["count_of_riichi_sticks"],
                    values["dora_indicator"],
                    self._normalize_position(values["dealer"], player_position),
                    shifted_scores,
                )

                hands = [
                    [int(x) for x in self.decoder.get_attribute_content(tag, "hai0").split(",")],
                    [int(x) for x in self.decoder.get_attribute_content(tag, "hai1").split(",")],
                    [int(x) for x in self.decoder.get_attribute_content(tag, "hai2").split(",")],
                    [int(x) for x in self.decoder.get_attribute_content(tag, "hai3").split(",")],
                ]

                self.table.player.init_hand(hands[player_position])
                self.table.player.name = players and players[player_position]["name"] or None

                self.logger.info("Init round info")
                self.logger.info(self.table.player.name)
                self.logger.info(f"Scores: {self.table.player.scores}")
                self.logger.info(f"Wind: {DISPLAY_WINDS[self.table.player.player_wind]}")

            if "DORA hai" in tag:
                self.table.add_dora_indicator(int(self._get_attribute_content(tag, "hai")))

            if draw_regex.match(tag) and "UN" not in tag:
                tile = self.decoder.parse_tile(tag)
                player_sign = tag.upper()[1]
                player_seat = self._normalize_position(draw_tags.index(player_sign), player_position)
                last_draws[player_seat] = tile

            if discard_regex.match(tag) and "DORA" not in tag:
                tile = self.decoder.parse_tile(tag)
                player_sign = tag.upper()[1]
                player_seat = self._normalize_position(discard_tags.index(player_sign), player_position)

                if player_seat == 0:
                    self.table.player.discard_tile(tile, force_tsumogiri=True)
                else:
                    # is it time to stop?
                    found_tile = TilesConverter.to_one_line_string([tile]) == needed_tile
                    is_kamicha_discard = player_seat == 3

                    if action == "enemy_discard" and found_tile:
                        enemy_discard_seen_number += 1
                        if enemy_discard_seen_number == tile_number_to_stop:
                            self.logger.info("Stop on enemy discard")
                            self._rebuild_bot_shanten_cache(self.table.player)
                            self.table.player.should_call_kan(tile, open_kan=True, from_riichi=False)
                            return self.table.player.try_to_call_meld(tile, is_kamicha_discard)

                    is_tsumogiri = last_draws[player_seat] == tile
                    self.table.add_discarded_tile(player_seat, tile, is_tsumogiri=is_tsumogiri)

            if "<N who=" in tag:
                meld = self.decoder.parse_meld(tag)
                player_seat = self._normalize_position(meld.who, player_position)
                self.table.add_called_meld(player_seat, meld)

                if player_seat == 0:
                    if meld.type != MeldPrint.KAN and meld.type != MeldPrint.SHOUMINKAN:
                        self.table.player.draw_tile(meld.called_tile)

            if "<REACH" in tag and 'step="1"' in tag:
                who_called_riichi = self._normalize_position(self.decoder.parse_who_called_riichi(tag), player_position)
                self.table.add_called_riichi_step_one(who_called_riichi)

            if "<REACH" in tag and 'step="2"' in tag:
                who_called_riichi = self._normalize_position(self.decoder.parse_who_called_riichi(tag), player_position)
                self.table.add_called_riichi_step_two(who_called_riichi)

    def reproduce(self, player, wind, honba, needed_tile, action, tile_number_to_stop):
        player_position = self._find_player_position(player)
        round_content = self._find_needed_round(wind, honba)
        return self.play_round(round_content, player_position, needed_tile, action, tile_number_to_stop)

    def _process_draw_action(self, tile):
        discard_result = None
        with_riichi = False
        self.table.player.draw_tile(tile)

        self.table.player.should_call_kan(tile, open_kan=False, from_riichi=self.table.player.in_riichi)

        if not self.table.player.in_riichi:
            discard_result, with_riichi = self.table.player.discard_tile()

        return discard_result, with_riichi

    def _find_needed_round(self, wind, honba):
        found_round_item = None
        for round_item in self.rounds:
            for tag in round_item:
                if "INIT" in tag:
                    init_values = self.decoder.parse_initial_values(tag)
                    if init_values["round_wind_number"] + 1 == wind and init_values["count_of_honba_sticks"] == honba:
                        found_round_item = round_item
        if not found_round_item:
            raise Exception(
                f"Can't find wind={wind}, honba={honba} game round. "
                f"Check log with --meta tag first to be sure that these attrs are correct."
            )
        return found_round_item

    def _rebuild_bot_shanten_cache(self, player):
        isolated_tile_34 = find_isolated_tile_indices(TilesConverter.to_34_array(player.closed_hand))[0]
        isolated_tile_136 = isolated_tile_34 * 4
        player.table.revealed_tiles[isolated_tile_34] -= 1
        player.draw_tile(isolated_tile_136)
        player.discard_tile()

    def _find_player_position(self, player):
        # seat number was provided
        try:
            position = int(player)
            if position > 3:
                raise Exception("Player seat can't be more than 3")
            return position
        except ValueError:
            pass

        # player nickname was provided
        for round_item in self.rounds:
            for tag in round_item:
                if "<UN" in tag:
                    values = self.decoder.parse_names_and_ranks(tag)
                    found_player = [x for x in values if x["name"] == player]
                    if len(found_player) == 0 or len(found_player) > 1:
                        raise Exception(f"Found players with '{player}' nickname: {len(found_player)}")
                    return found_player[0]["seat"]

    def _normalize_position(self, who, from_who):
        positions = [0, 1, 2, 3]
        return positions[who - from_who]

    def _download_log_content(self, log_id):
        """
        Check the log file, and if it is not there download it from tenhou.net
        """
        temp_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs")
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)

        log_file = os.path.join(temp_folder, log_id)
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                return f.read()
        else:
            url = f"http://tenhou.net/0/log/?{log_id}"
            response = requests.get(url)

            with open(log_file, "w") as f:
                f.write(response.text)

            return response.text

    def _parse_rounds(self, log_content):
        """
        Parse xml log to lists of tags
        """
        rounds = []

        game_round = []
        tag_start = 0
        tag = None
        for x in range(0, len(log_content)):
            if log_content[x] == ">":
                tag = log_content[tag_start : x + 1]
                tag_start = x + 1

            # not useful tags
            if tag and ("mjloggm" in tag or "TAIKYOKU" in tag):
                tag = None

            # new round was started
            if tag and "INIT" in tag:
                rounds.append(game_round)
                game_round = []

            # the end of the game
            if tag and "owari" in tag:
                rounds.append(game_round)

            if tag:
                # to save some memory we can remove not needed information from logs
                if "INIT" in tag:
                    # we dont need seed information
                    find = re.compile(r'shuffle="[^"]*"')
                    tag = find.sub("", tag)

                # add processed tag to the round
                game_round.append(tag)
                tag = None

        return rounds

    def _is_discard(self, tag):
        skip_tags = ["<GO", "<FURITEN", "<DORA"]
        if any([x in tag for x in skip_tags]):
            return False

        match_discard = re.match(r"^<[defgDEFG]+\d*", tag)
        if match_discard:
            return True

        return False

    def _is_draw(self, tag):
        match_discard = re.match(r"^<[tuvwTUVW]+\d*", tag)
        if match_discard:
            return True

        return False

    def _is_agari(self, tag):
        return "AGARI" in tag

    def _parse_tile(self, tag):
        result = re.match(r"^<[defgtuvwDEFGTUVW]+\d*", tag).group()
        return int(result[2:])

    def _is_init_tag(self, tag):
        return tag and "INIT" in tag

    def _get_attribute_content(self, tag, attribute_name):
        result = re.findall(r'{}="([^"]*)"'.format(attribute_name), tag)
        return result and result[0] or None


def parse_args_and_start_reproducer(logger):
    opts = parse_reproducer_args(sys.argv)

    reproducer = TenhouLogReproducer(opts.log, opts.file, logger)
    if opts.meta:
        meta_information = reproducer.print_meta_info()
        logger.debug(json.dumps(meta_information, indent=2, ensure_ascii=False))
    else:
        reproducer.reproduce(opts.player, opts.wind, opts.honba, opts.tile, opts.action, opts.n)


def parse_reproducer_args(args):
    parser = OptionParser()

    parser.add_option(
        "--log",
        type="string",
        help="Tenhou.net log link. Example: 2020102008gm-0001-7994-9438a8f4",
    )
    parser.add_option(
        "--file",
        type="string",
        help="Path to local game log file",
    )
    parser.add_option(
        "--meta",
        action="store_true",
        help="Print meta information about the game",
    )
    parser.add_option(
        "--player",
        type="string",
        help="Player seat number [0, 3] or player nickname",
    )
    parser.add_option(
        "--wind",
        type="int",
        help="Wind number where to stop. 1-4 for east, 5-8 for south, 9-12 for west",
    )
    parser.add_option(
        "--honba",
        type="int",
        help="Honba number where to stop",
    )
    parser.add_option(
        "--tile",
        type="string",
        help='Tile where to stop in "2s", "5m" format',
    )
    parser.add_option(
        "--n",
        type="int",
        default=1,
        help="On what discarded tile we need to stop",
    )
    parser.add_option(
        "--action",
        type="string",
        default="draw",
        help="Action where to stop. Available options: draw, enemy_discard",
    )

    opts, _ = parser.parse_args(args)
    return opts


def main():
    logger = set_up_logging(save_to_file=False)
    parse_args_and_start_reproducer(logger)


if __name__ == "__main__":
    main()

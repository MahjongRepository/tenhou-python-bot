from typing import Optional

import utils.decisions_constants as log
from game.ai.configs.default import BotDefaultConfig
from game.ai.main import MahjongAI
from mahjong.constants import CHUN, EAST, HAKU, HATSU, NORTH, SOUTH, WEST
from mahjong.tile import Tile, TilesConverter
from utils.decisions_logger import DecisionsLogger, MeldPrint


class PlayerInterface:
    table = None
    discards = None
    tiles = None
    melds = None
    round_step = None

    # current player seat
    seat = 0
    # where is sitting dealer, based on this information we can calculate player wind
    dealer_seat = 0
    # it is important to know initial seat for correct players sorting
    first_seat = 0

    # position based on scores
    position = 0
    scores = None
    uma = 0

    name = ""
    rank = ""

    logger = None

    in_riichi: bool = False
    is_ippatsu: bool = False
    is_oikake_riichi: bool = False
    is_oikake_riichi_against_dealer_riichi_threat: bool = False
    is_riichi_against_open_hand_threat: bool = False

    def __init__(self, table, seat, dealer_seat):
        self.table = table
        self.seat = seat
        self.dealer_seat = dealer_seat
        self.logger = DecisionsLogger()

        self.erase_state()

    def __str__(self):
        result = "{0}".format(self.name)
        if self.scores is not None:
            result += " ({:,d})".format(int(self.scores))
            if self.uma:
                result += " {0}".format(self.uma)
        else:
            result += " ({0})".format(self.rank)
        return result

    def __repr__(self):
        return self.__str__()

    def init_logger(self, logger):
        self.logger.logger = logger

    def erase_state(self):
        self.tiles = []
        self.discards = []
        self.melds = []
        self.in_riichi = False
        self.is_ippatsu = False
        self.is_oikake_riichi = False
        self.is_oikake_riichi_against_dealer_riichi_threat = False
        self.is_riichi_against_open_hand_threat = False
        self.position = 0
        self.scores = None
        self.uma = 0
        self.round_step = 0

    def add_called_meld(self, meld: MeldPrint):
        # we already added shouminkan as a pon set
        if meld.type == MeldPrint.SHOUMINKAN:
            tile_34 = meld.tiles[0] // 4

            pon_set = [x for x in self.melds if x.type == MeldPrint.PON and (x.tiles[0] // 4) == tile_34]

            # when we are doing reconnect and we have called shouminkan set
            # we will not have called pon set in the hand
            if pon_set:
                self.melds.remove(pon_set[0])

        # we need to add tile that we used for open can to the hand
        if meld.type == MeldPrint.KAN and meld.opened:
            self.tiles.append(meld.called_tile)

        self.melds.append(meld)

    def add_discarded_tile(self, tile: Tile):
        self.discards.append(tile)

        # all tiles that were discarded after player riichi will be safe against him
        # because of furiten
        tile = tile.value // 4
        for player in self.table.players[1:]:
            if player.in_riichi and tile not in player.safe_tiles:
                player.safe_tiles.append(tile)

        # one discard == one round step
        self.round_step += 1

    @property
    def player_wind(self):
        shift = self.dealer_seat - self.seat
        position = [0, 1, 2, 3][shift]
        if position == 0:
            return EAST
        elif position == 1:
            return NORTH
        elif position == 2:
            return WEST
        else:
            return SOUTH

    @property
    def is_dealer(self):
        return self.seat == self.dealer_seat

    @property
    def is_open_hand(self):
        opened_melds = [x for x in self.melds if x.opened]
        return len(opened_melds) > 0

    @property
    def meld_tiles(self):
        """
        Array of 136 tiles format
        :return:
        """
        result = []
        for meld in self.melds:
            result.extend(meld.tiles)
        return result

    @property
    def meld_34_tiles(self):
        """
        Array of array with 34 tiles indices
        :return: array
        """
        melds = [x.tiles[:] for x in self.melds]
        results = []
        for meld in melds:
            meld_34 = [meld[0] // 4, meld[1] // 4, meld[2] // 4]
            # kan
            if len(meld) > 3:
                meld_34.append(meld[3] // 4)
            results.append(meld_34)
        return results

    @property
    def valued_honors(self):
        return [CHUN, HAKU, HATSU, self.table.round_wind_tile, self.player_wind]


class Player(PlayerInterface):
    ai: Optional[MahjongAI] = None
    config: Optional[BotDefaultConfig] = None
    last_draw = None
    in_tempai = False

    def __init__(self, table, seat, dealer_seat, bot_config: Optional[BotDefaultConfig]):
        super().__init__(table, seat, dealer_seat)
        self.config = bot_config or BotDefaultConfig()
        self.ai = MahjongAI(self)

    def erase_state(self):
        super().erase_state()

        self.last_draw = None
        self.in_tempai = False

        if self.ai:
            self.ai.erase_state()

    def init_hand(self, tiles):
        self.tiles = tiles

        self.ai.init_hand()

    def draw_tile(self, tile_136):
        context = [
            f"Step: {self.round_step}",
            f"Remaining tiles: {self.table.count_of_remaining_tiles}",
            f"Hand: {self.format_hand_for_print(tile_136)}",
        ]
        if self.ai.current_strategy:
            context.append(f"Current strategy: {self.ai.current_strategy}")

        self.logger.debug(log.DRAW, context=context)

        self.last_draw = tile_136
        self.tiles.append(tile_136)

        # we need sort it to have a better string presentation
        self.tiles = sorted(self.tiles)

        self.ai.draw_tile(tile_136)

    def discard_tile(self, discard_tile=None, force_tsumogiri=False):
        if force_tsumogiri:
            tile_to_discard = discard_tile
            with_riichi = False
        else:
            tile_to_discard, with_riichi = self.ai.discard_tile(discard_tile)

        is_tsumogiri = tile_to_discard == self.last_draw
        # it is important to use table method,
        # to recalculate revealed tiles and etc.
        self.table.add_discarded_tile(0, tile_to_discard, is_tsumogiri)
        self.tiles.remove(tile_to_discard)

        return tile_to_discard, with_riichi

    # FIXME: remove this method and cleanup tests
    def formal_riichi_conditions(self):
        return all(
            [
                self.in_tempai,
                not self.in_riichi,
                not self.is_open_hand,
                self.scores >= 1000,
                self.table.count_of_remaining_tiles > 4,
            ]
        )

    def should_call_kan(self, tile, open_kan, from_riichi=False):
        return self.ai.kan.should_call_kan(tile, open_kan, from_riichi)

    def should_call_win(self, tile, is_tsumo, enemy_seat=None, is_chankan=False):
        return self.ai.should_call_win(tile, is_tsumo, enemy_seat, is_chankan)

    def should_call_kyuushu_kyuuhai(self):
        return self.ai.should_call_kyuushu_kyuuhai()

    def try_to_call_meld(self, tile, is_kamicha_discard):
        return self.ai.try_to_call_meld(tile, is_kamicha_discard)

    def enemy_called_riichi(self, player_seat):
        self.ai.enemy_called_riichi(player_seat)

    def number_of_revealed_tiles(self, tile_34, closed_hand_34):
        """
        Return sum of all tiles (discarded + from melds + our hand)
        :param tile_34: 34 tile format
        :param closed_hand_34: cached list of tiles (to not build it for each iteration)
        :return: int
        """
        revealed_tiles = closed_hand_34[tile_34] + self.table.revealed_tiles[tile_34]
        assert revealed_tiles <= 4, "we have only 4 tiles in the game"
        return revealed_tiles

    def format_hand_for_print(self, tile_136=None):
        hand_string = "{}".format(
            TilesConverter.to_one_line_string(self.closed_hand, print_aka_dora=self.table.has_aka_dora)
        )

        if tile_136 is not None:
            hand_string += " + {}".format(
                TilesConverter.to_one_line_string([tile_136], print_aka_dora=self.table.has_aka_dora)
            )

        melds = []
        for item in self.melds:
            melds.append(
                "{}".format(TilesConverter.to_one_line_string(item.tiles, print_aka_dora=self.table.has_aka_dora))
            )

        if melds:
            hand_string += " [{}]".format(", ".join(melds))

        return hand_string

    @property
    def closed_hand(self):
        tiles = self.tiles[:]
        return [item for item in tiles if item not in self.meld_tiles]


class EnemyPlayer(PlayerInterface):
    # array of tiles in 34 tile format
    safe_tiles = None
    # tiles that were discarded in the current "step"
    # so, for example kamicha discard will be a safe tile for all players
    temporary_safe_tiles = None

    riichi_tile_136 = None

    def erase_state(self):
        super().erase_state()

        self.safe_tiles = []
        self.temporary_safe_tiles = []
        self.riichi_tile_136 = None

    def add_discarded_tile(self, tile: Tile):
        super().add_discarded_tile(tile)

        tile = tile.value // 4
        if tile not in self.safe_tiles:
            self.safe_tiles.append(tile)

        # erase temporary furiten after tile draw
        self.temporary_safe_tiles = []
        affected_players = [1, 2, 3]
        affected_players.remove(self.seat)

        # temporary furiten, for one "step"
        for x in affected_players:
            if tile not in self.table.get_player(x).temporary_safe_tiles:
                self.table.get_player(x).temporary_safe_tiles.append(tile)

    @property
    def all_safe_tiles(self):
        return list(set(self.temporary_safe_tiles + self.safe_tiles))

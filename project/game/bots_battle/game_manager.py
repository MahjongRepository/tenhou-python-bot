import datetime
import logging
from collections import deque
from random import randint, random, seed

from game.bots_battle.local_client import LocalClient
from game.bots_battle.replays.tenhou import TenhouReplay
from mahjong.agari import Agari
from mahjong.constants import WINDS
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from mahjong.utils import is_honor, is_terminal
from utils.decisions_logger import MeldPrint
from utils.settings_handler import settings

# we need to have it
# to be able repeat our tests with needed random
seed_value = random()

logger = logging.getLogger("game")


# to be able repeat our games
def shuffle_seed():
    return seed_value


class GameManager:
    """
    Allow to play bots between each other
    To have a metrics how new version plays against old versions
    """

    replay_name = ""

    tiles = None
    dead_wall = None
    clients = None
    dora_indicators = None
    players_with_open_hands = None
    discards = None
    replay = None

    dealer = None
    current_client_seat = None
    round_number = 0
    honba_sticks = 0
    riichi_sticks = 0

    _unique_dealers = 0
    _need_to_check_same_winds = None

    def __init__(self, clients, replays_directory, replay_name):
        self.tiles = []
        self.dead_wall = []
        self.dora_indicators = []
        self.discards = []
        self.clients = clients

        self.agari = Agari()
        self.finished_hand = HandCalculator()
        self.replays_directory = replays_directory
        self.replay_name = replay_name

    @staticmethod
    def generate_replay_name():
        return f"{datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}_{randint(0, 99999):03}.txt"

    def init_game(self):
        """
        Beginning of the game.
        Clients random placement and dealer selection.
        """

        logger.info("Replay name: {}".format(self.replay_name))
        self.replay = TenhouReplay(self.replay_name, self.clients, self.replays_directory)

        seed(shuffle_seed())
        self.clients = self._randomly_shuffle_array(self.clients)
        for i in range(0, len(self.clients)):
            self.clients[i].seat = i

        # oya should be always first player
        # to have compatibility with tenhou format
        self.set_dealer(0)

        for client in self.clients:
            client.player.scores = 25000

        self._unique_dealers = 0
        self.round_number = 0

    def play_game(self):
        logger.info("The start of the game")

        is_game_end = False
        self.init_game()
        self.replay.init_game(shuffle_seed())

        while not is_game_end:
            self.init_round()

            results = self.play_round()

            dealer_won = False
            was_retake = False
            for result in results:
                # we want to increase honba in that case and don't move dealer seat
                if result["is_abortive_retake"]:
                    dealer_won = True

                if not result["winner"]:
                    was_retake = True
                    continue

                if result["winner"].player.is_dealer:
                    dealer_won = True

            old_dealer = self.dealer
            # if dealer won we need to increment honba sticks
            if dealer_won:
                self.honba_sticks += 1
            # otherwise let's move dealer seat
            else:
                # retake and dealer is noten
                if was_retake:
                    self.honba_sticks += 1
                else:
                    self.honba_sticks = 0

                new_dealer = self._move_position(self.dealer)
                self.set_dealer(new_dealer)

            is_game_end = self._check_the_end_of_game(old_dealer)

            # important increment, we are building wall seed based on the round number
            self.round_number += 1

        winner = self.recalculate_players_position()
        # winner takes riichi sticks
        winner.player.scores += self.riichi_sticks * 1000
        self.replay.end_game()

        logger.info("Final Scores: {0}".format(self.players_sorted_by_scores()))

        total_scores = sum([x.player.scores for x in self.clients])
        assert total_scores == 100000, total_scores

    def init_round(self):
        """
        Generate players hands, dead wall and dora indicators
        """
        self._need_to_check_same_winds = True

        self.players_with_open_hands = []
        self.dora_indicators = []

        self.tiles = self._generate_wall()

        for client in self.clients:
            client.erase_state()

        self.dead_wall = self._cut_tiles(14)
        self.add_new_dora_indicator()

        for x in range(0, len(self.clients)):
            client = self.clients[x]

            # each client think that he is a player with position = 0
            # so, we need to move dealer position for each client
            # and shift scores array
            client_dealer = self._enemy_position(self.dealer, x)

            player_scores = deque([i.player.scores / 100 for i in self.clients])
            player_scores.rotate(x * -1)
            player_scores = list(player_scores)

            client.table.init_round(
                self._unique_dealers,
                self.honba_sticks,
                self.riichi_sticks,
                self.dora_indicators[0],
                client_dealer,
                player_scores,
            )

        # each player by rotation draw 4 tiles until they have 12
        # after this each player draw one more tile
        # and this is will be their initial hand
        # we do it to make the tiles allocation in hands
        # more random
        for _ in range(0, 3):
            for client in self.clients:
                client.player.tiles += self._cut_tiles(4)

        for client in self.clients:
            client.player.tiles += self._cut_tiles(1)
            client.player.tiles = sorted(client.player.tiles)
            client.player.init_hand(client.player.tiles)

        logger.info("Seed: {}".format(shuffle_seed()))
        logger.info("Dealer: {}, {}".format(self.dealer, self.clients[self.dealer].player.name))
        logger.info(
            "Wind: {}. Riichi sticks: {}. Honba sticks: {}".format(
                self._unique_dealers, self.riichi_sticks, self.honba_sticks
            )
        )
        logger.info("Round number: {}".format(self.round_number))
        logger.info("Players: {0}".format(self.players_sorted_by_scores()))

        self.replay.init_round(
            self.dealer, self._unique_dealers, self.honba_sticks, self.riichi_sticks, self.dora_indicators[0]
        )

    def play_round(self) -> []:
        continue_to_play = True

        number_of_kan_sets_per_player = {0: 0, 1: 0, 2: 0, 3: 0}
        while continue_to_play:
            current_client = self._get_current_client()

            in_tempai = current_client.player.in_tempai

            drawn_tile = self._cut_tiles(1)[0]

            drawn_tile_34 = drawn_tile // 4
            current_client.table.count_of_remaining_tiles -= 1
            self.replay.draw(current_client.seat, drawn_tile)

            current_client.player.draw_tile(drawn_tile)
            tiles = current_client.player.tiles

            if (
                self.player_can_call_kyuushu_kyuuhai(current_client.player)
                and current_client.player.should_call_kyuushu_kyuuhai()
            ):
                return [self.abortive_retake(AbortiveDraw.NINE_DIFFERENT)]

            # win by tsumo after tile draw
            is_win = self.agari.is_agari(TilesConverter.to_34_array(tiles), current_client.player.meld_34_tiles)
            if is_win:
                tiles.remove(drawn_tile)
                can_win = True

                # with open hand it can be situation when we in the tempai
                # but our hand doesn't contain any yaku
                # in that case we can't call ron
                if not current_client.player.in_riichi:
                    result = current_client.player.ai.estimate_hand_value_or_get_from_cache(
                        drawn_tile_34, is_tsumo=True, is_rinshan=current_client.is_rinshan
                    )
                    can_win = result.error is None

                if can_win:
                    result = self.process_the_end_of_the_round(
                        tiles=tiles, win_tile=drawn_tile, winner=current_client, loser=None, is_tsumo=True
                    )
                    return [result]
                else:
                    # we can't win
                    # so let's add tile back to hand
                    # and discard it later
                    tiles.append(drawn_tile)

            # checks if we can call closed kan or shouminkan
            current_client_tiles_34 = TilesConverter.to_34_array(current_client.player.tiles)
            if current_client_tiles_34[drawn_tile_34] == 4 and len(self.tiles) > 1:
                kan_type = current_client.player.should_call_kan(
                    drawn_tile, open_kan=False, from_riichi=current_client.player.in_riichi
                )
                if kan_type:
                    tiles = [
                        (drawn_tile_34 * 4),
                        (drawn_tile_34 * 4) + 1,
                        (drawn_tile_34 * 4) + 2,
                        (drawn_tile_34 * 4) + 3,
                    ]
                    opened = False
                    if kan_type == MeldPrint.SHOUMINKAN:
                        opened = True
                    meld = MeldPrint(
                        kan_type,
                        tiles,
                        opened=opened,
                        called_tile=drawn_tile,
                        who=current_client.seat,
                        from_who=current_client.seat,
                    )
                    logger.info("Called meld: {} by {}".format(meld, current_client.player.name))

                    self.replay.open_meld(meld)

                    if opened:
                        for client in self.clients:
                            client.is_ippatsu = False

                        result = self.check_clients_possible_ron(
                            current_client, drawn_tile, is_tsumogiri=False, is_chankan=True
                        )

                        # the end of the round
                        if result:
                            return result

                    number_of_kan_sets_per_player[current_client.seat] += 1
                    if (
                        sum(number_of_kan_sets_per_player.values()) == 4
                        and len(number_of_kan_sets_per_player.values()) != 1
                    ):
                        return [self.abortive_retake(AbortiveDraw.FOUR_KANS)]

                    # we need to notify each client about called meld
                    for _client in self.clients:
                        _client.table.add_called_meld(self._enemy_position(current_client.seat, _client.seat), meld)

                    self.add_new_dora_indicator()

                    current_client.is_rinshan = True

                    # after that we will return to the current client next draw
                    continue

            # we had to clear state after tile draw
            current_client.is_ippatsu = False
            current_client.is_rinshan = False

            # if not in riichi, let's decide what tile to discard
            if not current_client.player.in_riichi:
                tile, with_riichi = current_client.player.discard_tile()
                in_tempai = current_client.player.in_tempai
                if with_riichi:
                    assert in_tempai
            else:
                tile, with_riichi = current_client.player.discard_tile(drawn_tile, force_tsumogiri=True)
                assert not with_riichi

            who_called_riichi_seat = None
            if in_tempai and not current_client.player.is_open_hand and with_riichi:
                who_called_riichi_seat = current_client.seat
                for client in self.clients:
                    client.table.add_called_riichi_step_one(self._enemy_position(who_called_riichi_seat, client.seat))
                self.replay.riichi(current_client.seat, 1)

            self.replay.discard(current_client.seat, tile)
            is_tsumogiri = drawn_tile == tile
            result = self.check_clients_possible_ron(current_client, tile, is_tsumogiri)
            # the end of the round
            if result:
                # check_clients_possible_ron already returns array
                return result

            # if there is no challenger to ron, let's check can we call riichi with tile discard or not
            if who_called_riichi_seat is not None:
                self.call_riichi(current_client)
                for client in self.clients:
                    client.table.add_called_riichi_step_two(self._enemy_position(who_called_riichi_seat, client.seat))
                self.replay.riichi(current_client.seat, 2)

                count_of_riichi_players = 0
                for client in self.clients:
                    if client.player.in_riichi:
                        count_of_riichi_players += 1

                if count_of_riichi_players == 4:
                    return [self.abortive_retake(AbortiveDraw.FOUR_RIICHI)]

            # abortive retake
            result = self._check_same_winds()
            if result:
                return [result]

            # let's check other players hand to possibility open sets
            possible_melds = []

            tile_34 = tile // 4
            for other_client in self.clients:
                # there is no need to check the current client
                # or check client in riichi
                if other_client == current_client or other_client.player.in_riichi:
                    continue

                # was a tile discarded by the left player or not
                if other_client.seat == 0:
                    is_kamicha_discard = current_client.seat == 3
                else:
                    is_kamicha_discard = other_client.seat - current_client.seat == 1

                other_client.table.revealed_tiles[tile_34] -= 1

                # opened kan
                other_client_closed_hand_34 = TilesConverter.to_34_array(other_client.player.closed_hand)
                if (
                    other_client_closed_hand_34[tile_34] == 3
                    and len(self.tiles) > 1
                    and other_client.player.should_call_kan(tile, open_kan=True)
                ):
                    tiles = [
                        (tile_34 * 4),
                        (tile_34 * 4) + 1,
                        (tile_34 * 4) + 2,
                        (tile_34 * 4) + 3,
                    ]
                    meld = MeldPrint(
                        MeldPrint.KAN,
                        tiles,
                        opened=True,
                        called_tile=tile,
                        who=other_client.seat,
                        from_who=current_client.seat,
                    )
                    logger.info("Called meld: {} by {}".format(meld, other_client.player.name))

                    self.replay.open_meld(meld)

                    # we changed current client seat
                    self.players_with_open_hands.append(other_client.seat)

                    number_of_kan_sets_per_player[other_client.seat] += 1
                    if (
                        sum(number_of_kan_sets_per_player.values()) == 4
                        and len(number_of_kan_sets_per_player.values()) != 1
                    ):
                        return [self.abortive_retake(AbortiveDraw.FOUR_KANS)]

                    # we need to notify each client about called meld
                    for _client in self.clients:
                        _client.table.add_called_meld(self._enemy_position(other_client.seat, _client.seat), meld)

                    self.add_new_dora_indicator()

                    # move to draw tile action
                    other_client.is_rinshan = True
                    self.current_client_seat = self._move_position(other_client.seat, shift=-1)
                    continue

                meld, discard_option = other_client.player.try_to_call_meld(tile, is_kamicha_discard)

                other_client.table.revealed_tiles[tile_34] += 1

                if meld:
                    meld.from_who = current_client.seat
                    meld.who = other_client.seat
                    meld.called_tile = tile
                    possible_melds.append({"meld": meld, "discard_option": discard_option})

            if possible_melds:
                # pon is more important than chi
                possible_melds = sorted(possible_melds, key=lambda x: x["meld"].type == Meld.PON)
                meld = possible_melds[0]["meld"]
                discard_option = possible_melds[0]["discard_option"]

                # clear ippatsu after called meld
                for client_item in self.clients:
                    client_item.is_ippatsu = False

                # we changed current client with called open set
                self.current_client_seat = meld.who
                current_client = self._get_current_client()
                self.players_with_open_hands.append(self.current_client_seat)

                logger.info("Called meld: {} by {}".format(meld, current_client.player.name))

                # we need to notify each client about called meld
                for _client in self.clients:
                    _client.table.add_called_meld(self._enemy_position(current_client.seat, _client.seat), meld)

                self.replay.open_meld(meld)
                current_client.player.tiles.append(tile)
                discarded_tile, with_riichi = current_client.player.discard_tile(discard_option)
                assert not with_riichi

                self.replay.discard(current_client.seat, discarded_tile)

                # the end of the round
                result = self.check_clients_possible_ron(current_client, discarded_tile, False)
                if result:
                    # check_clients_possible_ron already returns array
                    return result

            self.current_client_seat = self._move_position(self.current_client_seat)

            # retake
            if not len(self.tiles):
                continue_to_play = False

        result = self.process_the_end_of_the_round([], 0, None, None, False)
        return [result]

    def check_clients_possible_ron(self, current_client, tile, is_tsumogiri, is_chankan=False) -> []:
        """
        After tile discard let's check all other players can they win or not
        at this tile
        """
        possible_win_client = []
        for other_client in self.clients:
            # there is no need to check the current client
            if other_client == current_client:
                continue

            # let's store other players discards
            if not is_chankan:
                other_client.table.add_discarded_tile(
                    self._enemy_position(current_client.seat, other_client.seat), tile, is_tsumogiri
                )

            if self.can_call_ron(
                other_client, tile, self._enemy_position(current_client.seat, other_client.seat), is_chankan
            ):
                possible_win_client.append(other_client)

        if len(possible_win_client) == 3:
            return [self.abortive_retake(AbortiveDraw.TRIPLE_RON)]

        # check multiple ron
        results = []
        for client in possible_win_client:
            result = self.process_the_end_of_the_round(
                tiles=client.player.tiles,
                win_tile=tile,
                winner=client,
                loser=current_client,
                is_tsumo=False,
                is_chankan=is_chankan,
            )
            results.append(result)

        return results

    def recalculate_players_position(self):
        """
        For players with same count of scores we need
        to set position based on their initial seat on the table
        """
        temp_clients = sorted(self.clients, key=lambda x: x.player.scores, reverse=True)
        for i in range(0, len(temp_clients)):
            temp_client = temp_clients[i]

            for client in self.clients:
                if client.id == temp_client.id:
                    client.player.position = i + 1

        # return winner of the game
        return sorted([x for x in self.clients], key=lambda x: x.player.position)[0]

    def can_call_ron(self, client, win_tile, shifted_enemy_seat, is_chankan):
        if not client.player.in_tempai:
            return False

        tiles = client.player.tiles
        is_agari = self.agari.is_agari(TilesConverter.to_34_array(tiles + [win_tile]), client.player.meld_34_tiles)
        if not is_agari:
            return False

        # check for furiten
        for item in client.player.discards:
            discarded_tile = item.value // 4
            if discarded_tile in client.player.ai.waiting:
                return False

        # it can be situation when we are in agari state
        # but our hand doesn't contain any yaku
        # in that case we can't call ron
        if not client.player.in_riichi:
            result = client.player.ai.estimate_hand_value_or_get_from_cache(
                win_tile // 4,
                is_tsumo=False,
                is_chankan=is_chankan,
            )
            if result.error:
                return False

        # bot decided to not call ron
        if not client.player.should_call_win(win_tile, False, shifted_enemy_seat, is_chankan):
            return False

        return True

    def call_riichi(self, client):
        client.player.in_riichi = True
        # -1000 we will deduct in the bot logic
        self.riichi_sticks += 1

        if len(client.player.discards) == 1 and not self.players_with_open_hands:
            client.is_daburi = True

        # we will set it to False after next draw
        # or called meld
        client.is_ippatsu = True

    def set_dealer(self, dealer):
        self.dealer = dealer
        self._unique_dealers += 1

        for x in range(0, len(self.clients)):
            client = self.clients[x]

            # each client think that he is a player with position = 0
            # so, we need to move dealer position for each client
            # and shift scores array
            client.player.dealer_seat = self._enemy_position(self.dealer, x)

        # first move should be dealer's move
        self.current_client_seat = dealer

    def process_the_end_of_the_round(self, tiles, win_tile, winner, loser, is_tsumo, is_chankan=False):
        """
        Increment a round number and do a scores calculations
        """

        if winner:
            return self.agari_result(winner, loser, is_tsumo, tiles, win_tile, is_chankan)
        else:
            return self.retake()

    def agari_result(self, winner, loser, is_tsumo, tiles, win_tile, is_chankan):
        logger.info(
            "{}: {} + {}".format(
                is_tsumo and "Tsumo" or "Ron",
                TilesConverter.to_one_line_string(tiles, print_aka_dora=True),
                TilesConverter.to_one_line_string([win_tile], print_aka_dora=True),
            ),
        )

        ura_dora = []
        number_of_dora_indicators = len(self.dora_indicators)
        # add one more dora for riichi win
        if winner.player.in_riichi:
            # 9 10 11 12 indices
            for x in range(number_of_dora_indicators):
                next_indicator_index = 9 + x
                ura_dora.append(self.dead_wall[next_indicator_index])

        is_tenhou = False
        # tenhou.net doesn't have renhou
        is_renhou = False
        is_chiihou = False

        if not self.players_with_open_hands and len(winner.player.discards) == 0 and is_tsumo:
            if winner.player.is_dealer:
                is_tenhou = True
            else:
                is_chiihou = True

        is_haitei = False
        is_houtei = False
        if not self.tiles:
            if is_tsumo:
                is_haitei = True
            else:
                is_houtei = True

        config = HandConfig(
            is_riichi=winner.player.in_riichi,
            player_wind=winner.player.player_wind,
            round_wind=winner.player.table.round_wind_tile,
            is_tsumo=is_tsumo,
            is_tenhou=is_tenhou,
            is_renhou=is_renhou,
            is_chiihou=is_chiihou,
            is_daburu_riichi=winner.is_daburi,
            is_ippatsu=winner.is_ippatsu,
            is_haitei=is_haitei,
            is_houtei=is_houtei,
            is_rinshan=winner.is_rinshan,
            is_chankan=is_chankan,
            options=OptionalRules(
                has_aka_dora=settings.FIVE_REDS,
                has_open_tanyao=settings.OPEN_TANYAO,
                has_double_yakuman=False,
            ),
        )

        hand_value = self.finished_hand.estimate_hand_value(
            tiles=tiles + [win_tile],
            win_tile=win_tile,
            melds=winner.player.melds,
            dora_indicators=self.dora_indicators + ura_dora,
            config=config,
        )

        if hand_value.error:
            logger.error(
                "Can't estimate a hand: {}. Error: {}".format(
                    TilesConverter.to_one_line_string(tiles + [win_tile], print_aka_dora=True), hand_value.error
                )
            )
            raise ValueError("Not correct hand")

        logger.info(
            "Dora indicators: {}".format(TilesConverter.to_one_line_string(self.dora_indicators, print_aka_dora=True))
        )
        logger.info("Hand yaku: {}".format(", ".join(str(x) for x in hand_value.yaku)))

        if loser is not None:
            loser_seat = loser.seat
        else:
            # tsumo
            loser_seat = winner.seat

        self.replay.win(
            winner.seat,
            loser_seat,
            win_tile,
            self.honba_sticks,
            self.riichi_sticks,
            hand_value.han,
            hand_value.fu,
            hand_value.cost,
            hand_value.yaku,
            self.dora_indicators,
            ura_dora,
        )

        riichi_bonus = self.riichi_sticks * 1000
        self.riichi_sticks = 0
        honba_bonus = self.honba_sticks * 300

        # win by ron
        if loser:
            scores_to_pay = hand_value.cost["main"] + honba_bonus
            win_amount = scores_to_pay + riichi_bonus
            winner.player.scores += win_amount
            loser.player.scores -= scores_to_pay

            logger.info("Win:  {0} +{1:,d} +{2:,d}".format(winner.player.name, scores_to_pay, riichi_bonus))
            logger.info("Lose: {0} -{1:,d}".format(loser.player.name, scores_to_pay))
        # win by tsumo
        else:
            calculated_cost = hand_value.cost["main"] + hand_value.cost["additional"] * 2
            win_amount = calculated_cost + riichi_bonus + honba_bonus
            winner.player.scores += win_amount

            logger.info(
                "Win:  {0} +{1:,d} +{2:,d}".format(winner.player.name, calculated_cost, riichi_bonus + honba_bonus)
            )

            for client in self.clients:
                if client != winner:
                    if client.player.is_dealer:
                        scores_to_pay = hand_value.cost["main"]
                    else:
                        scores_to_pay = hand_value.cost["additional"]
                    scores_to_pay += honba_bonus / 3

                    client.player.scores -= scores_to_pay
                    logger.info("Lose: {0} -{1:,d}".format(client.player.name, int(scores_to_pay)))

        return {"winner": winner, "loser": loser, "is_tsumo": is_tsumo, "is_abortive_retake": False}

    def retake(self):
        logger.info("Retake")
        tempai_users = []
        for client in self.clients:
            if client.player.in_tempai:
                tempai_users.append(client.seat)

        tempai_users_count = len(tempai_users)
        if tempai_users_count == 0 or tempai_users_count == 4:
            self.honba_sticks += 1
        else:
            # 1 tempai user  will get 3000
            # 2 tempai users will get 1500 each
            # 3 tempai users will get 1000 each
            scores_to_pay = 3000 / tempai_users_count
            for client in self.clients:
                if client.player.in_tempai:
                    client.player.scores += scores_to_pay
                    logger.info("{0} +{1:,d}".format(client.player.name, int(scores_to_pay)))

                    # dealer was tempai, we need to add honba stick
                    if client.player.is_dealer:
                        self.honba_sticks += 1
                else:
                    client.player.scores -= 3000 / (4 - tempai_users_count)

        self.replay.retake(tempai_users, self.honba_sticks, self.riichi_sticks)
        return {"winner": None, "loser": None, "is_tsumo": False, "is_abortive_retake": False}

    def abortive_retake(self, reason):
        logger.info("Abortive retake. Reason: {}".format(reason))
        self.replay.abortive_retake(reason, self.honba_sticks, self.riichi_sticks)
        return {"winner": None, "loser": None, "is_tsumo": False, "is_abortive_retake": True}

    def players_sorted_by_scores(self):
        return sorted([i.player for i in self.clients], key=lambda x: x.scores, reverse=True)

    def _check_same_winds(self):
        if not self._need_to_check_same_winds:
            return None

        # with called melds this abortive retake is not possible
        if self.players_with_open_hands:
            self._need_to_check_same_winds = False
            return None

        # it is possible only for the first 4 discards
        if len(self.discards) > 4:
            self._need_to_check_same_winds = False
            return None

        # it is too early
        if len(self.discards) != 4:
            return None

        tiles = [x // 4 for x in self.discards]
        unique_tiles = list(set(tiles))

        # first 4 discards wasn't same tiles
        if len(unique_tiles) != 1:
            self._need_to_check_same_winds = False
            return None

        tile = unique_tiles[1]
        if tile in WINDS:
            return self.abortive_retake(AbortiveDraw.SAME_FIRST_WIND)
        else:
            self._need_to_check_same_winds = False
            return None

    def _check_the_end_of_game(self, dealer_seat):
        dealer_has_higher_scores = True
        has_player_with_30000_plus_scores = False
        dealer = [x for x in self.clients if x.seat == dealer_seat][0]
        for client in self.clients:
            # if someone has negative scores at the end of round, we need to end the game
            if client.player.scores < 0:
                logger.info("Game end: negative scores")
                return True

            if client.player.scores >= 30000:
                has_player_with_30000_plus_scores = True

            if client.seat == dealer.seat:
                continue

            if client.player.scores > dealer.player.scores:
                dealer_has_higher_scores = False

        # orasu ended
        if self._unique_dealers == 8 and dealer_has_higher_scores:
            logger.info("Game end: dealer has higher scores at the end of south wind")
            return True

        # we have played all 8 winds (starting from wind 0)
        # and there is player with 30000+ scores
        if self._unique_dealers > 7 and has_player_with_30000_plus_scores:
            logger.info("Game end: 30000+ scores and the end of south wind")
            return True

        # west round was finished, we don't want to play north round
        if self._unique_dealers > 11:
            logger.info("Game end: the end of west wind")
            return True

        return False

    def _get_current_client(self) -> LocalClient:
        return self.clients[self.current_client_seat]

    def _cut_tiles(self, count_of_tiles) -> []:
        """
        Cut the tiles array
        :param count_of_tiles: how much tiles to cut
        :return: the array with specified count of tiles
        """

        result = self.tiles[0:count_of_tiles]
        self.tiles = self.tiles[count_of_tiles : len(self.tiles)]
        return result

    def _move_position(self, current_position, shift=1):
        """
        Loop 0 -> 1 -> 2 -> 3 -> 0
        """
        current_position += shift
        if current_position > 3:
            current_position = 0
        if current_position < 0:
            current_position = 3
        return current_position

    def _enemy_position(self, who, from_who):
        positions = [0, 1, 2, 3]
        return positions[who - from_who]

    def _generate_wall(self):
        # round of played numbers here to be sure that each wall will be unique
        wall_seed = shuffle_seed() + self.round_number

        # init seed for random generator
        seed(wall_seed)

        wall = [i for i in range(0, 136)]
        # let's shuffle wall two times just in case
        wall = self._randomly_shuffle_array(wall)
        wall = self._randomly_shuffle_array(wall)

        return wall

    def _randomly_shuffle_array(self, array):
        rand_seeds = [randint(0, len(array) - 1) for _ in range(0, len(array))]
        # for better wall shuffling we had to do it manually
        # shuffle() didn't make wall to be really random
        for x in range(0, len(array)):
            src = x
            dst = rand_seeds[x]

            swap = array[x]
            array[src] = array[dst]
            array[dst] = swap
        return array

    def add_new_dora_indicator(self):
        number_of_dora_indicators = len(self.dora_indicators)
        # 2 3 4 5 indices
        next_indicator_index = 2 + number_of_dora_indicators
        self.dora_indicators.append(self.dead_wall[next_indicator_index])

        if number_of_dora_indicators > 0:
            self.replay.add_new_dora(self.dora_indicators[-1])

        for _client in self.clients:
            _client.table.add_dora_indicator(self.dora_indicators[-1])

    def player_can_call_kyuushu_kyuuhai(self, player):
        if len(player.discards) > 0 or len(player.melds) > 0:
            return False
        tiles_34 = [x // 4 for x in player.tiles]
        terminals_and_honors = [x for x in tiles_34 if is_honor(x) or is_terminal(x)]
        return len(list(set(terminals_and_honors))) >= 9


# let's use tenhou constant values, to make things easier
class AbortiveDraw:
    NINE_DIFFERENT = "yao9"
    FOUR_RIICHI = "reach4"
    TRIPLE_RON = "ron3"
    FOUR_KANS = "kan4"
    SAME_FIRST_WIND = "kaze4"

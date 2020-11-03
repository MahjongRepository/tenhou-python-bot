import logging
import time
from collections import deque
from random import randint, random, seed, shuffle

from game.bots_battle.replays.tenhou import TenhouReplay
from game.client import Client
from mahjong.agari import Agari
from mahjong.constants import WINDS
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from utils.settings_handler import settings

settings.PRINT_LOGS = False
settings.FIVE_REDS = True
settings.OPEN_TANYAO = True

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

    def __init__(self, clients):
        self._need_to_check_same_winds = True
        self.tiles = []
        self.dead_wall = []
        self.dora_indicators = []
        self.discards = []
        self.clients = clients

        self.agari = Agari()
        self.finished_hand = HandCalculator()
        self.replay = TenhouReplay("", self.clients)

    def init_game(self):
        """
        Beginning of the game.
        Clients random placement and dealer selection.
        """

        replay_name = "{}.log".format(int(time.time()))
        logger.info("Replay name: {}".format(replay_name))
        self.replay = TenhouReplay(replay_name, self.clients)

        logger.info("Seed: {}".format(shuffle_seed()))
        logger.info("Aka dora: {}".format(settings.FIVE_REDS))
        logger.info("Open tanyao: {}".format(settings.FIVE_REDS))

        shuffle(self.clients, shuffle_seed)
        for i in range(0, len(self.clients)):
            self.clients[i].seat = i

        # oya should be always first player
        # to have compatibility with tenhou format
        self.set_dealer(0)

        for client in self.clients:
            client.player.scores = 25000

        self._unique_dealers = 1
        self.round_number = 0

    def init_round(self):
        """
        Generate players hands, dead wall and dora indicators
        """

        self.players_with_open_hands = []
        self.dora_indicators = []

        self.tiles = self._generate_wall()

        self.dead_wall = self._cut_tiles(14)
        self.dora_indicators.append(self.dead_wall[8])

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
            client.erase_state()

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
            self.dealer, self._unique_dealers - 1, self.honba_sticks, self.riichi_sticks, self.dora_indicators[0]
        )

    def play_round(self) -> []:
        continue_to_play = True

        while continue_to_play:
            current_client = self._get_current_client()
            in_tempai = current_client.player.in_tempai

            draw_tile = self._cut_tiles(1)[0]
            self.replay.draw(current_client.seat, draw_tile)

            # we don't need to add tile to the hand when we are in riichi
            if current_client.player.in_riichi:
                tiles = current_client.player.tiles + [draw_tile]
            else:
                current_client.player.draw_tile(draw_tile)
                tiles = current_client.player.tiles

            is_win = self.agari.is_agari(TilesConverter.to_34_array(tiles), current_client.player.meld_34_tiles)

            # win by tsumo after tile draw
            if is_win:
                tiles.remove(draw_tile)
                can_win = True

                # with open hand it can be situation when we in the tempai
                # but our hand doesn't contain any yaku
                # in that case we can't call ron
                if not current_client.player.in_riichi:
                    result = current_client.player.ai.estimate_hand_value_or_get_from_cache(
                        draw_tile // 4,
                        is_tsumo=True,
                    )
                    can_win = result.error is None

                if can_win:
                    result = self.process_the_end_of_the_round(
                        tiles=tiles, win_tile=draw_tile, winner=current_client, loser=None, is_tsumo=True
                    )
                    return [result]
                else:
                    # we can't win
                    # so let's add tile back to hand
                    # and discard it later
                    tiles.append(draw_tile)

            # we had to clear ippatsu, after tile draw
            current_client.is_ippatsu = False

            # if not in riichi, let's decide what tile to discard
            if not current_client.player.in_riichi:
                tile = current_client.player.discard_tile()
                in_tempai = current_client.player.in_tempai
            else:
                tile = draw_tile
                current_client.table.add_discarded_tile(0, tile, True)

            if in_tempai and current_client.player.can_call_riichi():
                who_called_riichi = current_client.seat
                for client in self.clients:
                    client.table.add_called_riichi(self._enemy_position(who_called_riichi, client.seat))
                self.replay.riichi(current_client.seat, 1)

            self.replay.discard(current_client.seat, tile)
            is_tsumogiri = draw_tile == tile
            result = self.check_clients_possible_ron(current_client, tile, is_tsumogiri)
            # the end of the round
            if result:
                # check_clients_possible_ron already returns array
                return result

            # if there is no challenger to ron, let's check can we call riichi with tile discard or not
            if in_tempai and current_client.player.can_call_riichi():
                self.call_riichi(current_client)
                self.replay.riichi(current_client.seat, 2)

                count_of_riichi_players = 0
                for client in self.clients:
                    if client.player.in_riichi:
                        count_of_riichi_players += 1

                if count_of_riichi_players == 4:
                    self.abortive_retake(self.FOUR_RIICHI)

            # abortive retake
            result = self._check_same_winds()
            if result:
                return [result]

            # let's check other players hand to possibility open sets
            possible_melds = []

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

                other_client.table.revealed_tiles[tile // 4] -= 1

                meld, discard_option = other_client.player.try_to_call_meld(tile, is_kamicha_discard)

                other_client.table.revealed_tiles[tile // 4] += 1

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
                logger.info("With hand: {}".format(current_client.player.format_hand_for_print(tile)))

                # we need to notify each client about called meld
                for _client in self.clients:
                    _client.table.add_called_meld(self._enemy_position(current_client.seat, _client.seat), meld)

                self.replay.open_meld(meld)
                current_client.player.tiles.append(tile)
                discarded_tile = current_client.player.discard_tile(discard_option)

                self.replay.discard(current_client.seat, discarded_tile)
                logger.info("Discard tile: {}".format(TilesConverter.to_one_line_string([discarded_tile])))

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

    def check_clients_possible_ron(self, current_client, tile, is_tsumogiri) -> []:
        """
        After tile discard let's check all other players can they win or not
        at this tile

        :param current_client:
        :param tile:
        :param is_tsumogiri:
        :return: None or ron result
        """
        possible_win_client = []
        for other_client in self.clients:
            # there is no need to check the current client
            if other_client == current_client:
                continue

            # let's store other players discards
            other_client.table.add_discarded_tile(
                self._enemy_position(current_client.seat, other_client.seat), tile, is_tsumogiri
            )

            if self.can_call_ron(other_client, tile):
                possible_win_client.append(other_client)

        if len(possible_win_client) == 3:
            return [self.abortive_retake(self.TRIPLE_RON)]

        # check multiple ron
        results = []
        for client in possible_win_client:
            result = self.process_the_end_of_the_round(
                tiles=client.player.tiles, win_tile=tile, winner=client, loser=current_client, is_tsumo=False
            )
            results.append(result)

        return results

    def play_game(self, total_results):
        """
        :param total_results: a dictionary with keys as client ids
        :return: game results
        """
        logger.info("The start of the game")
        logger.info("")

        is_game_end = False
        self.init_game()
        self.replay.init_game(shuffle_seed())

        played_rounds = 0

        while not is_game_end:
            self.init_round()
            result = self.play_round()

            for item in result:
                is_game_end = item["is_game_end"]
                loser = item["loser"]
                winner = item["winner"]
                if loser:
                    total_results[loser.id]["lose_rounds"] += 1
                if winner:
                    total_results[winner.id]["win_rounds"] += 1

            for client in self.clients:
                if client.player.in_riichi:
                    total_results[client.id]["riichi_rounds"] += 1

                called_melds = [x for x in self.players_with_open_hands if x == client.seat]
                if called_melds:
                    total_results[client.id]["called_rounds"] += 1

            played_rounds += 1

        self.recalculate_players_position()
        self.replay.end_game()

        logger.info("Final Scores: {0}".format(self.players_sorted_by_scores()))
        logger.info("The end of the game")

        return {"played_rounds": played_rounds}

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

    def can_call_ron(self, client, win_tile):
        if not client.player.in_tempai:
            return False

        # check for furiten
        for item in client.player.discards:
            discarded_tile = item.value // 4
            if discarded_tile in client.player.ai.waiting:
                return False

        tiles = client.player.tiles
        is_agari = self.agari.is_agari(TilesConverter.to_34_array(tiles + [win_tile]), client.player.meld_34_tiles)
        if not is_agari:
            return False

        # it can be situation when we are in agari state
        # but our hand doesn't contain any yaku
        # in that case we can't call ron
        if not client.player.in_riichi:
            result = client.player.ai.estimate_hand_value_or_get_from_cache(
                win_tile // 4,
                is_tsumo=False,
            )
            return result.error is None

        return True

    def call_riichi(self, client):
        client.player.in_riichi = True
        client.player.scores -= 1000
        self.riichi_sticks += 1

        if len(client.player.discards) == 1 and not self.players_with_open_hands:
            client.is_daburi = True

        # we will set it to False after next draw
        # or called meld
        client.is_ippatsu = True

        who_called_riichi = client.seat
        logger.info("Riichi: {0} -1,000".format(self.clients[who_called_riichi].player.name))
        logger.info(
            "With hand: {}".format(
                TilesConverter.to_one_line_string(self.clients[who_called_riichi].player.closed_hand)
            )
        )

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

    def process_the_end_of_the_round(self, tiles, win_tile, winner, loser, is_tsumo):
        """
        Increment a round number and do a scores calculations
        """
        count_of_tiles = len(tiles)
        # retake or win
        if count_of_tiles and count_of_tiles != 13:
            raise ValueError("Wrong tiles count: {}".format(len(tiles)))

        if winner:
            logger.info(
                "{}: {} + {}".format(
                    is_tsumo and "Tsumo" or "Ron",
                    TilesConverter.to_one_line_string(tiles),
                    TilesConverter.to_one_line_string([win_tile]),
                ),
            )
        else:
            logger.info("Retake")

        self.round_number += 1

        if winner:
            ura_dora = []
            # add one more dora for riichi win
            if winner.player.in_riichi:
                ura_dora.append(self.dead_wall[9])

            is_tenhou = False
            is_renhou = False
            is_chiihou = False
            # win on the first draw\discard
            # we can win after daburi riichi in that case we will have one tile in discard
            # that's why we have < 2 condition (not == 0)
            if not self.players_with_open_hands and len(winner.player.discards) < 2:
                if is_tsumo:
                    if winner.player.is_dealer:
                        is_tenhou = True
                    else:
                        is_chiihou = True
                else:
                    is_renhou = True

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
                options=OptionalRules(
                    has_aka_dora=True,
                    has_open_tanyao=True,
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
                        TilesConverter.to_one_line_string(tiles + [win_tile]), hand_value.error
                    )
                )
                raise ValueError("Not correct hand")

            logger.info("Dora indicators: {}".format(TilesConverter.to_one_line_string(self.dora_indicators)))
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

            # if dealer won we need to increment honba sticks
            if winner.player.is_dealer:
                self.honba_sticks += 1
            else:
                self.honba_sticks = 0
                new_dealer = self._move_position(self.dealer)
                self.set_dealer(new_dealer)

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

        # retake
        else:
            tempai_users = []

            dealer_was_tempai = False
            for client in self.clients:
                if client.player.in_tempai:
                    tempai_users.append(client.seat)

                    if client.player.is_dealer:
                        dealer_was_tempai = True

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

            # dealer not in tempai, so round should move
            if not dealer_was_tempai:
                new_dealer = self._move_position(self.dealer)
                self.set_dealer(new_dealer)

                # someone was in tempai, we need to add honba here
                if tempai_users_count != 0 and tempai_users_count != 4:
                    self.honba_sticks += 1

            self.replay.retake(tempai_users, self.honba_sticks, self.riichi_sticks)

        is_game_end = self._check_the_end_of_game()
        logger.info("")

        return {
            "winner": winner,
            "loser": loser,
            "is_tsumo": is_tsumo,
            "is_game_end": is_game_end,
        }

    def abortive_retake(self, reason):
        logger.info("Abortive retake. Reason: {}".format(reason))

        self.honba_sticks += 1
        is_game_end = self._check_the_end_of_game()

        self.replay.abortive_retake(reason, self.honba_sticks, self.riichi_sticks)

        return {
            "winner": None,
            "loser": None,
            "is_tsumo": False,
            "is_game_end": is_game_end,
        }

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
            return self.abortive_retake(self.SAME_FIRST_WIND)
        else:
            self._need_to_check_same_winds = False
            return None

    def _check_the_end_of_game(self):
        is_game_end = False

        # if someone has negative scores,
        # we need to end the game
        for client in self.clients:
            if client.player.scores < 0:
                is_game_end = True

        # we have played all 8 winds, let's finish the game
        if self._unique_dealers > 8:
            is_game_end = True

        return is_game_end

    def _get_current_client(self) -> Client:
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

    def _move_position(self, current_position):
        """
        Loop 0 -> 1 -> 2 -> 3 -> 0
        """
        current_position += 1
        if current_position > 3:
            current_position = 0
        return current_position

    def _enemy_position(self, who, from_who):
        positions = [0, 1, 2, 3]
        return positions[who - from_who]

    def _generate_wall(self):
        wall_seed = shuffle_seed() + self.round_number
        # init seed for random generator
        seed(wall_seed)

        def shuffle_wall(rand_seeds):
            # for better wall shuffling we had to do it manually
            # shuffle() didn't make wall to be really random
            for x in range(0, 136):
                src = x
                dst = rand_seeds[x]

                swap = wall[x]
                wall[src] = wall[dst]
                wall[dst] = swap

        wall = [i for i in range(0, 136)]
        rand_one = [randint(0, 135) for _ in range(0, 136)]
        rand_two = [randint(0, 135) for _ in range(0, 136)]

        # let's shuffle wall two times just in case
        shuffle_wall(rand_one)
        shuffle_wall(rand_two)

        return wall

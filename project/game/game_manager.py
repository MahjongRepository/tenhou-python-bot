# -*- coding: utf-8 -*-
import logging
from collections import deque
from random import randint, shuffle, random, seed

from game.logger import set_up_logging
from game.replays.tenhou import TenhouReplay as Replay
from mahjong.ai.agari import Agari
from mahjong.client import Client
from mahjong.hand import FinishedHand
from mahjong.meld import Meld
from mahjong.tile import TilesConverter
from utils.settings_handler import settings

settings.FIVE_REDS = True

# we need to have it
# to be able repeat our tests with needed random
seed_value = random()

set_up_logging()
logger = logging.getLogger('game')


def shuffle_seed():
    return seed_value


class GameManager(object):
    """
    Allow to play bots between each other
    To have a metrics how new version plays against old versions
    """

    tiles = []
    dead_wall = []
    clients = []
    dora_indicators = []
    players_with_open_hands = []

    dealer = None
    current_client_seat = None
    round_number = 0
    honba_sticks = 0
    riichi_sticks = 0

    _unique_dealers = 0

    def __init__(self, clients):

        self.tiles = []
        self.dead_wall = []
        self.dora_indicators = []
        self.clients = clients
        self._set_client_names()

        self.agari = Agari()
        self.finished_hand = FinishedHand()
        self.replay = Replay(self.clients)

    def init_game(self):
        """
        Beginning of the game.
        Clients random placement and dealer selection.
        """

        logger.info('Seed: {}'.format(shuffle_seed()))

        shuffle(self.clients, shuffle_seed)
        for i in range(0, len(self.clients)):
            self.clients[i].seat = i

        # oya should be always first player
        # to have compatibility with tenhou format
        self.set_dealer(0)

        for client in self.clients:
            client.player.scores = 25000

        self._unique_dealers = 1

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
                player_scores
            )

        # each player by rotation draw 4 tiles until they have 12
        # after this each player draw one more tile
        # and this is will be their initial hand
        # we do it to make the tiles allocation in hands
        # more random
        for x in range(0, 3):
            for client in self.clients:
                client.player.tiles += self._cut_tiles(4)

        for client in self.clients:
            client.player.tiles += self._cut_tiles(1)
            client.player.tiles = sorted(client.player.tiles)
            client.init_hand(client.player.tiles)

        logger.info('Round number: {}'.format(self.round_number))
        logger.info('Dealer: {}, {}'.format(self.dealer, self.clients[self.dealer].player.name))
        logger.info('Wind: {}. Riichi sticks: {}. Honba sticks: {}'.format(
            self._unique_dealers,
            self.riichi_sticks,
            self.honba_sticks
        ))
        logger.info('Players: {0}'.format(self.players_sorted_by_scores()))

        self.replay.init_round(self.dealer,
                               self._unique_dealers - 1,
                               self.honba_sticks,
                               self.riichi_sticks,
                               self.dora_indicators[0])

    def play_round(self):
        continue_to_play = True

        while continue_to_play:
            current_client = self._get_current_client()
            in_tempai = current_client.player.in_tempai

            tile = self._cut_tiles(1)[0]
            self.replay.draw(current_client.seat, tile)

            # we don't need to add tile to the hand when we are in riichi
            if current_client.player.in_riichi:
                tiles = current_client.player.tiles + [tile]
            else:
                current_client.draw_tile(tile)
                tiles = current_client.player.tiles

            is_win = self.agari.is_agari(TilesConverter.to_34_array(tiles), current_client.player.meld_tiles)

            # win by tsumo after tile draw
            if is_win:
                tiles.remove(tile)
                can_win = True

                # with open hand it can be situation when we in the tempai
                # but our hand doesn't contain any yaku
                # in that case we can't call ron
                if not current_client.player.in_riichi:
                    result = self.finished_hand.estimate_hand_value(tiles=tiles + [tile],
                                                                    win_tile=tile,
                                                                    is_tsumo=True,
                                                                    is_riichi=False,
                                                                    open_sets=current_client.player.meld_tiles,
                                                                    dora_indicators=self.dora_indicators,
                                                                    player_wind=current_client.player.player_wind,
                                                                    round_wind=current_client.player.table.round_wind)
                    can_win = result['error'] is None

                if can_win:
                    result = self.process_the_end_of_the_round(tiles=tiles,
                                                               win_tile=tile,
                                                               winner=current_client,
                                                               loser=None,
                                                               is_tsumo=True)
                    return result
                else:
                    # we can't win
                    # so let's add tile back to hand
                    # and discard it later
                    tiles.append(tile)

            # we had to clear ippatsu, after tile draw
            current_client.player._is_ippatsu = False

            # if not in riichi, let's decide what tile to discard
            if not current_client.player.in_riichi:
                tile = current_client.discard_tile()
                in_tempai = current_client.player.in_tempai

            if in_tempai and current_client.player.can_call_riichi():
                self.replay.riichi(current_client.seat, 1)

            self.replay.discard(current_client.seat, tile)
            result = self.check_clients_possible_ron(current_client, tile)
            # the end of the round
            if result:
                return result

            # if there is no challenger to ron, let's check can we call riichi with tile discard or not
            if in_tempai and current_client.player.can_call_riichi():
                self.call_riichi(current_client)
                self.replay.riichi(current_client.seat, 2)

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

                meld, discarded_tile, shanten = other_client.player.try_to_call_meld(tile, is_kamicha_discard)

                if meld:
                    meld.from_who = current_client.seat
                    meld.who = other_client.seat
                    meld.called_tile = tile
                    possible_melds.append({
                        'meld': meld,
                        'discarded_tile': discarded_tile,
                        'shanten': shanten
                    })

            if possible_melds:
                # pon is more important than chi
                possible_melds = sorted(possible_melds, key=lambda x: x['meld'].type == Meld.PON)
                tile_to_discard = possible_melds[0]['discarded_tile']
                meld = possible_melds[0]['meld']
                shanten = possible_melds[0]['shanten']

                # clear ippatsu after called meld
                for client_item in self.clients:
                    client_item.player._is_ippatsu = False

                # we changed current client with called open set
                self.current_client_seat = meld.who
                current_client = self._get_current_client()
                self.players_with_open_hands.append(self.current_client_seat)

                logger.info('Called meld: {} by {}'.format(meld, current_client.player.name))
                hand_string = 'With hand: {} + {}'.format(
                    TilesConverter.to_one_line_string(current_client.player.closed_hand),
                    TilesConverter.to_one_line_string([tile])
                )
                if current_client.player.is_open_hand:
                    melds = []
                    for item in current_client.player.melds:
                        melds.append('{}'.format(TilesConverter.to_one_line_string(item.tiles)))
                    hand_string += ' [{}]'.format(', '.join(melds))
                logger.info(hand_string)

                # we need to notify each client about called meld
                for _client in self.clients:
                    _client.table.add_called_meld(meld, self._enemy_position(current_client.seat, _client.seat))

                current_client.player.tiles.append(tile)
                current_client.player.ai.previous_shanten = shanten

                if shanten == 0:
                    current_client.player.in_tempai = True

                self.replay.open_meld(meld)

                # we need to double validate that we are doing fine
                if tile_to_discard not in current_client.player.closed_hand:
                    raise ValueError("We can't discard a tile from the opened part of the hand")

                current_client.discard_tile(tile_to_discard)
                self.replay.discard(current_client.seat, tile_to_discard)
                logger.info('Discard tile: {}'.format(TilesConverter.to_one_line_string([tile_to_discard])))

                # the end of the round
                result = self.check_clients_possible_ron(current_client, tile_to_discard)
                if result:
                    return result

            self.current_client_seat = self._move_position(self.current_client_seat)

            # retake
            if not len(self.tiles):
                continue_to_play = False

        result = self.process_the_end_of_the_round([], 0, None, None, False)
        return result

    def check_clients_possible_ron(self, current_client, tile):
        """
        After tile discard let's check all other players can they win or not
        at this tile
        :param current_client:
        :param tile:
        :return: None or ron result
        """
        for other_client in self.clients:
            # there is no need to check the current client
            if other_client == current_client:
                continue

            # let's store other players discards
            other_client.table.enemy_discard(tile, self._enemy_position(current_client.seat, other_client.seat))

            # TODO support multiple ron
            if self.can_call_ron(other_client, tile):
                # the end of the round
                result = self.process_the_end_of_the_round(tiles=other_client.player.tiles,
                                                           win_tile=tile,
                                                           winner=other_client,
                                                           loser=current_client,
                                                           is_tsumo=False)
                return result

        return None

    def play_game(self, total_results):
        """
        :param total_results: a dictionary with keys as client ids
        :return: game results
        """
        logger.info('The start of the game')
        logger.info('')

        is_game_end = False
        self.init_game()
        self.replay.init_game()

        played_rounds = 0

        while not is_game_end:
            self.init_round()
            result = self.play_round()

            is_game_end = result['is_game_end']
            loser = result['loser']
            winner = result['winner']
            if loser:
                total_results[loser.id]['lose_rounds'] += 1
            if winner:
                total_results[winner.id]['win_rounds'] += 1

            for client in self.clients:
                if client.player.in_riichi:
                    total_results[client.id]['riichi_rounds'] += 1

                called_melds = [x for x in self.players_with_open_hands if x == client.seat]
                if called_melds:
                    total_results[client.id]['called_rounds'] += 1

            played_rounds += 1

        self.recalculate_players_position()
        self.replay.end_game()

        logger.info('Final Scores: {0}'.format(self.players_sorted_by_scores()))
        logger.info('The end of the game')

        return {'played_rounds': played_rounds}

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

        tiles = client.player.tiles

        # with open hand it can be situation when we in the tempai
        # but our hand doesn't contain any yaku
        # in that case we can't call ron
        if not client.player.in_riichi:
            result = self.finished_hand.estimate_hand_value(tiles=tiles + [win_tile],
                                                            win_tile=win_tile,
                                                            is_tsumo=False,
                                                            is_riichi=False,
                                                            open_sets=client.player.meld_tiles,
                                                            dora_indicators=self.dora_indicators,
                                                            player_wind=client.player.player_wind,
                                                            round_wind=client.player.table.round_wind)
            return result['error'] is None

        is_ron = self.agari.is_agari(TilesConverter.to_34_array(tiles + [win_tile]), client.player.meld_tiles)
        return is_ron

    def call_riichi(self, client):
        client.player.in_riichi = True
        client.player.scores -= 1000
        self.riichi_sticks += 1

        if len(client.player.discards) == 1:
            client.player._is_daburi = True
        # we will set it to False after next draw
        # or called meld
        client.player._is_ippatsu = True

        who_called_riichi = client.seat
        for client in self.clients:
            client.enemy_riichi(self._enemy_position(who_called_riichi, client.seat))

        logger.info('Riichi: {0} -1,000'.format(self.clients[who_called_riichi].player.name))
        logger.info('With hand: {}'.format(
            TilesConverter.to_one_line_string(self.clients[who_called_riichi].player.closed_hand)
        ))

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
            raise ValueError('Wrong tiles count: {}'.format(len(tiles)))

        if winner:
            logger.info('{}: {} + {}'.format(
                is_tsumo and 'Tsumo' or 'Ron',
                TilesConverter.to_one_line_string(tiles),
                TilesConverter.to_one_line_string([win_tile])),
            )
        else:
            logger.info('Retake')

        is_game_end = False
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

            hand_value = self.finished_hand.estimate_hand_value(tiles=tiles + [win_tile],
                                                                win_tile=win_tile,
                                                                is_tsumo=is_tsumo,
                                                                is_riichi=winner.player.in_riichi,
                                                                is_dealer=winner.player.is_dealer,
                                                                open_sets=winner.player.meld_tiles,
                                                                dora_indicators=self.dora_indicators + ura_dora,
                                                                player_wind=winner.player.player_wind,
                                                                round_wind=winner.player.table.round_wind,
                                                                is_tenhou=is_tenhou,
                                                                is_renhou=is_renhou,
                                                                is_chiihou=is_chiihou,
                                                                is_daburu_riichi=winner.player._is_daburi,
                                                                is_ippatsu=winner.player._is_ippatsu,
                                                                is_haitei=is_haitei,
                                                                is_houtei=is_houtei)

            if hand_value['error']:
                logger.error("Can't estimate a hand: {}. Error: {}".format(
                    TilesConverter.to_one_line_string(tiles + [win_tile]),
                    hand_value['error']
                ))
                raise ValueError('Not correct hand')

            logger.info('Dora indicators: {}'.format(TilesConverter.to_one_line_string(self.dora_indicators)))
            logger.info('Hand yaku: {}'.format(', '.join(str(x) for x in hand_value['hand_yaku'])))

            if loser is not None:
                loser_seat = loser.seat
            else:
                # tsumo
                loser_seat = winner.seat

            self.replay.win(winner.seat,
                            loser_seat,
                            win_tile,
                            self.honba_sticks,
                            self.riichi_sticks,
                            hand_value['han'],
                            hand_value['fu'],
                            hand_value['cost'],
                            hand_value['hand_yaku'],
                            self.dora_indicators,
                            ura_dora)

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
                scores_to_pay = hand_value['cost']['main'] + honba_bonus
                win_amount = scores_to_pay + riichi_bonus
                winner.player.scores += win_amount
                loser.player.scores -= scores_to_pay

                logger.info('Win:  {0} +{1:,d} +{2:,d}'.format(winner.player.name, scores_to_pay, riichi_bonus))
                logger.info('Lose: {0} -{1:,d}'.format(loser.player.name, scores_to_pay))
            # win by tsumo
            else:
                calculated_cost = hand_value['cost']['main'] + hand_value['cost']['additional'] * 2
                win_amount = calculated_cost + riichi_bonus + honba_bonus
                winner.player.scores += win_amount

                logger.info('Win:  {0} +{1:,d} +{2:,d}'.format(winner.player.name, calculated_cost,
                                                               riichi_bonus + honba_bonus))

                for client in self.clients:
                    if client != winner:
                        if client.player.is_dealer:
                            scores_to_pay = hand_value['cost']['main']
                        else:
                            scores_to_pay = hand_value['cost']['additional']
                        scores_to_pay += (honba_bonus / 3)

                        client.player.scores -= scores_to_pay
                        logger.info('Lose: {0} -{1:,d}'.format(client.player.name, int(scores_to_pay)))

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
                        logger.info('{0} +{1:,d}'.format(client.player.name, int(scores_to_pay)))

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

        # if someone has negative scores,
        # we need to end the game
        for client in self.clients:
            if client.player.scores < 0:
                is_game_end = True

        # we have played all 8 winds, let's finish the game
        if self._unique_dealers > 8:
            is_game_end = True

        logger.info('')

        return {
            'winner': winner,
            'loser': loser,
            'is_tsumo': is_tsumo,
            'is_game_end': is_game_end,
            'players_with_open_hands': self.players_with_open_hands
        }

    def players_sorted_by_scores(self):
        return sorted([i.player for i in self.clients], key=lambda x: x.scores, reverse=True)

    def _set_client_names(self):
        """
        For better tests output
        """
        names = ['Sato', 'Suzuki', 'Takahashi', 'Tanaka', 'Watanabe', 'Ito',
                 'Yamamoto', 'Nakamura', 'Kobayashi', 'Kato', 'Yoshida', 'Yamada']

        for client in self.clients:
            name = names[randint(0, len(names) - 1)]
            names.remove(name)

            client.player.name = name

    def _get_current_client(self) -> Client:
        return self.clients[self.current_client_seat]

    def _cut_tiles(self, count_of_tiles) -> []:
        """
        Cut the tiles array
        :param count_of_tiles: how much tiles to cut
        :return: the array with specified count of tiles
        """

        result = self.tiles[0:count_of_tiles]
        self.tiles = self.tiles[count_of_tiles:len(self.tiles)]
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
        seed(shuffle_seed() + self.round_number)

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
        rand_one = [randint(0, 135) for i in range(0, 136)]
        rand_two = [randint(0, 135) for i in range(0, 136)]

        # let's shuffle wall two times just in case
        shuffle_wall(rand_one)
        shuffle_wall(rand_two)

        return wall

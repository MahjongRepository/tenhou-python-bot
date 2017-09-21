# -*- coding: utf-8 -*-
import unittest

from mahjong.constants import EAST, WEST
from mahjong.meld import Meld
from mahjong.tests_mixin import TestMixin

from game.table import Table


class DefenceTestCase(unittest.TestCase, TestMixin):

    def test_add_safe_tile_after_discard(self):
        table = Table()
        table.add_called_riichi(3)

        table.add_discarded_tile(1, self._string_to_136_tile(man='3'), False)
        table.add_discarded_tile(0, self._string_to_136_tile(man='4'), False)

        self.assertEqual(len(table.get_player(1).discards), 1)
        self.assertEqual(len(table.get_player(2).discards), 0)
        self.assertEqual(len(table.get_player(3).discards), 0)

        self.assertEqual(len(table.get_player(1).safe_tiles), 1)
        self.assertEqual(len(table.get_player(2).safe_tiles), 0)
        self.assertEqual(len(table.get_player(3).safe_tiles), 2)

        # "2" is 3 man
        self.assertEqual(table.get_player(1).safe_tiles, [2])
        self.assertEqual(table.get_player(3).safe_tiles, [2, 3])

    def test_temporary_safe_tiles(self):
        table = Table()

        table.add_discarded_tile(1, self._string_to_136_tile(man='4'), False)

        self.assertEqual(table.get_player(1).temporary_safe_tiles, [])
        self.assertEqual(table.get_player(2).temporary_safe_tiles, [3])
        self.assertEqual(table.get_player(3).temporary_safe_tiles, [3])

        table.add_discarded_tile(2, self._string_to_136_tile(man='5'), False)

        self.assertEqual(table.get_player(1).temporary_safe_tiles, [4])
        self.assertEqual(table.get_player(2).temporary_safe_tiles, [])
        self.assertEqual(table.get_player(3).temporary_safe_tiles, [3, 4])

        table.add_discarded_tile(3, self._string_to_136_tile(man='6'), False)

        self.assertEqual(table.get_player(1).temporary_safe_tiles, [4, 5])
        self.assertEqual(table.get_player(2).temporary_safe_tiles, [5])
        self.assertEqual(table.get_player(3).temporary_safe_tiles, [])

        table.add_discarded_tile(1, self._string_to_136_tile(man='7'), False)

        self.assertEqual(table.get_player(1).temporary_safe_tiles, [])
        self.assertEqual(table.get_player(2).temporary_safe_tiles, [5, 6])
        self.assertEqual(table.get_player(3).temporary_safe_tiles, [6])

    def test_should_go_for_defence_and_bad_hand(self):
        """
        When we have 13 tiles in hand and someone declared a riichi
        """
        table = Table()

        tiles = self._string_to_136_array(sou='1259', pin='12348', honors='3456')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(man='6'))
        # discard here to reinit shanten number in AI
        table.player.discard_tile()

        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), False)

        table.add_called_riichi(3)

        # our hand is pretty bad, there is no sense to push it against riichi
        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), True)

    def test_should_go_for_defence_and_good_hand(self):
        """
        When we have 13 tiles in hand and someone declared a riichi
        """
        table = Table()

        tiles = self._string_to_136_array(sou='234678', pin='34789', man='77')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(man='6'))
        # discard here to reinit shanten number in AI
        table.player.discard_tile()

        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), False)

        table.add_called_riichi(3)

        # our hand is in tempai, but it is really cheap
        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), True)

        table.add_dora_indicator(self._string_to_136_tile(man='4'))
        table.add_dora_indicator(self._string_to_136_tile(pin='3'))

        # our hand in tempai, and it has a cost, so let's push it
        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), False)

    def test_call_riichi_with_good_wait_against_other_player_riichi(self):
        table = Table()
        table.has_aka_dora = True
        table.count_of_remaining_tiles = 60
        table.player.scores = 25000

        tiles = self._string_to_136_array(sou='123789', pin='23467', man='55')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(man='9'))

        table.add_called_riichi(3)

        discard = table.player.discard_tile()
        self.assertEqual(self._to_string([discard]), '9m')
        self.assertEqual(table.player.ai.in_defence, False)
        self.assertEqual(table.player.can_call_riichi(), True)

    def test_call_riichi_with_bad_wait_against_other_player_riichi(self):
        table = Table()
        table.count_of_remaining_tiles = 60
        table.player.scores = 25000

        tiles = self._string_to_136_array(sou='11223', pin='234678', man='55')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(man='9'))

        table.add_called_riichi(3)

        discard = table.player.discard_tile()
        self.assertEqual(self._to_string([discard]), '9m')
        self.assertEqual(table.player.ai.in_defence, True)
        self.assertEqual(table.player.can_call_riichi(), False)

    def test_should_go_for_defence_and_good_hand_with_drawn_tile(self):
        """
        When we have 14 tiles in hand and someone declared a riichi
        """
        table = Table()
        table.has_aka_dora = True

        tiles = self._string_to_136_array(sou='2223457899', honors='666')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(man='8'))
        table.player.add_called_meld(self._make_meld(Meld.PON, sou='222'))
        table.player.add_called_meld(self._make_meld(Meld.PON, honors='666'))

        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(), False)

        table.add_called_riichi(3)

        results, shanten = table.player.ai.calculate_outs(table.player.tiles,
                                                          table.player.closed_hand,
                                                          table.player.open_hand_34_tiles)
        selected_tile = table.player.ai.process_discard_options_and_select_tile_to_discard(results, shanten)

        self.assertEqual(table.player.ai.defence.should_go_to_defence_mode(selected_tile), False)
        result = table.player.discard_tile()
        self.assertEqual(self._to_string([result]), '8m')

    def test_find_common_safe_tile_to_discard(self):
        table = Table()

        tiles = self._string_to_136_array(sou='2456', pin='234478', man='2336')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(sou='6'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='5'), False)

        table.add_discarded_tile(2, self._string_to_136_tile(pin='5'), False)
        table.add_discarded_tile(2, self._string_to_136_tile(sou='6'), False)

        table.add_called_riichi(1)
        table.add_called_riichi(2)

        # for this test we don't need temporary_safe_tiles
        table.get_player(1).temporary_safe_tiles = []
        table.get_player(2).temporary_safe_tiles = []

        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '6s')

    def test_find_dealer_tile_to_discard(self):
        dealer = 2
        dora = self._string_to_136_tile(honors='3')
        table = Table()
        table.init_round(0, 0, 0, dora, dealer, [])

        tiles = self._string_to_136_array(sou='2234678', pin='34', man='45789')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(man='4'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='5'), False)

        table.add_discarded_tile(2, self._string_to_136_tile(man='8'), False)
        table.add_discarded_tile(2, self._string_to_136_tile(man='9'), False)

        table.add_called_riichi(1)
        table.add_called_riichi(2)

        # for this test we don't need temporary_safe_tiles
        table.get_player(1).temporary_safe_tiles = []
        table.get_player(2).temporary_safe_tiles = []

        result = table.player.discard_tile()
        # second player is a dealer, let's fold against him
        self.assertEqual(self._to_string([result]), '9m')

        tiles = self._string_to_136_array(sou='234567', pin='348', man='234', honors='23')
        table.player.init_hand(tiles)

        result = table.player.discard_tile()
        # there is no safe tiles against dealer, so let's fold against other players
        self.assertEqual(table.player.ai.in_defence, True)
        self.assertEqual(self._to_string([result]), '4m')

    def test_try_to_discard_not_needed_tiles_first_in_defence_mode(self):
        table = Table()

        tiles = self._string_to_136_array(sou='2345678', pin='789', man='55', honors='12')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(man='5'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(honors='1'), False)

        table.add_called_riichi(1)

        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '1z')

    def test_try_to_discard_less_valuable_tiles_first_in_defence_mode(self):
        table = Table()

        tiles = self._string_to_136_array(sou='234678', pin='6789', man='55', honors='13')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(pin='7'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(sou='2'), False)

        table.add_called_riichi(1)

        result = table.player.discard_tile()

        # discard of 2s will do less damage to our hand shape than 7p discard
        self.assertEqual(table.player.ai.in_defence, True)
        self.assertEqual(self._to_string([result]), '2s')

    def test_find_impossible_waits_and_honor_tiles(self):
        table = Table()

        tiles = self._string_to_136_array(honors='1133')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(honors='1'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(honors='3'), False)

        table.add_called_riichi(2)

        table.player.ai.defence.hand_34 = self._to_34_array(table.player.tiles)
        table.player.ai.defence.closed_hand_34 = self._to_34_array(table.player.closed_hand)
        result = table.player.ai.defence.impossible_wait.find_tiles_to_discard([])

        # dora is not safe against tanki wait, so let's hold it
        self.assertEqual([x.value for x in result], [EAST, WEST])

    def test_find_impossible_waits_and_kabe_technique(self):
        table = Table()
        tiles = self._string_to_136_array(pin='11122777799')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(pin='2'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='2'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='9'), False)

        table.add_called_riichi(2)

        table.player.ai.defence.hand_34 = self._to_34_array(table.player.tiles)
        table.player.ai.defence.closed_hand_34 = self._to_34_array(table.player.closed_hand)
        result = table.player.ai.defence.kabe.find_tiles_to_discard([])

        self.assertEqual(self._to_string([x.value * 4 for x in result]), '19p')

        table = Table()
        tiles = self._string_to_136_array(pin='33337777')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(pin='5'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='5'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='5'), False)

        table.add_called_riichi(2)

        table.player.ai.defence.hand_34 = self._to_34_array(table.player.tiles)
        table.player.ai.defence.closed_hand_34 = self._to_34_array(table.player.closed_hand)
        result = table.player.ai.defence.kabe.find_tiles_to_discard([])

        self.assertEqual(self._to_string([x.value * 4 for x in result]), '5p')

        table = Table()
        tiles = self._string_to_136_array(pin='33334446666')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(pin='5'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='5'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='5'), False)

        table.add_called_riichi(2)

        table.player.ai.defence.hand_34 = self._to_34_array(table.player.tiles)
        table.player.ai.defence.closed_hand_34 = self._to_34_array(table.player.closed_hand)
        result = table.player.ai.defence.kabe.find_tiles_to_discard([])

        self.assertEqual(self._to_string([x.value * 4 for x in result]), '45p')

    def test_find_common_suji_tiles_to_discard_for_multiple_players(self):
        table = Table()

        tiles = self._string_to_136_array(sou='2345678', pin='12789', man='55')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(pin='4'), False)
        table.add_discarded_tile(2, self._string_to_136_tile(pin='4'), False)

        table.add_called_riichi(1)
        table.add_called_riichi(2)

        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '1p')

    def test_find_suji_tiles_to_discard_for_one_player(self):
        table = Table()

        tiles = self._string_to_136_array(sou='2345678', pin='12789', man='55')
        table.player.init_hand(tiles)

        table.add_discarded_tile(1, self._string_to_136_tile(man='2'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='8'), False)

        table.add_called_riichi(1)

        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '5m')

    def test_dont_discard_safe_tiles_when_call_riichi(self):
        table = Table()
        table.count_of_remaining_tiles = 70
        table.player.scores = 2000

        tiles = self._string_to_136_array(sou='12356789', pin='22678')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(honors='1'))
        table.player.discard_tile()
        table.player.draw_tile(self._string_to_136_tile(honors='1'))

        table.add_discarded_tile(1, self._string_to_136_tile(sou='1'), False)
        table.add_called_riichi(1)

        result = table.player.discard_tile()

        self.assertEqual(table.player.can_call_riichi(), True)
        self.assertEqual(self._to_string([result]), '1z')

    def test_mark_dora_as_dangerous_tile_for_suji(self):
        table = Table()
        table.add_dora_indicator(self._string_to_136_tile(man='8'))

        tiles = self._string_to_136_array(man='112235', pin='4557788')
        table.player.init_hand(tiles)
        # 9 man is dora!
        table.player.draw_tile(self._string_to_136_tile(man='9'))

        table.add_discarded_tile(1, self._string_to_136_tile(man='6'), False)
        table.add_called_riichi(1)

        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '3m')

    def test_priority_of_players_safe_tiles(self):
        table = Table()

        tiles = self._string_to_136_array(man='789', pin='2789', sou='23789', honors='1')
        table.player.init_hand(tiles)
        table.player.draw_tile(self._string_to_136_tile(sou='1'))

        table.add_discarded_tile(1, self._string_to_136_tile(sou='7'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(honors='1'), False)
        table.add_called_riichi(1)
        table.add_discarded_tile(2, self._string_to_136_tile(honors='1'), False)

        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '1z')

    def test_defence_against_honitsu_first_case(self):
        table = Table()

        tiles = self._string_to_136_array(sou='22', pin='222367899', man='45', honors='1')
        table.player.init_hand(tiles)

        table.add_called_meld(1, self._make_meld(Meld.CHI, pin='567'))
        table.add_called_meld(1, self._make_meld(Meld.CHI, pin='123'))
        table.add_called_meld(1, self._make_meld(Meld.CHI, pin='345'))

        table.add_discarded_tile(1, self._string_to_136_tile(sou='6'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(sou='6'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(sou='8'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(sou='9'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='1'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='1'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='5'), False)

        result = table.player.discard_tile()

        # we can't discard pin and honor tiles against honitsu
        self.assertEqual(self._to_string([result]), '2s')

    def test_defence_against_honitsu_second_case(self):
        table = Table()

        tiles = self._string_to_136_array(sou='4', pin='223456', man='678', honors='66')
        table.player.init_hand(tiles)

        table.add_called_meld(1, self._make_meld(Meld.CHI, sou='789'))
        table.add_called_meld(1, self._make_meld(Meld.PON, honors='444'))
        table.add_called_meld(1, self._make_meld(Meld.PON, honors='222'))

        table.add_discarded_tile(1, self._string_to_136_tile(man='2'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(man='8'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='1'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='3'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='4'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='6'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(sou='7'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(pin='9'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(honors='5'), False)
        table.add_discarded_tile(1, self._string_to_136_tile(honors='7'), False)

        table.player.draw_tile(self._string_to_136_tile(sou='9'))
        result = table.player.discard_tile()

        self.assertEqual(self._to_string([result]), '3p')

from tenhou.decoder import MeldPrint, TenhouDecoder


def test_parse_initial_round_values():
    decoder = TenhouDecoder()
    message = (
        '<INIT seed="0,2,3,0,1,126" ten="250,250,250,250" oya="3" hai="30,67,44,21,133,123,87,69,36,34,94,4,128"/>'
    )
    values = decoder.parse_initial_values(message)
    assert values["round_wind_number"] == 0
    assert values["count_of_honba_sticks"] == 2
    assert values["count_of_riichi_sticks"] == 3
    assert values["dora_indicator"] == 126
    assert values["dealer"] == 3


def test_parse_initial_hand():
    decoder = TenhouDecoder()
    message = (
        '<INIT seed="0,2,3,0,1,126" ten="250,250,250,250" oya="3" hai="30,67,44,21,133,123,87,69,36,34,94,4,128"/>'
    )
    tiles = decoder.parse_initial_hand(message)
    assert len(tiles) == 13


def test_parse_initial_scores():
    decoder = TenhouDecoder()
    message = (
        '<INIT seed="0,2,3,0,1,126" ten="240,260,270,280" oya="3" hai="30,67,44,21,133,123,87,69,36,34,94,4,128"/>'
    )
    values = decoder.parse_initial_values(message)
    assert values["scores"] == [240, 260, 270, 280]


def test_parse_names_and_ranks():
    decoder = TenhouDecoder()
    message = (
        '<un n0="%4e%6f%4e%61%6d%65" n1="%6f%32%6f%32" n2="%73%68%69%6d%6d%6d%6d%6d"'
        ' n3="%e5%b7%9d%e6%b5%b7%e8%80%81" dan="0,7,12,1" '
        'rate="1500.00,1421.91,1790.94,1532.23" sx="m,m,m,m"/>'
    )
    values = decoder.parse_names_and_ranks(message)
    assert values[0] == {"seat": 0, "name": "NoName", "rank": TenhouDecoder.RANKS[0]}
    assert values[1] == {"seat": 1, "name": "o2o2", "rank": TenhouDecoder.RANKS[7]}
    assert values[2] == {"seat": 2, "name": "shimmmmm", "rank": TenhouDecoder.RANKS[12]}
    assert values[3] == {"seat": 3, "name": "川海老", "rank": TenhouDecoder.RANKS[1]}


def test_parse_final_scores_and_uma():
    decoder = TenhouDecoder()
    message = (
        '<agari ba="0,0" hai="12,13,41,46,51,78,80,84,98,101,105" m="51243" '
        'machi="101" ten="30,1000,0" yaku="20,1" dorahai="89" who="2" fromwho="1" '
        'sc="225,0,240,-10,378,10,157,0" owari="225,-17.0,230,3.0,388,48.0,157,-34.0" />'
    )
    values = decoder.parse_final_scores_and_uma(message)
    assert values["scores"] == [225, 230, 388, 157]
    assert values["uma"] == [-17, 3, 48, -34]

    message = (
        '<ryuukyoku ten="30,1000,0" sc="225,0,240,-10,378,10,157,0" owari="225,-17.0,230,3.0,388,48.0,157,-34.0" />'
    )
    values = decoder.parse_final_scores_and_uma(message)
    assert values["scores"] == [225, 230, 388, 157]
    assert values["uma"] == [-17, 3, 48, -34]


def test_parse_log_link():
    decoder = TenhouDecoder()
    message = '<TAIKYOKU oya="1" log="2016031911gm-0001-0000-381f693b"/>'
    game_id, position = decoder.parse_log_link(message)
    assert game_id == "2016031911gm-0001-0000-381f693b"
    assert position == 3


def test_auth_message():
    decoder = TenhouDecoder()
    message = """<HELO uname="%4E%6F%4E%61%6D%65"
                       PF4="9,45,1290.90,-5184.0,69,95,129,157,71,4303,831,830,33,1761"/>"""

    rating_string, _ = decoder.parse_hello_string(message)
    assert rating_string == "9,45,1290.90,-5184.0,69,95,129,157,71,4303,831,830,33,1761"


def test_decode_new_dora_indicator():
    decoder = TenhouDecoder()
    message = '<DORA hai="125" />'

    result = decoder.parse_dora_indicator(message)

    assert result == 125


def test_parse_called_pon():
    decoder = TenhouDecoder()
    meld = decoder.parse_meld('<N who="3" m="34314" />')

    assert meld.who == 3
    assert meld.type == MeldPrint.PON
    assert meld.opened is True
    assert meld.tiles == [89, 90, 91]


def test_parse_called_closed_kan():
    decoder = TenhouDecoder()
    meld = decoder.parse_meld('<N who="0" m="15872" />')

    assert meld.who == 0
    assert meld.from_who == 0
    assert meld.type == MeldPrint.KAN
    assert meld.opened is False
    assert meld.tiles == [60, 61, 62, 63]


def test_parse_called_opened_kan():
    decoder = TenhouDecoder()
    meld = decoder.parse_meld('<N who="3" m="13825" />')

    assert meld.who == 3
    assert meld.from_who == 0
    assert meld.type == MeldPrint.KAN
    assert meld.opened is True
    assert meld.tiles == [52, 53, 54, 55]


def test_parse_called_chakan():
    decoder = TenhouDecoder()
    meld = decoder.parse_meld('<N who="3" m="18547" />')

    assert meld.who == 3
    assert meld.type == MeldPrint.SHOUMINKAN
    assert meld.opened is True
    assert meld.tiles == [48, 49, 50, 51]


def test_parse_called_chi():
    decoder = TenhouDecoder()
    meld = decoder.parse_meld('<N who="3" m="27031" />')

    assert meld.who == 3
    assert meld.type == MeldPrint.CHI
    assert meld.opened is True
    assert meld.tiles == [42, 44, 51]


def test_parse_tile():
    decoder = TenhouDecoder()

    tile = decoder.parse_tile("<t23/>")
    assert tile == 23

    tile = decoder.parse_tile("<e24/>")
    assert tile == 24

    tile = decoder.parse_tile("<f25/>")
    assert tile == 25

    tile = decoder.parse_tile("<g26/>")
    assert tile == 26

    tile = decoder.parse_tile('<f23 t="4"/>')
    assert tile == 23


def test_parse_who_called_riichi():
    decoder = TenhouDecoder()

    who = decoder.parse_who_called_riichi('<REACH who="2" ten="255,216,261,258" step="2"/>')
    assert who == 2


def test_reconnection_information():
    message = (
        '<REINIT seed="0,0,1,4,3,59" ten="250,250,250,240" oya="0" '
        'hai="1,2,4,13,17,20,46,47,53,71,76,81,85" '
        'm2="41515" '
        'kawa0="120,28,128,131,18,75,74,27,69,130,64" '
        'kawa1="117,121,123,129,103,72,83,125,62,84" '
        'kawa2="33,114,122,107,31,105,78,9,68,73,38" '
        'kawa3="115,0,126,87,24,25,106,255,70,3,119"/>'
    )
    decoder = TenhouDecoder()
    result = decoder.parse_table_state_after_reconnection(message)
    assert len(result) == 4

    assert len(result[0]["discards"]) == 11
    # one additional tile from meld
    assert len(result[1]["discards"]) == 11
    assert len(result[2]["discards"]) == 11
    assert len(result[3]["discards"]) == 10
    assert len(result[2]["melds"]) == 1


def test_is_match_discard():
    decoder = TenhouDecoder()

    assert decoder.is_discarded_tile_message("<e107/>") is True
    assert decoder.is_discarded_tile_message("<F107/>") is True
    assert decoder.is_discarded_tile_message("<g107/>") is True
    assert decoder.is_discarded_tile_message('<GO type="9" lobby="0" gpid=""/>') is False
    assert decoder.is_discarded_tile_message('<FURITEN show="1" />') is False

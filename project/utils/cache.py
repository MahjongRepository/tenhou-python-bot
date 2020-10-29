from typing import List, Optional

from mahjong.tile import TilesConverter
from utils.decisions_logger import MeldPrint


def build_shanten_cache_key(tiles_34: List[int], open_sets_34: Optional[List[List[int]]], use_chiitoitsu: bool):
    cache_key = "{},{},{}".format(
        "".join([str(x) for x in tiles_34]),
        open_sets_34 and ";".join([str(x) for x in open_sets_34]) or "",
        use_chiitoitsu and 1 or 0,
    )
    return cache_key


def build_estimate_hand_value_cache_key(
    tiles_136: List[int], is_riichi: bool, is_tsumo: bool, melds: List[MeldPrint], dora_indicators: List[int]
):
    cache_key = "{}.{}.{}.{}.{}".format(
        TilesConverter.to_one_line_string(tiles_136),
        is_tsumo and 1 or 0,
        is_riichi and 1 or 0,
        ",".join([";".join([str(x) for x in x.tiles]) for x in melds]),
        ",".join([str(x) for x in dora_indicators]),
    )
    return cache_key

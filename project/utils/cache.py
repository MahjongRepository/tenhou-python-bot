import hashlib
import marshal
from typing import List

from utils.decisions_logger import MeldPrint


def build_shanten_cache_key(tiles_34: List[int], use_chiitoitsu: bool):
    prepared_array = tiles_34 + [int(use_chiitoitsu)]
    return hashlib.md5(marshal.dumps(prepared_array)).hexdigest()


def build_estimate_hand_value_cache_key(
    tiles_136: List[int],
    is_riichi: bool,
    is_tsumo: bool,
    melds: List[MeldPrint],
    dora_indicators: List[int],
    count_of_riichi_sticks: int,
    count_of_honba_sticks: int,
    additional_han: int,
    is_rinshan: bool,
    is_chankan: bool,
):
    prepared_array = (
        tiles_136
        + [is_tsumo and 1 or 0]
        + [is_riichi and 1 or 0]
        + (melds and [x.tiles for x in melds] or [])
        + dora_indicators
        + [count_of_riichi_sticks]
        + [count_of_honba_sticks]
        + [additional_han]
        + [is_rinshan and 1 or 0]
        + [is_chankan and 1 or 0]
    )
    return hashlib.md5(marshal.dumps(prepared_array)).hexdigest()

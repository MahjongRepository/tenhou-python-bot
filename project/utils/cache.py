import hashlib
import marshal
from typing import List

from utils.decisions_logger import MeldPrint


def build_shanten_cache_key(tiles_34: List[int], use_chiitoitsu: bool):
    prepared_array = tiles_34 + [int(use_chiitoitsu)]
    return hashlib.md5(marshal.dumps(prepared_array)).hexdigest()


def build_estimate_hand_value_cache_key(
    tiles_136: List[int], is_riichi: bool, is_tsumo: bool, melds: List[MeldPrint], dora_indicators: List[int]
):
    prepared_array = (
        tiles_136
        + [is_tsumo and 1 or 0]
        + [is_riichi and 1 or 0]
        + [200]  # to be sure that hand and meld tiles will not be mixed together
        + (melds and [x.tiles for x in melds] or [])
        + [200]
        + dora_indicators
    )
    return hashlib.md5(marshal.dumps(prepared_array)).hexdigest()

# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from functools import lru_cache
from math import floor

import pytermor as pt

from es7s_commons.strutil import to_superscript

FULL_BLOCK = "█"


class Scale(pt.Text):
    SCALE_LEN = 10

    def __init__(
        self,
        ratio: float,
        label_st: pt.FT,
        scale_st: pt.FT,
        length: int = SCALE_LEN,
        *,
        use_partials: bool = True,
        require_not_empty: bool = False,
        full_block_char: str = FULL_BLOCK,
        start_char: str = None,
        label_override: str = None,
    ):
        label_str = label_override or format_ratio(ratio)
        label_frag: pt.Fragment = pt.Fragment(f" {label_str} ", label_st)

        char_num: float = length * ratio
        full_block_num = floor(char_num)
        blocks_str = full_block_char * full_block_num
        if len(blocks_str) and start_char:
            blocks_str = start_char + blocks_str[1:]
        if use_partials:
            blocks_str += get_partial_hblock(char_num - full_block_num)
        if not blocks_str and require_not_empty:
            blocks_str = "▏"
        blocks_frag: pt.Fragment = pt.Fragment(blocks_str, scale_st)

        empty_blocks_frag: pt.Fragment = pt.Fragment(pt.pad(length - len(blocks_str)), scale_st)

        super().__init__(label_frag, blocks_frag, empty_blocks_frag)


@lru_cache(maxsize=128)
def format_ratio(ratio: float):
    ratio_str = pt.format_auto_float(100 * ratio, 3)
    if ratio_str == "0.0":
        ratio_str = "e-2"
    if "e" in ratio_str:
        base, exp, power = ratio_str.partition("e")
        ratio_str = base + "10" + to_superscript(power)
    return f"{ratio_str:>3s}%"


def get_partial_hblock(val: float) -> str:  # @REFACTOR ME
    if val >= 7 / 8:
        return "▉"
    elif val >= 6 / 8:
        return "▊"
    elif val >= 5 / 8:
        return "▋"
    elif val >= 4 / 8:
        return "▌"
    elif val >= 3 / 8:
        return "▍"
    elif val >= 2 / 8:
        return "▎"
    elif val >= 1 / 8:
        return "▏"
    return ""

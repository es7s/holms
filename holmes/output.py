import math
import re
import sys
import unicodedata
from collections.abc import Iterable

from holmes.core import Char
import pytermor as pt


class CategoryStyles(dict[str, dict[str, pt.FrozenStyle]]):
    _BASE = pt.FrozenStyle()
    C = pt.FrozenStyle(_BASE, fg=pt.cv.RED)
    CS = pt.FrozenStyle(_BASE, fg=pt.cv.HI_YELLOW, bg=pt.cv.DARK_RED)
    CO = pt.FrozenStyle(_BASE, fg=pt.cv.BLACK, bg=pt.cv.RED)
    CN = pt.FrozenStyle(_BASE, fg=pt.cv.GRAY)
    Z = pt.FrozenStyle(_BASE, fg=pt.cv.CYAN)
    N = pt.FrozenStyle(_BASE, fg=pt.cv.BLUE)
    P = pt.FrozenStyle(_BASE, fg=pt.cv.YELLOW)
    S = pt.FrozenStyle(_BASE, fg=pt.cv.GREEN)
    M = pt.FrozenStyle(_BASE, fg=pt.cv.HI_YELLOW)
    NOT_UTF_8 = pt.FrozenStyle(_BASE, fg=pt.cv.MAGENTA)

    _CATEGORY_MAP = [
        ("Cc", C),
        ("Cf", C),
        ("Cs", CS),
        ("Co", CO),
        ("Cn", CN),
        ("Z*", Z),
        ("N*", N),
        ("P*", P),
        ("S*", S),
        ("M*", M),
        ("--", NOT_UTF_8),
    ]

    def __init__(self):
        super().__init__()
        for cat, st in self._CATEGORY_MAP:
            k1, k2 = self._category_to_key(cat)
            subdict = super().get(k1, dict())
            if not subdict:
                self.update({k1: subdict})
            subdict.update({k2: st})

    def get(self, cat: str, default: pt.Style = pt.NOOP_STYLE) -> pt.Style:
        k1, k2 = self._category_to_key(cat)
        if k1 not in self.keys():
            return default
        subdict = super().get(k1)
        if k2 in subdict.keys():
            return subdict.get(k2)
        if "*" in subdict.keys():
            return subdict.get("*")
        return default

    @classmethod
    def _category_to_key(cls, cat: str) -> tuple[str, str]:
        if len(cat) != 2:
            raise ValueError(f"Category mapping key should be 2-char long: {cat!r}")
        return cat[0], cat[1]


class CliWriter:
    IDX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_50, bg=pt.cv.BLACK)
    IDX_ZEROS_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_23, bg=pt.cv.BLACK)
    CPNUM_PFX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30)
    CHAR_STYLE = pt.FrozenStyle(fg=0xFFFFFF, bg=0, bold=True)
    INVALID_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30)

    def __init__(self, io=sys.stdout, decimal: bool = False, squash: bool = False):
        self._io = io
        pt.RendererManager.set_default(pt.SgrRenderer(pt.OutputMode.XTERM_256))

        self._decimal_idx = decimal
        self._squash = squash

        self._idx = 0
        self._max_idx_len = 4
        self._styles = CategoryStyles()

    def print_string(self, cc: Iterable[Char]):
        prev_c: Char | None = None
        dup_count = 0

        for c in cc:
            if not self._squash:
                self._print_char(c)
                continue

            if prev_c and prev_c != c:
                self._print_char(prev_c, dup_count)
                dup_count = 0
            if prev_c == c:
                dup_count += 1
            prev_c = c

    def _print_char(self, c: Char, dup_count: int = 0):
        text = pt.Text(
            self._format_idx(self._idx, dup_count),
            " ",
            self._format_dup_count(dup_count),
            self._format_cpnum(c),
            "▕",
            self._format_char(c),
            "▏",
            self._format_category(c),
            " ",
            self._format_name(c),
        )
        pt.echo(text, file=self._io)
        self._idx += 1 + dup_count

    @property
    def _base(self) -> int:
        return [0x10, 10][self._decimal_idx]

    def _format_idx(self, idx: int, dup_count: int) -> str:
        self._max_idx_len = max(self._max_idx_len, len(self._format_idx_val(idx)))
        idx_str = self._format_idx_val(idx, self._max_idx_len)
        idx_st = self.IDX_STYLE
        suffix = [" ", ":"][dup_count > 0]

        try:
            _, zeros, nonzeros = re.split('^([0 ]+)', idx_str)
            return pt.render(pt.Text(zeros, self.IDX_ZEROS_STYLE, nonzeros+suffix, idx_st))
        except ValueError:
            return pt.render(pt.Text(idx_str+suffix, idx_st))

    def _format_idx_val(self, idx: int, max_len: int = None) -> str:
        fmt = "xd"[self._decimal_idx]

        if max_len is None:
            result = f"{idx:{fmt}}"
            if self._decimal_idx:
                return result
            return pt.fit(result, 2 * math.ceil(len(result) / 2), fill="0")

        fill = "0-"[self._decimal_idx]
        return f"{idx:{fill}{max_len}{fmt}}"

    def _format_dup_count(self, dup_count: int) -> str:
        if not self._squash:
            return ""
        sep = " "
        if dup_count == 0:
            return pt.pad(self._max_idx_len + 1) + sep
        return f"{(dup_count+1):>{self._max_idx_len}d}×{sep}"

    def _format_cpnum_val(self, c: Char) -> str:
        if c.is_invalid:
            return f"0x{c.cpnum:>6X}"
        result = f"{c.cpnum:02X}"
        return f"U+{result:<6s}"

    def _format_cpnum(self, c: Char) -> str:
        val = self._format_cpnum_val(c)
        return pt.render(pt.Text(val[:2], self.CPNUM_PFX_STYLE, val[2:]))

    def _format_char(self, c: Char) -> str:
        char = c.char
        st = pt.merge_styles(
            self.CHAR_STYLE,
            overwrites=[
                self._styles._BASE,
                self._styles.get(c.category, pt.NOOP_STYLE),
            ],
        )
        aux = ""

        if c.is_control or c.is_surrogate or c.is_unassigned or c.is_invalid:
            char = "▯"
            charlen = 1
        else:
            charlen = pt.get_char_width(c.char, block=False)
            if unicodedata.combining(c.char):
                aux = " "
                charlen += 1
        return " " * (2 - max(-1, charlen)) + pt.render(aux + char, st) + " "

    def _format_category(self, c: Char) -> str:
        if not c.category:
            return ""
        return pt.render(c.category, self._styles.get(c.category, self._styles._BASE))

    def _format_name(self, c: Char) -> str:
        st = pt.NOOP_STYLE
        if c.is_invalid:
            st = self.INVALID_STYLE
        return pt.render(c.name or "", st)

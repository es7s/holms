# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import math
import re
import sys
import unicodedata
from collections import deque, OrderedDict
from collections.abc import Iterable
import typing as t
from dataclasses import dataclass

from es7s_commons.pt_ import joincoal

from .core import Char, Attribute
import pytermor as pt


@dataclass
class Column:
    attr: Attribute
    max_val: int = 0
    max_width: int = 0

    def update_val(self, val) -> int:
        self.max_val = max(self.max_val, val)
        return self.max_val

    def update_width(self, width) -> int:
        self.max_width = max(self.max_width, width)
        return self.max_width


@dataclass
class Row:
    char: Char | None
    offset: int
    index: int
    dup_count: int = 0

    @property
    def has_cpnum(self) -> bool:
        return self.char and not self.char.is_invalid

    @property
    def cpnum_or_byte(self) -> int | None:
        if not self.char:
            return None
        return self.char.cpnum


class Totals(t.Dict[Char, int]):
    def sorted(self) -> list[tuple[Char, int]]:
        return sorted(self.items(), key=lambda kv: kv[1])


class Table(OrderedDict[Attribute, Column]):
    DEFAULT_WIDTH = {
        Attribute.OFFSET: 4,
        Attribute.INDEX: 4,
        Attribute.COUNT: 4,
        Attribute.NUMBER: 6,
        Attribute.NAME: 16,
    }

    def __init__(self, data):
        super().__init__(data)
        self.index = 0
        self.offset = 0

    def setdefaults(self):
        for attr, col in self.items():
            col.update_width(self.DEFAULT_WIDTH.get(attr, 0))


@dataclass(frozen=True)
class Format:
    render_fn: t.Callable[[Row], str]
    fmt_val_fn: t.Callable[[Row, Column | None], str] | None = None


class CliWriter:
    IDX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_50, bg=pt.cv.BLACK)
    IDX_ZEROS_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_23, bg=pt.cv.BLACK)
    CPNUM_PFX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30)
    CHAR_STYLE = pt.FrozenStyle(fg=0xFFFFFF, bg=0)
    INVALID_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30)

    _OVERRIDE_CHARS = dict[int, str](
        {
            0x00: "Ø",
            0x08: "←",
            0x09: "⇥",
            0x0A: "↵",
            0x0B: "⤓",
            0x0C: "↡",
            0x0D: "⇤",
            0x1B: "ə",
            0x20: "␣",
            0x7F: "→",
        }
    )

    def __init__(
        self,
        format: list[Attribute],
        squash: bool,
        total: bool,
        output_mode: str | None,
        decimal: bool,
        io=sys.stdout,
        **kwargs,
    ):
        self._io = io
        pt.RendererManager.set_default(pt.SgrRenderer(output_mode or pt.OutputMode.AUTO))

        self._attributes = format
        self._single_char_mode = {*self._attributes} == {Attribute.CHAR}
        self._squash = squash
        self._total = total
        self._decimal_offset = decimal

        self._buffer = deque[Row]()
        self._styles = CategoryStyles()

        self._table = Table({a: Column(a) for a in self._attributes})
        self._totals = Totals()

    def _get_format(self, attr: Attribute) -> Format:
        match attr:
            case Attribute.OFFSET:
                return Format(self._render_offset, self._format_offset_val)
            case Attribute.INDEX:
                return Format(self._render_index, self._format_index_val)
            case Attribute.NUMBER:
                return Format(self._render_cpnum, self._format_cpnum_val)
            case Attribute.COUNT:
                return Format(self._render_dup_count, self._format_dup_count_val)
            case Attribute.CHAR:
                return Format(self._render_char)
            case Attribute.TYPE:
                return Format(self._render_type)
            case Attribute.NAME:
                return Format(self._render_name, self._format_name)
            case _:
                raise RuntimeError(f"Invalid attribute: {attr}")

    def write(self, chars: Iterable[Char | None]):
        prev_char: Char | None = None
        dup_count = 0
        self._buffered = isinstance(chars, t.Sized)
        if not self._buffered:
            self._table.setdefaults()

        for char in chars:
            if self._total:
                if char not in self._totals.keys():
                    self._totals[char] = 0
                self._totals[char] += 1
                continue

            if not self._squash:
                self._make_row(char)
                continue

            if prev_char and prev_char != char:
                self._make_row(prev_char, dup_count)
                dup_count = 0
            if prev_char == char:
                dup_count += 1
            prev_char = char

        if not self._buffered:
            return

        if self._total:
            for char, count in self._totals.sorted():
                self._make_row(char, count - 1)

        self._update_columns()
        for row in self._buffer:
            self._print_row(row)

    def _make_row(self, char: Char | None, dup_count: int = 0):
        if char is None:
            return
        row = Row(char, self._table.offset, self._table.index, dup_count)
        self._update_columns(row)
        char_count = 1 + dup_count
        self._table.offset += char_count * char.bytelen
        self._table.index += char_count

        if self._buffered:
            self._buffer.append(row)
        else:
            self._print_row(row)

    def _print_row(self, row: Row):
        if row.char is None:
            return
        pt.echo(self._render_row(row), nl=(not self._single_char_mode), file=self._io)

    def _render_row(self, row: Row):
        return joincoal(*[f.render_fn(row) for f in self._iter_formats()])

    def _iter_formats(self) -> Iterable[Format]:
        for attr in self._attributes:
            yield self._get_format(attr)

    @property
    def _base(self) -> int:
        return [0x10, 10][self._decimal_offset]

    def _update_columns(self, row: Row = None):
        for attr in self._attributes:
            if not (col := self._table.get(attr)):
                continue
            if not (val_fmt_fn := self._get_format(attr).fmt_val_fn):
                continue
            val_str = val_fmt_fn(row, col)
            width = len(val_str)
            col.update_width(width)

    def _render_offset(self, row: Row) -> str:
        if self._total:
            return ""
        col = self._table.get(Attribute.OFFSET)
        o_str = self._format_offset_val(row, col)
        o_st = self.IDX_STYLE
        prefix = ["0x", "@"][self._decimal_offset]
        suffix = [" ", "‥"][row.dup_count > 0]

        _, zeros, nonzeros = re.split("^([0 ]*)(?=.)", o_str)
        text = pt.Text(prefix + zeros, self.IDX_ZEROS_STYLE, nonzeros + suffix, o_st)
        return pt.render(text) + " "

    def _format_offset_val(self, row: Row, col: Column = None) -> str:
        val = row.offset if row else col.max_val
        fmt = ["x", "d"][self._decimal_offset]

        if col is None:
            result = f"{val:{fmt}}"
            if self._decimal_offset:
                return result
            return pt.fit(result, 2 * math.ceil(len(result) / 2), fill="0")
        fill = ["0", ""][self._decimal_offset]
        return f"{val:{fill}{col.max_width}{fmt}}"

    def _render_index(self, row: Row) -> str:
        if self._total:
            return ""
        col = self._table.get(Attribute.INDEX)
        o_str = self._format_index_val(row, col)
        o_st = self.IDX_STYLE
        prefix = "#"
        suffix = " "

        _, zeros, nonzeros = re.split("^([0 ]*)(?=.)", o_str)
        text = pt.Text(prefix + zeros, self.IDX_ZEROS_STYLE, nonzeros + suffix, o_st)
        return pt.render(text) + " "

    def _format_index_val(self, row: Row, col: Column = None) -> str:
        val = row.index if row else col.max_val

        if col is None:
            result = f"{val:d}"
            if self._decimal_offset:
                return result
            return pt.fit(result, 2 * math.ceil(len(result) / 2), fill="0")
        return f"{val:{col.max_width}d}"

    def _render_dup_count(self, row: Row) -> str:
        if not self._squash:
            return ""
        col = self._table.get(Attribute.COUNT)
        return pt.render(pt.highlight(self._format_dup_count_val(row, col)))

    def _format_dup_count_val(self, row: Row, col: Column = None) -> str:
        val = max((row.dup_count if row else 0), col.max_val)
        if val == 0 and not self._total:
            result = ""
        else:
            result = str(val + 1) + "x"

        if col is None:
            return result
        return pt.fit(result, max(len(result), col.max_width), ">")

    def _render_cpnum(self, row: Row) -> str:
        prefix = "U+"
        result_st = pt.NOOP_STYLE
        if row.char.is_invalid:
            prefix = "0x"
            result_st = self.INVALID_STYLE

        col = self._table.get(Attribute.NUMBER)
        result = self._format_cpnum_val(row, col).strip()
        max_col_width = min(7, col.max_width + 2)
        prefix = pt.fit(prefix, max_col_width - len(result), "<", overflow="")
        return pt.render(pt.Text(prefix, self.CPNUM_PFX_STYLE, result, result_st))

    def _format_cpnum_val(self, row: Row, col: Column = None) -> str:
        if not row or not row.char:
            return ""
        max_width = max((col.max_width if col else 0), 2)
        return f"{row.cpnum_or_byte:>{max_width}X}"

    def _render_char(self, row: Row) -> str:
        cat_st = self._styles.get(row.char.type, pt.NOOP_STYLE)
        value = row.char.value

        if self._single_char_mode:
            if row.char.is_ascii_c0:
                return value
            if row.char.is_surrogate or row.char.is_invalid:
                return "▯"
            pad = " " * bool(unicodedata.combining(value))
            return pt.render(pad + value, cat_st)

        st = pt.merge_styles(self.CHAR_STYLE, overwrites=[self._styles._BASE, cat_st])
        pad = ""

        if override := self._OVERRIDE_CHARS.get(ord(value), None):
            val_len = 1
            value = override
        elif (
            row.char.is_control
            or row.char.is_surrogate
            or row.char.is_unassigned
            or row.char.is_invalid
        ):
            val_len = 1
            value = "▯"
        else:
            val_len = pt.get_char_width(value, block=False)
            if unicodedata.combining(value):
                pad = " "
                val_len += 1

        prefix = "▕" + pt.render(" " * (2 - max(-1, val_len)), self.CHAR_STYLE)
        suffix = pt.render(" ", self.CHAR_STYLE) + "▏"
        return prefix + pt.render(pad + value, st) + suffix

    def _render_type(self, row: Row) -> str:
        prefix = " "
        type = row.char.type
        if not type:
            return prefix
        st = self._styles.get(type, self._styles._BASE)
        return prefix + pt.render(type, st)

    def _render_name(self, row: Row) -> str:
        prefix = " "
        st: pt.Style = [pt.NOOP_STYLE, self.INVALID_STYLE][row.char.is_invalid]
        col = self._table.get(Attribute.NAME)
        return prefix + pt.render(self._format_name(row, col), st)

    def _format_name(self, row: Row, col: Column = None) -> str:
        if not row or not row.char:
            return ""
        max_width = max((col.max_width if col else 0), 16)
        return f"{row.char.name:{max_width}s}"


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

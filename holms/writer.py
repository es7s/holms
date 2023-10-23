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
    char: Char|None
    offset: int
    dup_count: int = 0


class Table(OrderedDict[Attribute, Column]):
    pass


@dataclass(frozen=True)
class Format:
    render_fn: t.Callable[[Row], str]
    fmt_val_fn: t.Callable[[int, Column|None], str] | None = None


class CliWriter:
    IDX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_50, bg=pt.cv.BLACK)
    IDX_ZEROS_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_23, bg=pt.cv.BLACK)
    CPNUM_PFX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30)
    CHAR_STYLE = pt.FrozenStyle(fg=0xFFFFFF, bg=0)
    INVALID_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30)

    def __init__(
        self,
        format: list[Attribute],
        decimal: bool,
        squash: bool,
        io=sys.stdout,
        **kwargs,
    ):
        self._io = io
        pt.RendererManager.set_default(pt.SgrRenderer(pt.OutputMode.XTERM_256))

        self._attributes = format
        self._single_char_mode = {*self._attributes} == {Attribute.CHAR}
        self._decimal_offset = decimal
        self._squash = squash

        self._offset = 0
        self._buffered = False
        self._buffer = deque[Row]()
        self._styles = CategoryStyles()

        self._table = Table({a: Column(a) for a in self._attributes})

    def _get_formatters(self, attr: Attribute) -> Format:
        match attr:
            case Attribute.OFFSET:
                return Format(self._render_offset, self._format_offset_val)
            case Attribute.COUNT:
                return Format(self._render_dup_count, self._format_dup_count_val)
            case Attribute.NUMBER:
                return Format(self._render_cpnum)
            case Attribute.CHAR:
                return Format(self._render_char)
            case Attribute.CATEGORY:
                return Format(self._render_category)
            case Attribute.NAME:
                return Format(self._render_name)
            case _:
                raise RuntimeError(f"Invalid attribute: {attr}")

    def write(self, chars: Iterable[Char | None]):
        prev_char: Char | None = None
        dup_count = 0
        if isinstance(chars, t.Sized):
            self._buffered = True
        else:
            self._update_column(Attribute.OFFSET, width=4)
            self._update_column(Attribute.COUNT, width=4)

        for char in chars:
            if not self._squash:
                self._make_row(char)
                continue

            if prev_char and prev_char != char:
                self._make_row(prev_char, dup_count)
                dup_count = 0
            if prev_char == char:
                dup_count += 1
            prev_char = char

        if self._buffered:
            self._update_columns()
            for row in self._buffer:
                self._print_row(row)

    def _make_row(self, char: Char | None, dup_count: int = 0):
        row = Row(char, self._offset, dup_count)
        self._update_columns(row)
        self._offset += 1 + dup_count

        if self._buffered:
            self._buffer.append(row)
        else:
            self._print_row(row)

    def _print_row(self, row: Row):
        if row.char is None:
            return

        line = pt.Text("".join(self._iter_attributes(row)))
        pt.echo(line, nl=(not self._single_char_mode), file=self._io)

    def _iter_attributes(self, row: Row):
        for attr in self._attributes:
            if render_fn := self._get_formatters(attr).render_fn:
                if rendered := render_fn(row):
                    yield rendered

    @property
    def _base(self) -> int:
        return [0x10, 10][self._decimal_offset]

    def _update_columns(self, row: Row = None):
        self._update_column(Attribute.OFFSET, val=row.offset if row else None)
        self._update_column(Attribute.COUNT, val=row.dup_count if row else None)

    def _update_column(self, attr: Attribute, *, val: int = None, width: int = None):
        if not (col := self._table.get(attr)):
            return

        if val is not None:
            col.update_val(val)

        if width is None:
            if val_fmt_fn := self._get_formatters(attr).fmt_val_fn:
                val_str = val_fmt_fn(col.max_val, None)
                width = len(val_str)

        if width is not None:
            col.update_width(width)

    def _render_offset(self, row: Row) -> str:
        col = self._table.get(Attribute.OFFSET)
        o_str = self._format_offset_val(row.offset, col)
        o_st = self.IDX_STYLE

        prefix = " "
        suffix = [" ", ":"][row.dup_count > 0]

        _, zeros, nonzeros = re.split("^([0 ]*)(?=.)", o_str)
        text = pt.Text(prefix + zeros, self.IDX_ZEROS_STYLE, nonzeros + suffix, o_st)
        return pt.render(text)

    def _format_offset_val(self, val: int, col: Column = None) -> str:
        fmt = "xd"[self._decimal_offset]

        if col is None:
            result = f"{val:{fmt}}"
            if self._decimal_offset:
                return result
            return pt.fit(result, 2 * math.ceil(len(result) / 2), fill="0")
        return f"{val:0{col.max_width}{fmt}}"

    def _render_dup_count(self, row: Row) -> str:
        if not self._squash:
            return ""
        col = self._table.get(Attribute.COUNT)
        return self._format_dup_count_val(row.dup_count, col)

    def _format_dup_count_val(self, val: int, col: Column = None) -> str:
        if val == 0:
            result = ""
        else:
            result = str(val + 1)+"×"

        if col is None:
            return result
        return pt.fit(result, col.max_width, ">")

    def _render_cpnum(self, row: Row) -> str:
        if row.char.is_invalid:
            prefix = "0x"
            result = f"{row.char.cpnum:>4X}"
        else:
            prefix = "U+"
            result = f"{row.char.cpnum:04X}"
        prefix = pt.fit(prefix, 7 - len(result), "<", overflow="")
        return pt.render(pt.Text(prefix, self.CPNUM_PFX_STYLE, result))

    def _render_char(self, row: Row) -> str:
        cat_st = self._styles.get(row.char.category, pt.NOOP_STYLE)
        value = row.char.value

        if self._single_char_mode:
            if row.char.is_ascii_c0:
                return value
            if row.char.is_surrogate or row.char.is_invalid:
                return "▯"
            pad = ""
            if unicodedata.combining(value):
                pad = " "
            return pt.render(pad +value, cat_st)

        st = pt.merge_styles(self.CHAR_STYLE, overwrites=[self._styles._BASE, cat_st])
        pad = ""

        if row.char.is_control or row.char.is_surrogate or row.char.is_unassigned or row.char.is_invalid:
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

    def _render_category(self, row: Row) -> str:
        prefix = " "
        cat = row.char.category
        if not cat:
            return prefix
        st = self._styles.get(cat, self._styles._BASE)
        return prefix + pt.render(cat, st)

    def _render_name(self, row: Row) -> str:
        prefix = " "
        st: pt.Style = [pt.NOOP_STYLE, self.INVALID_STYLE][row.char.is_invalid]
        return prefix + pt.render(row.char.name or "", st)


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

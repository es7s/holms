# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import math
import re
import sys
import typing as t
import unicodedata
from collections import deque, OrderedDict, namedtuple
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property

import pytermor as pt
from es7s_commons import Scale
from es7s_commons.pt_ import joincoal

from .common import Char, Attribute, _FORMAT_ALL
from .uccat import resolve_category


@dataclass(frozen=True)
class Setup:
    _columns: list[Attribute]
    _all_columns: bool
    merge: bool
    group: int
    decimal_offset: bool
    static: bool

    @cached_property
    def columns(self) -> list[Attribute]:
        if self._all_columns:
            return _FORMAT_ALL
        if not self._columns:
            return self._columns_default
        return self._columns

    @cached_property
    def _columns_default(self) -> list[Attribute]:
        exclude_by_default = [Attribute.INDEX, Attribute.RAW]
        if not self.group_cats:
            exclude_by_default.append(Attribute.TYPE_NAME)
        return [col for col in _FORMAT_ALL if col not in exclude_by_default]

    @cached_property
    def group_cats(self):
        return self.group >= 2

    @cached_property
    def group_super_cats(self):
        return self.group >= 3

    @cached_property
    def highlight_only_mode(self) -> bool:
        return len(self.columns) == 1 and self.columns[0] == Attribute.CHAR


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
    def raw_bytes(self) -> list[int]:
        if self.char:
            return [*self.char.bytes]
        return []


class Groups(t.Dict[Char | str, int]):
    def sorted(self) -> list[tuple[Char | str, int]]:
        return sorted(self.items(), key=lambda kv: -kv[1])

    @cached_property
    def sum(self) -> int:
        return sum(self.values())


class CategorySampleCache(t.Dict[str, Char]):
    pass


class Table(OrderedDict[Attribute, Column]):
    DEFAULT_WIDTH = {
        Attribute.OFFSET: 4,
        Attribute.INDEX: 4,
        Attribute.COUNT: 4,
        Attribute.RAW: 8,
        Attribute.NUMBER: 6,
        Attribute.NAME: 16,
        Attribute.TYPE: 2,
        Attribute.TYPE_NAME: 16,
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


class CategoryStyles(dict[str, dict[str, pt.FrozenStyle]]):
    _BASE = pt.FrozenStyle()
    C = pt.FrozenStyle(_BASE, fg=pt.cv.RED)
    CS = pt.FrozenStyle(_BASE, fg=pt.cv.HI_YELLOW, bg=pt.cv.DARK_RED)
    CO = pt.FrozenStyle(_BASE, fg=pt.cv.BLACK, bg=pt.cv.RED)
    CN = pt.FrozenStyle(_BASE, fg=pt.cv.GRAY)
    C_CUSTOM = pt.FrozenStyle(_BASE, fg=pt.cv.HI_RED)
    Z_CUSTOM = pt.FrozenStyle(_BASE, fg=pt.cv.HI_CYAN)
    Z = pt.FrozenStyle(_BASE, fg=pt.cv.CYAN)
    N = pt.FrozenStyle(_BASE, fg=pt.cv.BLUE)
    P = pt.FrozenStyle(_BASE, fg=pt.cv.YELLOW)
    S = pt.FrozenStyle(_BASE, fg=pt.cv.GREEN)
    M = pt.FrozenStyle(_BASE, fg=pt.cv.HI_YELLOW)
    NOT_UTF_8 = pt.FrozenStyle(_BASE, fg=pt.cv.MAGENTA)

    _CATEGORY_STYLE_MAP = [
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
        ("-*", NOT_UTF_8),
        ("C*", C),
    ]

    def __init__(self):
        super().__init__()
        for cat, st in self._CATEGORY_STYLE_MAP:
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
        if len(cat) == 1:
            return cat[0], " "
        if len(cat) != 2:
            raise ValueError(f"Category mapping key should be 1/2-char long: {cat!r}")
        return cat[0], cat[1]


CharOverride = namedtuple("CharOverride", ["char", "style"])


class CliWriter:
    IDX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_50, bg=pt.cv.BLACK)
    IDX_ZEROS_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_23, bg=pt.cv.BLACK)
    IDX_PFX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30, bg=pt.cv.BLACK)
    CPNUM_PFX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30)
    CHAR_STYLE = pt.FrozenStyle(fg=0xFFFFFF, bg=0)
    INVALID_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_30)
    PLAIN_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY_50)

    COLUMN_SEPARATOR = " "
    LTR_CHAR = "\u200e"  # to normalize the output after possible RTL switch

    _OVERRIDE_CHARS = dict[int, CharOverride](
        {
            0x00: CharOverride("Ø", CategoryStyles.C_CUSTOM),
            0x08: CharOverride("←", CategoryStyles.C_CUSTOM),
            0x09: CharOverride("⇥", CategoryStyles.C_CUSTOM),
            0x0A: CharOverride("↵", CategoryStyles.C_CUSTOM),
            0x0B: CharOverride("⤓", CategoryStyles.C_CUSTOM),
            0x0C: CharOverride("↡", CategoryStyles.C_CUSTOM),
            0x0D: CharOverride("⇤", CategoryStyles.C_CUSTOM),
            0x1B: CharOverride("ə", CategoryStyles.C_CUSTOM),
            0x1C: CharOverride("⁜", CategoryStyles.C_CUSTOM),
            0x1D: CharOverride("⋮", CategoryStyles.C_CUSTOM),
            0x1E: CharOverride("∻", CategoryStyles.C_CUSTOM),
            0x1F: CharOverride("·", CategoryStyles.C_CUSTOM),
            0x20: CharOverride("␣", CategoryStyles.Z_CUSTOM),
            0x7F: CharOverride("→", CategoryStyles.C_CUSTOM),
        }
    )

    def __init__(self, setup: Setup, output=sys.stdout):
        self._setup = setup
        self._output = output

        self._buffer = deque[Row]()
        self._table = Table({a: Column(a) for a in self._setup.columns})
        self._groups = Groups()
        self._cat_cache = CategorySampleCache()

        self._styles = CategoryStyles()

    def _get_format(self, attr: Attribute) -> Format:
        match attr:
            case Attribute.OFFSET:
                return Format(self._render_offset, self._format_offset_val)
            case Attribute.INDEX:
                return Format(self._render_index, self._format_index_val)
            case Attribute.RAW:
                return Format(self._render_raw, self._format_raw)
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
            case Attribute.TYPE_NAME:
                return Format(self._render_type_name, self._format_type_name)
            case _:
                raise RuntimeError(f"Invalid attribute: {attr}")

    def write(self, chars: Iterable[Char | None]):
        prev_char: Char | None = None
        dup_count = 0
        self._buffered = isinstance(chars, t.Sized)
        if not self._buffered:
            self._table.setdefaults()

        for char in chars:
            if self._setup.group:
                if char is not None:
                    match self._setup.group:
                        case 1:
                            key = char
                        case 2:
                            key = char.type
                        case 3:
                            key = char.type[0]
                        case _:
                            raise RuntimeError(f"Invalid 'group' value: {self._setup.group}")
                    if key not in self._groups.keys():
                        self._groups[key] = 0
                        if not isinstance(key, Char):
                            self._cat_cache[key] = char
                            char.type = key
                    self._groups[key] += 1
                continue

            if not self._setup.merge:
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

        if self._setup.group:
            for key, count in self._groups.sorted():
                char = key if isinstance(key, Char) else self._cat_cache.get(key)
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
        pt.echo(self._render_row(row), nl=(not self._setup.highlight_only_mode), file=self._output)

    def _render_row(self, row: Row):
        # if self._setup.group_cats:
        #     return self._render_group(row)
        return joincoal(*[f.render_fn(row) for f in self._iter_formats()])

    def _iter_formats(self) -> Iterable[Format]:
        for attr in self._setup.columns:
            yield self._get_format(attr)

    @property
    def _base(self) -> int:
        return [0x10, 10][self._setup.decimal_offset]

    def _update_columns(self, row: Row = None):
        for attr in self._setup.columns:
            if not (col := self._table.get(attr)):
                continue
            if not (val_fmt_fn := self._get_format(attr).fmt_val_fn):
                continue
            val_str = val_fmt_fn(row, col)
            width = len(val_str)
            col.update_width(width)

    def _render_offset(self, row: Row) -> str:
        if self._setup.group:
            return ""
        col = self._table.get(Attribute.OFFSET)
        return self.__render_address(
            row,
            [" ", "⏨"][self._setup.decimal_offset],
            self._format_offset_val(row, col),
            self.IDX_STYLE,
        )

    def _format_offset_val(self, row: Row, col: Column = None) -> str:
        val = row.offset if row else col.max_val
        fmt = ["x", "d"][self._setup.decimal_offset]

        if col is None:
            result = f"{val:{fmt}}"
            if self._setup.decimal_offset:
                return result
            return pt.fit(result, 2 * math.ceil(len(result) / 2), fill="0")
        fill = ["0", ""][self._setup.decimal_offset]
        return f"{val:{fill}{col.max_width}{fmt}}"

    def _render_index(self, row: Row) -> str:
        if self._setup.group:
            return ""
        col = self._table.get(Attribute.INDEX)
        return self.__render_address(
            row,
            "#",
            self._format_index_val(row, col),
            self.IDX_STYLE,
        )

    def __render_address(self, row: Row, prefix: str, val_str: str, val_st: pt.Style):
        suffix = [" ", "+"][row.dup_count > 0]
        _, zeros, nonzeros = re.split("^([0 ]*)(?=.)", val_str)
        text = pt.Text(
            prefix, self.IDX_PFX_STYLE, zeros, self.IDX_ZEROS_STYLE, nonzeros + suffix, val_st
        )
        return pt.render(text) + self.COLUMN_SEPARATOR

    def _format_index_val(self, row: Row, col: Column = None) -> str:
        val = row.index if row else col.max_val
        max_width = col.max_width if col else 0
        return f"{val:{max_width}d}"

    def _render_dup_count(self, row: Row) -> str:
        if not self._setup.merge:
            return ""
        col = self._table.get(Attribute.COUNT)
        val_str = self._format_dup_count_val(row, col)
        if not val_str.strip() and not self._setup.group:
            result = pt.pad(len(val_str) + 1)
        else:
            result = pt.render(pt.highlight(val_str)) + "×"
        result += self.COLUMN_SEPARATOR

        if row and self._setup.group:
            ratio = (row.dup_count + 1) / self._groups.sum
            scale_st = self._styles.get(row.char.type, self._styles._BASE)
            if scale_st.bg:
                scale_st = pt.Style(fg=scale_st.bg)
            scale_width = [3, 10][self._setup.group_cats]
            scale = Scale(ratio, pt.NOOP_STYLE, scale_st, scale_width, allow_partials=True)
            result = pt.render(scale) + self.COLUMN_SEPARATOR + result
        return result

    def _format_dup_count_val(self, row: Row, col: Column = None) -> str:
        val = max((row.dup_count if row else 0), col.max_val)

        if val > 1 or self._setup.group:
            result = str(val + 1)
        else:
            result = " "

        if col is None:
            return result
        return pt.fit(result, max(len(result), col.max_width), ">")

    def _render_raw(self, row: Row) -> str:
        if self._setup.group_cats:
            return ""

        col = self._table.get(Attribute.RAW)

        result = self._format_raw(row, col).strip()
        prefix = " 0x "

        max_col_width = min([9, 14][self._setup.static], col.max_width + len(prefix))
        prefix = pt.fit(prefix, max_col_width - len(result), "<", overflow="")
        return pt.render(pt.Text(prefix, self.CPNUM_PFX_STYLE, result)) + self.COLUMN_SEPARATOR

    def _format_raw(self, row: Row, col: Column = None) -> str:
        if not row or not row.char:
            return ""
        raw_bytes = row.raw_bytes
        max_width = max((col.max_width if col else 0, 2))
        str_bytes = [f"{b:02x}" for b in raw_bytes]
        sep = ["", " "][len(raw_bytes) < 4 or self._setup.static]
        return f"{sep.join(str_bytes):>{max_width}s}"

    def _render_cpnum(self, row: Row) -> str:
        if self._setup.group_cats:
            return ""

        prefix = "U+"
        result_st = pt.NOOP_STYLE
        col = self._table.get(Attribute.NUMBER)

        if row.char.is_invalid:
            result = " -- "
            prefix = "  "
            result_st = self.INVALID_STYLE
        else:
            result = self._format_cpnum_val(row, col).strip()

        max_col_width = min([6, 8][self._setup.static], col.max_width + len(prefix))
        prefix = pt.fit(prefix, max_col_width - len(result), "<", overflow="")
        return (
            pt.render(pt.Text(prefix, self.CPNUM_PFX_STYLE, result, result_st))
            + self.COLUMN_SEPARATOR
        )

    def _format_cpnum_val(self, row: Row, col: Column = None) -> str:
        if not row or not row.char or row.char.is_invalid:
            return ""
        max_width = max((col.max_width if col else 0), 2)
        return f"{row.char.cpnum:>{max_width}X}"

    def _render_char(self, row: Row) -> str:
        if self._setup.group_cats:
            return ""

        cat_st = self._styles.get(row.char.type, pt.NOOP_STYLE)
        chr_st = cat_st
        value = row.char.value
        override = self._OVERRIDE_CHARS.get(ord(value), None)
        if override:
            chr_st = override.style
        if row.char.is_ascii_letter:
            chr_st = cat_st = self.PLAIN_STYLE
        chr_st = pt.merge_styles(self.CHAR_STYLE, overwrites=[self._styles._BASE, chr_st])

        if self._setup.highlight_only_mode:
            if row.char.is_ascii_c0:
                return value
            if row.char.is_surrogate or row.char.is_invalid:
                value = "▯"
            pad = " " * bool(unicodedata.combining(value))
            return pt.render(pad + value, cat_st)

        pad = ""

        if override:
            val_len = 1
            value = override.char
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
        suffix = pt.render(" ", self.CHAR_STYLE) + "▏" + self.LTR_CHAR
        return prefix + pt.render(pad + value, chr_st) + suffix  # NO SEPARATOR

    def _render_type(self, row: Row) -> str:
        prefix = ""
        type = row.char.type
        if not type:
            return prefix
        st = self._styles.get(type, self._styles._BASE)
        return prefix + pt.render(type, st) + self.COLUMN_SEPARATOR

    def _render_type_name(self, row: Row) -> str:
        if not (type := row.char.type):
            return ""
        st = self._styles.get(type, self._styles._BASE)
        col = self._table.get(Attribute.TYPE_NAME)
        result = self._format_type_name(row, col)
        if not self._setup.static:
            result = pt.fit(result.strip(), 16)
        return pt.render(result, st) + self.COLUMN_SEPARATOR

    def _format_type_name(self, row: Row, col: Column = None) -> str:
        if not row or not row.char:
            return ""
        max_width = max((col.max_width if col else 0), 2)
        try:
            cat_name = resolve_category(row.char.type).name
        except LookupError:
            cat_name = "Binary"
        return f"{cat_name:{max_width}s}"

    def _render_name(self, row: Row) -> str:
        if self._setup.group_cats:
            return ""

        prefix = ""
        st: pt.Style = [pt.NOOP_STYLE, self.INVALID_STYLE][row.char.is_invalid]
        col = self._table.get(Attribute.NAME)
        return prefix + pt.render(self._format_name(row, col), st) + self.COLUMN_SEPARATOR

    def _format_name(self, row: Row, col: Column = None) -> str:
        if not row or not row.char:
            return ""
        max_width = max((col.max_width if col else 0), 16)
        return f"{row.char.name:{max_width}s}"

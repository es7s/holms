# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023-2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations
import io
import math
import re
import sys
import unicodedata
from collections import deque, OrderedDict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import lru_cache

import pytermor as pt

from holms.db import resolve_category, UnicodeBlock, find_block
from holms.shared import CacheInfo
from .attr import Attribute
from .cats import CategoryStyles, _cc_styles, OVERRIDE_CHARS
from .char import Char, Groups
from .opt import Options
from holms.shared.scale import format_ratio, Scale

COLUMN_SEPARATOR = " "
CHAR_PLACEHOLDER = "▯"
LTR_CHAR = "\u200e"  # to normalize the output after possible RTL switch


@dataclass
class Column:
    attr: Attribute
    max_val: int = 0
    max_width: int = 0

    def update_val(self, val) -> int:
        self.max_val = max(self.max_val, val)
        return self.max_val

    def update_width(self, width) -> int:
        if width > self.max_width:
            get_view(self.attr).reset()
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


CategorySampleCache = dict[str, Char]


class Table(OrderedDict[Attribute, Column]):
    DEFAULT_WIDTH = {
        Attribute.OFFSET: 4,
        Attribute.INDEX: 4,
        Attribute.COUNT: 4,
        Attribute.RAW: 8,
        Attribute.NUMBER: 6,
        Attribute.NAME: 16,
        Attribute.CAT: 2,
        Attribute.BLOCK: 4,
    }

    def __init__(self, data):
        super().__init__(data)
        self.index = 0
        self.offset = 0

    def set_defaults(self):
        for attr, col in self.items():
            col.update_width(self.DEFAULT_WIDTH.get(attr, 0))


class Styles:
    INDEX = pt.FrozenStyle(fg=pt.cv.GRAY_50, bg=pt.cv.BLACK)
    INDEX_ZEROS = pt.FrozenStyle(fg=pt.cv.GRAY_23, bg=pt.cv.BLACK)
    INDEX_PREFIX = pt.FrozenStyle(fg=pt.cv.GRAY_30, bg=pt.cv.BLACK)
    CPNUM_PREFIX = pt.FrozenStyle(fg=pt.cv.GRAY_30)
    RAW_PREFIX = INDEX_PREFIX
    RAW = INDEX
    CHAR = pt.FrozenStyle(fg=0xFFFFFF, bg=0)
    INVALID = pt.FrozenStyle(fg=pt.cv.GRAY_30)
    PLAIN = pt.FrozenStyle(fg=pt.cv.GRAY_50)
    TOTALS = pt.FrozenStyle(overlined=True)


@dataclass
class RunStats:
    proc_bytes: int = 0
    proc_chars: int = 0


from .view import IView, get_view, reset_views


class CliWriter:
    def __init__(self, opt: Options, buffered: bool, output: io.IOBase = None):
        self._opt = opt
        self._buffered = buffered
        self._output = output or sys.stdout

        self._buffer = deque[Row]()
        self._table = Table({a: Column(a) for a in self._opt.columns})
        if not self._buffered:
            self._table.set_defaults()
        self._groups = Groups()
        self._cat_cache = CategorySampleCache()

    def __del__(self):
        reset_views()  # drops lru caches with rendered strings
        CacheInfo().upd_from_tuple(find_block.cache_info()).debug(find_block.__qualname__)

    @staticmethod
    def get_group_key(opt: Options, char: Char) -> Char | str:
        if opt.group_cats or opt.group_super_cats:
            return CliWriter.get_effective_category(opt, char)
        return char

    @staticmethod
    def get_effective_category(opt: Options, char: Char) -> str:
        if opt.group_super_cats:
            return char.cat[0]
        return char.cat

    def write(self, chars: Iterator[Char | None]) -> RunStats:
        prev_char: Char | None = None
        dup_count = 0
        run_stats = RunStats()
        opt = self._opt

        if self._buffered:
            chars = [*chars]

        for char in chars:
            if char:
                if opt.oneline and char.value == "\n":
                    continue
                run_stats.proc_chars += 1
                run_stats.proc_bytes += char.bytelen

            if opt.group:
                if char is not None:
                    key = self.get_group_key(opt, char)
                    if key not in self._groups.keys():
                        self._groups[key] = 0
                        if not isinstance(key, Char):
                            self._cat_cache[key] = char
                    self._groups[key] += 1
                continue

            if not opt.merge:
                self._make_row(char)
                continue

            if prev_char and prev_char != char:
                self._make_row(prev_char, dup_count)
                dup_count = 0
            if prev_char == char:
                dup_count += 1
            prev_char = char

        if not self._buffered:
            return run_stats

        if opt.group:
            for key, count in self._groups.sorted():
                char = key if isinstance(key, Char) else self._cat_cache.get(key)
                self._make_row(char, count - 1)

        self._update_columns()
        for row in self._buffer:
            self._print_row(row)

        return run_stats

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
        if not self._is_row_visible(row):
            return
        rendered = self._render_row(row)
        pt.echo(rendered, nl=(not self._opt.highlight_only_mode), file=self._output)

    def _is_row_visible(self, row: Row) -> bool:
        if row.char is None:
            return False
        return True

    def _render_row(self, row: Row):
        def __iter() -> Iterable[str]:
            for attr in self._opt.columns:
                view = get_view(attr)
                col = self._table.get(attr)
                yield view.render(self._opt, row, col, self._groups)

        return pt.joine(*__iter())

    def _update_columns(self, row: Row = None):
        for attr in self._opt.columns:
            if not (col := self._table.get(attr)):
                continue

            view = get_view(attr)
            val_str = view.format(self._opt, row, col)
            if not val_str:
                continue

            width = len(val_str)
            col.update_width(width)


class RendersAddress:
    @classmethod
    def _format_address(cls, row: Row, prefix: str, val_str: str):
        suffix = [" ", "+"][row.dup_count > 0]
        _, zeros, nonzeros = re.split("^([0 ]*)(?=.)", val_str)
        return prefix, zeros, nonzeros + suffix

    @staticmethod
    @lru_cache(maxsize=1)
    def _render_template() -> str:
        text = pt.Text(
            ("%s", Styles.INDEX_PREFIX),
            ("%s", Styles.INDEX_ZEROS),
            ("%s", Styles.INDEX),
        )
        return pt.render(text) + COLUMN_SEPARATOR


class OffsetView(IView, RendersAddress):
    @staticmethod
    def attr() -> Attribute:
        return Attribute.OFFSET

    def format(self, opt: Options, row: Row, col: Column = None) -> str:
        val = row.offset if row else col.max_val
        fmt = ["x", "d"][opt.decimal_offset]

        if col is None:
            result = f"{val:{fmt}}"
            if opt.decimal_offset:
                return result
            return pt.fit(result, 2 * math.ceil(len(result) / 2), fill="0")

        fill = ["0", ""][opt.decimal_offset]
        return f"{val:{fill}{col.max_width}{fmt}}"

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if opt.group:
            return ""
        pfx = [" ", "⏨"][opt.decimal_offset]
        address_parts = self._format_address(row, pfx, self.format(opt, row, col))
        return self._render_template() % address_parts


class IndexView(IView, RendersAddress):
    @staticmethod
    def attr() -> Attribute:
        return Attribute.INDEX

    def format(self, opt: Options, row: Row, col: Column = None) -> str:
        val = row.index if row else col.max_val
        max_width = col.max_width if col else 0
        return f"{val:{max_width}d}"

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if opt.group:
            return ""
        address_parts = self._format_address(row, "#", self.format(opt, row, col))
        return self._render_template() % address_parts


class RawView(IView):
    @staticmethod
    def attr() -> Attribute:
        return Attribute.RAW

    def format(self, opt: Options, row: Row, col: Column = None) -> str:
        if not row or not row.char:
            return ""
        return self._format_bytes(opt.rigid, (*row.raw_bytes,), col.max_width if col else 0)

    @lru_cache(maxsize=256)
    def _format_bytes(self, rigid: bool, raw_bytes: tuple[int, ...], max_width=0):
        max_width = max(max_width, 2)
        str_bytes = [f"{b:02x}" for b in raw_bytes]
        sep = ["", " "][len(raw_bytes) < 4 or rigid]
        return f"{sep.join(str_bytes):>{max_width}s}"

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if opt.group_cats:
            return ""
        formatted = self.format(opt, row, col).strip()
        return self._render_bytes(opt.rigid, formatted, col.max_width)

    @lru_cache(maxsize=256)
    def _render_bytes(self, rigid: bool, formatted: str, max_width=0):
        prefix = " 0x "

        max_col_width = min([9, 14][rigid], max_width + len(prefix))
        prefix = pt.fit(prefix, max_col_width - len(formatted), "<", overflow="")
        return pt.render(pt.Text(prefix, Styles.RAW_PREFIX, formatted, Styles.RAW)) + COLUMN_SEPARATOR


class CpNumberView(IView):
    PREFIX = "U+"

    @staticmethod
    def attr() -> Attribute:
        return Attribute.NUMBER

    def format(self, opt: Options, row: Row, col: Column = None) -> str:
        if not row:
            return ""
        return self._format_char(row.char, col.max_width if col else 0)

    @lru_cache(maxsize=256)
    def _format_char(self, char: Char | None, max_width=0) -> str:
        if not char or char.is_invalid:
            return ""
        max_width = max(max_width, 2)
        return f"{char.cpnum:>{max_width}X}"

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if opt.group_cats:
            return ""
        max_width = col.max_width if col else 0
        return self._render_char(opt.rigid, row.char, max_width)

    @lru_cache(maxsize=256)
    def _render_char(self, _rigid: bool, char: Char, max_width=0) -> str:
        prefix = self.PREFIX
        result_st = pt.NOOP_STYLE

        if char.is_invalid:
            result = " -- "
            prefix = "  "
            result_st = Styles.INVALID
        else:
            result = self._format_char(char, max_width).strip()

        max_col_width = min([6, 8][_rigid], max_width + len(prefix))
        prefix = pt.fit(prefix, max_col_width - len(result), "<", overflow="")
        return pt.render(pt.Text(prefix, Styles.CPNUM_PREFIX, result, result_st)) + COLUMN_SEPARATOR


class CountView(IView):
    @staticmethod
    def attr() -> Attribute:
        return Attribute.COUNT

    def format(self, opt: Options, row: Row, col: Column = None) -> str:
        val = max((row.dup_count if row else 0), col.max_val)

        if val > 0 or opt.group:
            result = str(val + 1)
        else:
            result = " "

        if col is None:
            return result
        return pt.fit(result, max(len(result), col.max_width), ">")

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if not opt.merge:
            return ""
        val_str = self.format(opt, row, col)
        suffix = "×" if row.char else " "
        result = self._render_count(opt.group, val_str, suffix)

        if row and opt.group and row.char:
            scale_str = self._render_scale(opt.group_cats, row.char.cat, row.dup_count, grp.max, grp.sum)
            result = scale_str + result
        return result

    @lru_cache(maxsize=512)
    def _render_count(self, group: bool, formatted: str, suffix: str) -> str:
        if not formatted.strip() and not group:
            result = pt.pad(len(formatted) + 1)
        else:
            result = pt.render(pt.highlight(formatted)) + suffix
        return result + COLUMN_SEPARATOR

    @lru_cache(maxsize=512)
    def _render_scale(
        self, group_cats: bool, cat: str, count: int, max: int, sum: int
    ) -> str:
        scale_st = _cc_styles.get(cat, CategoryStyles.BASE)

        if scale_st.bg:
            scale_st = pt.Style(fg=scale_st.bg)
        scale_width = self._get_scale_width(group_cats)
        scale_label = format_ratio((count + 1) / sum)
        scale = Scale(
            (count + 1) / max,
            pt.NOOP_STYLE,
            scale_st,
            scale_width,
            use_partials=True,
            require_not_empty=True,
            label_override=scale_label,
        )
        return pt.render(scale) + COLUMN_SEPARATOR

    @staticmethod
    def _get_scale_width(group_cats: bool) -> int:
        return [3, 10][group_cats]


class CharView(IView):
    @staticmethod
    def attr() -> Attribute:
        return Attribute.CHAR

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if opt.group_cats:
            return ""

        return self._render_char(row.char, opt.highlight_only_mode)

    @lru_cache(maxsize=256)
    def _render_char(self, char: Char, highlight_only_mode: bool) -> str:
        value = char.value
        cat_st = _cc_styles.get(char.cat, pt.NOOP_STYLE)
        chr_st = cat_st

        override = None
        if not char.is_invalid:
            override = OVERRIDE_CHARS.get(char.cpnum, None)

        if override:
            chr_st = override.style
        if char.is_ascii_letter:
            chr_st = cat_st = Styles.PLAIN
        chr_st = pt.merge_styles(Styles.CHAR, overwrites=[CategoryStyles.BASE, chr_st])

        if highlight_only_mode:
            if char.is_ascii_c0:
                return value
            if char.is_surrogate or char.is_invalid:
                value = CHAR_PLACEHOLDER
            pad = " " * bool(unicodedata.combining(value))
            return pt.render(pad + value, cat_st)

        pad = ""

        if override:
            val_len = 1
            value = override.char
        elif char.should_print_placeholder:
            val_len = 1
            value = CHAR_PLACEHOLDER
        else:
            val_len = pt.get_char_width(value, block=False)
            if unicodedata.combining(value):
                pad = " "
                val_len += 1

        prefix = "▕" + pt.render(" " * (2 - max(-1, val_len)), Styles.CHAR)
        ltr_char = LTR_CHAR
        suffix = pt.render(" ", Styles.CHAR) + "▏" + ltr_char
        return prefix + pt.render(pad + value, chr_st) + suffix + COLUMN_SEPARATOR


class NameView(IView):
    @staticmethod
    def attr() -> Attribute:
        return Attribute.NAME

    def format(self, opt: Options, row: Row, col: Column = None) -> str:
        if not row or not row.char:
            return ""
        return self._format_name(row.char.name, col.max_width if col else 0)

    @lru_cache(maxsize=256)
    def _format_name(self, name: str, max_width=0):
        max_width = max(max_width, 16)
        return f"{name:{max_width}s}"

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if opt.group_cats or not row.char:
            return ""
        formatted = self.format(opt, row, col)
        return self._render_name(formatted, row.char.is_invalid)

    @lru_cache(maxsize=256)
    def _render_name(self, formatted: str, is_invalid: bool):
        if is_invalid:
            return pt.render(formatted, Styles.INVALID) + COLUMN_SEPARATOR
        return formatted + COLUMN_SEPARATOR


class CatView(IView):
    @staticmethod
    def attr() -> Attribute:
        return Attribute.CAT

    def format(self, opt: Options, row: Row, col: Column = None) -> str:
        if not row or not row.char or not opt.names:
            return ""
        max_width = max((col.max_width if col else 0), 2)
        cat = CliWriter.get_effective_category(opt, row.char)
        try:
            cat_name = resolve_category(cat).name
        except LookupError:
            cat_name = "Binary"
        return f"{cat_name:{max_width}s}"

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if not row.char:
            return ""
        cat = CliWriter.get_effective_category(opt, row.char)
        if not opt.names:
            return self._render_cat_abbr(cat)
        formatted = self.format(opt, row, col)
        return self._render_cat(opt.rigid, formatted, cat)

    @lru_cache(maxsize=64)
    def _render_cat_abbr(self, cat: str) -> str:
        prefix = ""
        if not cat:
            return prefix
        st = _cc_styles.get(cat, CategoryStyles.BASE)
        return prefix + pt.render(cat, st) + COLUMN_SEPARATOR

    @lru_cache(maxsize=64)
    def _render_cat(self, _rigid: bool, formatted: str, cat: str):
        st = _cc_styles.get(cat, CategoryStyles.BASE)
        if not _rigid:
            formatted = pt.fit(formatted.strip(), 16)
        return pt.render(formatted, st) + COLUMN_SEPARATOR


class BlockView(IView):
    @staticmethod
    def attr() -> Attribute:
        return Attribute.BLOCK

    def format(self, opt: Options, row: Row, col: Column = None) -> str:
        if not row or not row.char or not opt.names:
            return ""
        block = row.char.block
        return self._format_block(block.name if block else None, col.max_width if col else 0)

    @lru_cache(maxsize=256)
    def _format_block(self, block_name: str | None, max_width=0) -> str:
        max_width = max(max_width, 2)
        return f"{(block_name or Char.NO_VALUE):>{max_width}s}"

    def render(self, opt: Options, row: Row, col: Column = None, grp: Groups = None) -> str:
        if opt.group_cats or not row.char:
            return ""
        if not opt.names:
            return self._render_block_abbr(row.char.block)
        formatted = self.format(opt, row, col)
        return self._render_block(opt._rigid, formatted, row.char.block is not None)

    @lru_cache(maxsize=256)
    def _render_block_abbr(self, block: UnicodeBlock | None) -> str:
        s = Char.NO_VALUE
        st = Styles.INVALID
        if block:
            s = block.abbr
            st = Styles.PLAIN
        return pt.render(s.ljust(4), st)

    @lru_cache(maxsize=256)
    def _render_block(self, _rigid: bool, formatted: str, block_defined: bool):
        if not _rigid:
            formatted = pt.fit(pt.cut(formatted.strip(), 16, "<"), 16, ">")

        st = (Styles.INVALID, Styles.PLAIN)[block_defined]
        return pt.render(formatted, st) + COLUMN_SEPARATOR

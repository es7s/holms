# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from collections.abc import Iterable
from dataclasses import dataclass, field
from functools import cached_property

from .attr import Attribute

_FORMAT_ALL = [
    Attribute.OFFSET,
    Attribute.INDEX,
    Attribute.RAW,
    Attribute.NUMBER,
    Attribute.CHAR,
    Attribute.BLOCK,
    Attribute.CAT,
    Attribute.COUNT,
    Attribute.NAME,
]

_FORMAT_DEFAULT = [
    Attribute.OFFSET,
    Attribute.NUMBER,
    Attribute.CHAR,
    Attribute.CAT,
    Attribute.COUNT,
    Attribute.NAME,
]

_ATTR_EXPANDABLE = [
    Attribute.CAT,
    Attribute.BLOCK,
]


@dataclass(frozen=True)
class Options:
    _columns: list[Attribute] = field(default_factory=list)
    all_columns: bool = False
    _merge: bool = False
    group_level: int = 0
    alt_cc: bool = False
    decimal_offset: bool = False
    _rigid: bool = False
    oneline: bool = False
    _names: bool = False
    no_override: bool = False
    _no_table: bool = False

    @cached_property
    def columns(self) -> list[Attribute]:
        if not self._columns:
            if self._no_table:
                return [Attribute.CHAR]
            return [*self._columns_default]
        return self._columns

    @cached_property
    def _columns_default(self) -> Iterable[Attribute]:
        last = []
        for f in [_FORMAT_DEFAULT, _FORMAT_ALL][self.all_columns]:
            if f in _ATTR_EXPANDABLE and self.names:
                last.append(f)
                continue
            yield f
        yield from last

    @cached_property
    def merge(self) -> bool:
        return self._merge or self.group > 0

    @cached_property
    def group(self) -> bool:
        return self.group_level >= 1

    @cached_property
    def group_cats(self) -> bool:
        return self.group_level >= 2

    @cached_property
    def group_super_cats(self) -> bool:
        return self.group_level >= 3

    @cached_property
    def no_table(self) -> bool:
        return self._no_table or self.columns == [Attribute.CHAR]

    @cached_property
    def names(self) -> bool:
        return self._names or self.group_cats

    @cached_property
    def rigid(self) -> bool:
        if self.group_cats:
            return True
        return self._rigid

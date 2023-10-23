# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import unicodedata
from collections.abc import Iterable
import typing as t
import pytermor as pt

_CT = t.TypeVar("_CT", str, bytes)

#    ⇥       ⇥ ⇥        09
#    ↵       ↵ ↵        0a
#    ⤓       ⤓ ⤓        0b
#    ↡       ↡ ↡        0c
#    ⇤       ⇤ ⇤        0d
#  ␣   ·     ␣ ·        20
#    Ø       Ø Ø        00
#    ←       ← ←        08
#    →       → →        7f
#    ∌       ∌ ∌        1b


class Attribute(str, pt.ExtendedEnum):
    OFFSET = "offset"
    NUMBER = "number"
    CHAR = "char"
    COUNT = "count"
    CATEGORY = "category"
    NAME = "name"


class Char(t.Generic[_CT]):
    _SINGLE_CHAR_OVERRIDE = {
        0x0A: "Line Feed",
    }
    _ASCII_C0 = [*range(0x00, 0x20), 0x7F]
    _ASCII_C1 = [*range(0x80, 0xA0)]

    def __init__(self, c: _CT):
        if isinstance(c, int):
            c = bytes((c,))
        if len(c) > 1:
            raise ValueError(f"Char length must be exactly 1 (got {len(c)})")
        self._value: _CT = c
        self._category = self._get_category_override()
        self._name = self._get_name_override()

    def __eq__(self, other: "Char") -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._value == other._value

    def __hash__(self):
        return hash((self._value, self.__class__.__name__))

    @property
    def value(self) -> str:
        return self._value

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def cpnum(self) -> int:
        return ord(self._value)

    @property
    def category(self) -> str:
        return self._category

    @property
    def is_control(self) -> bool:
        return self._category == "Cc"

    @property
    def is_private_use(self) -> bool:
        return self._category == "Co"

    @property
    def is_unassigned(self) -> bool:
        return self._category == "Cn"

    @property
    def is_invalid(self) -> bool:
        return isinstance(self._value, bytes)

    @property
    def is_surrogate(self) -> bool:
        return 0xD800 <= ord(self._value) <= 0xDFFF

    @property
    def is_ascii_c0(self) -> bool:
        return ord(self._value) in self._ASCII_C0

    @property
    def is_ascii_c1(self) -> bool:
        return ord(self._value) in self._ASCII_C1

    def _get_name_override(self) -> str | None:
        if self.is_invalid:
            return "BINARY/NOT UTF-8"
        if self.is_surrogate:
            return "UTF-16 SURROGATE"
        if self.is_private_use:
            return "PRIVATE USE"
        if self.is_unassigned:
            return "UNASSIGNED"
        if self.is_ascii_c0:
            return f"ASCII C0 CONTROL CODE {ord(self._value):02X}"
        if self.is_ascii_c1:
            return f"ASCII C1 CONTROL CODE {ord(self._value):02X}"

        try:
            return unicodedata.name(self._value)
        except ValueError:
            return None

    def _get_category_override(self) -> str | None:
        if self.is_invalid:
            return "--"
        try:
            return unicodedata.category(self._value)
        except ValueError:
            return None


def parse(string: Iterable[t.AnyStr]) -> Iterable[Char|None]:
    for c in string:
        yield Char(c)
    yield None

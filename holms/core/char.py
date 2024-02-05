# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023-2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import unicodedata
from collections.abc import Iterable, Iterator
from functools import cached_property

import pytermor as pt
import typing as t

from holms.db import resolve_ascii_cc, find_block, UnicodeBlock

_CT = t.TypeVar("_CT", str, bytes)


class Char(t.Generic[_CT]):
    NO_VALUE = "--"

    _ASCII_C0 = [*range(0x00, 0x20), 0x7F]
    _ASCII_C1 = [*range(0x80, 0xA0)]
    _ASCII_LETTERS = [*pt.char_range("A", "Z"), *pt.char_range("a", "z")]

    @staticmethod
    def parse(string: Iterable[t.AnyStr | int]) -> Iterator[t.Optional["Char"]]:
        yield from map(Char, string)
        yield None

    def __init__(self, c: _CT):
        if isinstance(c, int):
            c = bytes((c,))
            self._bytelen = 1

        if len(c) > 1:
            raise ValueError(f"Input must be exactly 1 char long (got {len(c)})")

        if not isinstance(c, bytes):
            self._bytelen = len(c.encode(errors="surrogatepass"))
        else:
            self._bytelen = len(c)

        self._value: _CT = c

    def __eq__(self, other: "Char") -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._value == other._value

    def __hash__(self):
        return hash((self._value, self.__class__.__name__))

    def __repr__(self):
        return f"<{pt.get_qname(self)}[U+{ord(self._value):X}][{self._value}]>"

    @cached_property
    def name(self) -> str:
        if self.is_surrogate:
            return "UTF-16 SURROGATE"
        if self.is_private_use:
            return "PRIVATE USE"
        if self.is_unassigned:
            return "UNASSIGNED"
        if self.is_ascii_cc:
            cc = resolve_ascii_cc(self.cpnum)
            ccpg = "01"[bool(self.is_ascii_c1)]
            return f"ASCII C{ccpg} [{cc.abbr}] {cc.name}"
        if self.is_invalid:
            # printf '\x80'   0x 80         --  NON UTF-8 BYTE 0x80
            # printf '\u80'   0x C2 80    U+80  ASCII C1 BYTE 0x80
            return f"NON UTF-8 BYTE 0x{ord(self._value):X}"
        try:
            return unicodedata.name(self._value)
        except ValueError:
            return self.NO_VALUE

    @cached_property
    def cat(self) -> str:
        try:
            if not self.is_invalid:
                return unicodedata.category(self._value)
        except ValueError:
            pass
        return self.NO_VALUE

    @cached_property
    def block(self) -> UnicodeBlock | None:
        if self.is_invalid:
            return None
        return find_block(self.cpnum)

    @property
    def value(self) -> str:
        return self._value

    @cached_property
    def cpnum(self) -> int:
        return ord(self._value)

    @property
    def bytelen(self) -> int:
        return self._bytelen

    @cached_property
    def bytes(self) -> bytes:
        if isinstance(self._value, bytes):
            return self._value
        return self._value.encode(errors="surrogatepass")

    @cached_property
    def decomposition(self) -> str | None:
        if self.is_invalid:
            return None
        return unicodedata.decomposition(self._value)

    @cached_property
    def should_print_placeholder(self) -> bool:
        return (
            self.is_control_or_format
            or self.is_surrogate
            or self.is_invalid
            or self.is_unassigned
            or self.value.isspace()
        )

    @cached_property
    def is_control_or_format(self) -> bool:
        return self.cat in ["Cc", "Cf"]

    @cached_property
    def is_private_use(self) -> bool:
        return self.cat == "Co"

    @cached_property
    def is_unassigned(self) -> bool:
        return self.cat == "Cn"

    @cached_property
    def is_invalid(self) -> bool:
        return isinstance(self._value, bytes)

    @cached_property
    def is_surrogate(self) -> bool:
        return 0xD800 <= ord(self._value) <= 0xDFFF

    @cached_property
    def is_ascii_c0(self) -> bool:
        return not self.is_invalid and ord(self._value) in self._ASCII_C0

    @cached_property
    def is_ascii_c1(self) -> bool:
        return not self.is_invalid and ord(self._value) in self._ASCII_C1

    @cached_property
    def is_ascii_cc(self) -> bool:
        return self.is_ascii_c0 or self.is_ascii_c1

    @cached_property
    def is_ascii_letter(self) -> bool:
        return self._value in self._ASCII_LETTERS


class Groups(t.Dict[Char | str, int]):
    def sorted(self) -> list[tuple[Char | str, int]]:
        return sorted(self.items(), key=lambda kv: -kv[1])

    @cached_property
    def sum(self) -> int:
        return sum(self.values())

    @cached_property
    def max(self) -> int:
        return max(self.values())

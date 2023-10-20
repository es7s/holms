import unicodedata
from collections import deque
from collections.abc import Iterable
import typing as t

_CT = t.TypeVar("_CT", str, bytes)


class Char(t.Generic[_CT]):
    def __init__(self, c: _CT):
        if len(c) > 1:
            raise ValueError(f"Char length must be exactly 1 (got {len(c)})")
        self._char: _CT = c

        try:
            self._category: str = unicodedata.category(c)
        except:
            self._category = None

        try:
            self._name = unicodedata.name(c)
        except ValueError:
            if self.is_surrogate:
                self._name = "<UTF-16 SURROGATE>"
            elif self.is_private_use:
                self._name = "<PRIVATE USE>"
            elif self.is_unassigned:
                self._name = "<UNASSIGNED>"
            else:
                self._name = None
        except TypeError:
            self._name = "<NOT UTF-8>"
            self._category = " ?"

    @property
    def char(self) -> str:
        return self._char

    @property
    def name(self) -> str|None:
        return self._name

    @property
    def cpnum(self) -> int:
        return ord(self._char)

    @property
    def category(self) -> str:
        return self._category

    @property
    def is_control(self) -> bool:
        return self._category == 'Cc'

    @property
    def is_private_use(self) -> bool:
        return self._category == 'Co'

    @property
    def is_unassigned(self) -> bool:
        return self._category == 'Cn'

    @property
    def is_invalid(self) -> bool:
        return isinstance(self._char, bytes)

    @property
    def is_surrogate(self) -> bool:
        return 0xd800 <= ord(self._char) <= 0xdfff


def parse(string: Iterable[t.AnyStr]) -> Iterable[Char]:
    for c in string:
        yield Char(c)

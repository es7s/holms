# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import unicodedata
import pytermor as pt
import click
import typing as t

from holms.ascii_cc import resolve_ascii_cc

_CT = t.TypeVar("_CT", str, bytes)


class Attribute(str, pt.ExtendedEnum):
    OFFSET = "offset"
    INDEX = "index"
    RAW = "raw"
    NUMBER = "number"
    CHAR = "char"
    COUNT = "count"
    TYPE = "type"
    NAME = "name"
    TYPE_NAME = "typename"


_FORMAT_ALL = [
    Attribute.OFFSET,
    Attribute.INDEX,
    Attribute.NUMBER,
    Attribute.RAW,
    Attribute.CHAR,
    Attribute.COUNT,
    Attribute.TYPE,
    Attribute.NAME,
    Attribute.TYPE_NAME,
]


class Char(t.Generic[_CT]):
    _ASCII_C0 = [*range(0x00, 0x20), 0x7F]
    _ASCII_C1 = [*range(0x80, 0xA0)]
    _ASCII_LETTERS = [*pt.char_range('A', 'Z'), *pt.char_range('a', 'z')]

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
        self._type = self._get_category()
        self._name = self._get_name()

    def __eq__(self, other: "Char") -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._value == other._value

    def __hash__(self):
        return hash((self._value, self.__class__.__name__))

    def __repr__(self):
        return f'<{pt.get_qname(self)}[U+{ord(self._value):X}][{self._value}]>'

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
    def bytelen(self) -> int:
        return self._bytelen

    @property
    def bytes(self) -> bytes:
        if isinstance(self._value, bytes):
            return self._value
        return self._value.encode(errors="surrogatepass")

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, val: str):
        self._type = val

    @property
    def is_control(self) -> bool:
        return self._type == "Cc"

    @property
    def is_private_use(self) -> bool:
        return self._type == "Co"

    @property
    def is_unassigned(self) -> bool:
        return self._type == "Cn"

    @property
    def is_invalid(self) -> bool:
        return isinstance(self._value, bytes)

    @property
    def is_surrogate(self) -> bool:
        return 0xD800 <= ord(self._value) <= 0xDFFF

    @property
    def is_ascii_c0(self) -> bool:
        return not self.is_invalid and ord(self._value) in self._ASCII_C0

    @property
    def is_ascii_c1(self) -> bool:
        return not self.is_invalid and ord(self._value) in self._ASCII_C1

    @property
    def is_ascii_cc(self) -> bool:
        return self.is_ascii_c0 or self.is_ascii_c1

    @property
    def is_ascii_letter(self) -> bool:
        return self._value in self._ASCII_LETTERS

    def _get_name(self) -> str:
        if self.is_surrogate:
            return "UTF-16 SURROGATE"
        if self.is_private_use:
            return "PRIVATE USE"
        if self.is_unassigned:
            return "UNASSIGNED"
        if self.is_ascii_cc:
            cc = resolve_ascii_cc(self.cpnum)
            ccpg = '01'[bool(self.is_ascii_c1)]
            return f"ASCII C{ccpg} [{cc.abbr}] {cc.name}"
        if self.is_invalid:
            # printf '\x80'   0x 80         --  NON UTF-8 BYTE 0x80
            # printf '\u80'   0x C2 80    U+80  ASCII C1 BYTE 0x80
            return f"NON UTF-8 BYTE 0x{ord(self._value):X}"
        try:
            return unicodedata.name(self._value)
        except ValueError:
            return "--"

    def _get_category(self) -> str:
        try:
            if not self.is_invalid:
                return unicodedata.category(self._value)
        except ValueError:
            pass
        return "--"


class MultiChoice(click.Choice):
    def __init__(self, choices: t.Sequence[str], case_sensitive: bool = True, hide_choices: bool = False) -> None:
        self._hide_choices = hide_choices
        super().__init__(choices, case_sensitive)

    def convert(self, value: t.Any, *args, **kwargs) -> t.Any:
        return [super(MultiChoice, self).convert(v, *args, **kwargs) for v in value.split(",")]

    def get_metavar(self, param: click.Parameter) -> str:
        if self._hide_choices:
            return ""
        return super().get_metavar(param)

class HiddenIntRange(click.IntRange):
    def _describe_range(self) -> str:
        return ""

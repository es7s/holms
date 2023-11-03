# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations
import unicodedata
from collections.abc import Iterable
import typing as t
import pytermor as pt

_CT = t.TypeVar("_CT", str, bytes)


class Attribute(str, pt.ExtendedEnum):
    OFFSET = "offset"
    INDEX = "index"
    NUMBER = "number"
    CHAR = "char"
    COUNT = "count"
    TYPE = "type"
    NAME = "name"


class Char(t.Generic[_CT]):
    _ASCII_C0 = [*range(0x00, 0x20), 0x7F]

    _OVERRIDE_NAMES = dict[int, str]({
        0x00:  "ASCII C0 [NUL] Null",
        0x01:  "ASCII C0 [SOH] Start of Heading",
        0x02:  "ASCII C0 [STX] Start of Text",
        0x03:  "ASCII C0 [ETX] End of Text",
        0x04:  "ASCII C0 [EOT] End of Transmission",
        0x05:  "ASCII C0 [ENQ] Enquiry",
        0x06:  "ASCII C0 [ACK] Acknowledge",
        0x07:  "ASCII C0 [BEL] Bell",
        0x08:  "ASCII C0 [BS] Backspace",
        0x09:  "ASCII C0 [HT] Horizontal Tabulation",
        0x0A:  "ASCII C0 [LF] Line Feed",
        0x0B:  "ASCII C0 [VT] Vertical Tabulation",
        0x0C:  "ASCII C0 [FF] Form Feed",
        0x0D:  "ASCII C0 [CR] Carriage Return",
        0x0E:  "ASCII C0 [SO] Shift Out",
        0x0F:  "ASCII C0 [SI] Shift In",
        0x10:  "ASCII C0 [DLE] Data Link Escape",
        0x11:  "ASCII C0 [DC1] Device Control One",
        0x12:  "ASCII C0 [DC2] Device Control Two",
        0x13:  "ASCII C0 [DC3] Device Control Three",
        0x14:  "ASCII C0 [DC4] Device Control Four",
        0x15:  "ASCII C0 [NAK] Negative Acknowledge",
        0x16:  "ASCII C0 [SYN] Synchronous Idle",
        0x17:  "ASCII C0 [ETB] End of Transmission Block",
        0x18:  "ASCII C0 [CAN] Cancel",
        0x19:  "ASCII C0 [EM] End of medium",
        0x1A:  "ASCII C0 [SUB] Substitute",
        0x1B:  "ASCII C0 [ESC] Escape",
        0x1C:  "ASCII C0 [FS] File Separator",
        0x1D:  "ASCII C0 [GS] Group Separator",
        0x1E:  "ASCII C0 [RS] Record Separator",
        0x1F:  "ASCII C0 [US] Unit Separator",
        0x7F:  "ASCII C0 [DEL] Delete",
        0x80:  "ASCII C1 [PC] Padding Character",
        0x81:  "ASCII C1 [HOP] High Octet Preset",
        0x82:  "ASCII C1 [BPH] Break Permitted Here",
        0x83:  "ASCII C1 [NBH] No Break Here",
        0x84:  "ASCII C1 [IND] Index",
        0x85:  "ASCII C1 [NEL] Next Line",
        0x86:  "ASCII C1 [SSA] Start of Selected Area",
        0x87:  "ASCII C1 [ESA] End of Selected Area",
        0x88:  "ASCII C1 [HTS] Horizontal Tabulation Set",
        0x89:  "ASCII C1 [HTJ] Horizontal Tabulation with Justification",
        0x8A:  "ASCII C1 [LTS] Line Tabulation Set",
        0x8B:  "ASCII C1 [PLD] Partial Line Down",
        0x8C:  "ASCII C1 [PLU] Partial Line Up",
        0x8D:  "ASCII C1 [RI] Reverse Index",
        0x8E:  "ASCII C1 [SS2] Single-Shift Two",
        0x8F:  "ASCII C1 [SS3] Single-Shift Three",
        0x90:  "ASCII C1 [DCS] Device Control String",
        0x91:  "ASCII C1 [PU1] Private Use One",
        0x92:  "ASCII C1 [PU2] Private Use Two",
        0x93:  "ASCII C1 [STS] Set Transmit State",
        0x94:  "ASCII C1 [CCH] Cancel character",
        0x95:  "ASCII C1 [MW] Message Waiting",
        0x96:  "ASCII C1 [SPA] Start of Protected Area",
        0x97:  "ASCII C1 [EPA] End of Protected Area",
        0x98:  "ASCII C1 [SOS] Start of String",
        0x99:  "ASCII C1 [SGCI] Single Graphic Character Introducer",
        0x9A:  "ASCII C1 [SCI] Single Character Introducer",
        0x9B:  "ASCII C1 [CSI] Control Sequence Introducer",
        0x9C:  "ASCII C1 [ST] String Terminator",
        0x9D:  "ASCII C1 [OSC] Operating System Command",
        0x9E:  "ASCII C1 [PM] Private Message",
        0x9F:  "ASCII C1 [APC] Application Program Command",
    })

    _ASCII_C1 = [*range(0x80, 0xA0)]

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
        self._type = self._get_category_override()
        self._name = self._get_name_override()

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
    def type(self) -> str:
        return self._type

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
        return ord(self._value) in self._ASCII_C0

    @property
    def is_ascii_c1(self) -> bool:
        return ord(self._value) in self._ASCII_C1

    def _get_name_override(self) -> str | None:
        if self.is_invalid:
            return "BINARY / NON UTF-8 BYTE"
        if self.is_surrogate:
            return "UTF-16 SURROGATE"
        if self.is_private_use:
            return "PRIVATE USE"
        if self.is_unassigned:
            return "UNASSIGNED"
        if self.is_ascii_c0 or self.is_ascii_c1:
            if ovr := self._OVERRIDE_NAMES.get(ord(self._value), None):
                return ovr.upper()
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

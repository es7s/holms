# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023-2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from collections import namedtuple

AsciiCc = namedtuple('AsciiCc', ['abbr', 'alt', 'name'])

# fmt: off
_ASCII_CCS = dict[int, AsciiCc]({
    0x00: AsciiCc("NUL", "^@",    "NULL"),
    0x01: AsciiCc("SOH", "^A",    "START OF HEADING"),
    0x02: AsciiCc("STX", "^B",    "START OF TEXT"),
    0x03: AsciiCc("ETX", "^C",    "END OF TEXT"),
    0x04: AsciiCc("EOT", "^D",    "END OF TRANSMISSION"),
    0x05: AsciiCc("ENQ", "^E",    "ENQUIRY"),
    0x06: AsciiCc("ACK", "^F",    "ACKNOWLEDGE"),
    0x07: AsciiCc("BEL", "^G",    "BELL"),
    0x08: AsciiCc("BS",  "^H",    "BACKSPACE"),
    0x09: AsciiCc("HT",  "^I",    "HORIZONTAL TABULATION"),
    0x0A: AsciiCc("LF",  "^J",    "LINE FEED"),
    0x0B: AsciiCc("VT",  "^K",    "VERTICAL TABULATION"),
    0x0C: AsciiCc("FF",  "^L",    "FORM FEED"),
    0x0D: AsciiCc("CR",  "^M",    "CARRIAGE RETURN"),
    0x0E: AsciiCc("SO",  "^N",    "SHIFT OUT"),
    0x0F: AsciiCc("SI",  "^O",    "SHIFT IN"),
    0x10: AsciiCc("DLE", "^P",    "DATA LINK ESCAPE"),
    0x11: AsciiCc("DC1", "^Q",    "DEVICE CONTROL ONE"),
    0x12: AsciiCc("DC2", "^R",    "DEVICE CONTROL TWO"),
    0x13: AsciiCc("DC3", "^S",    "DEVICE CONTROL THREE"),
    0x14: AsciiCc("DC4", "^T",    "DEVICE CONTROL FOUR"),
    0x15: AsciiCc("NAK", "^U",    "NEGATIVE ACKNOWLEDGE"),
    0x16: AsciiCc("SYN", "^V",    "SYNCHRONOUS IDLE"),
    0x17: AsciiCc("ETB", "^W",    "END OF TRANSMISSION BLOCK"),
    0x18: AsciiCc("CAN", "^X",    "CANCEL"),
    0x19: AsciiCc("EM",  "^Y",    "END OF MEDIUM"),
    0x1A: AsciiCc("SUB", "^Z",    "SUBSTITUTE"),
    0x1B: AsciiCc("ESC", "^[",    "ESCAPE"),
    0x1C: AsciiCc("FS",  "^\\",   "FILE SEPARATOR"),
    0x1D: AsciiCc("GS",  "^]",    "GROUP SEPARATOR"),
    0x1E: AsciiCc("RS",  "^^",    "RECORD SEPARATOR"),
    0x1F: AsciiCc("US",  "^_",    "UNIT SEPARATOR"),
    0x7F: AsciiCc("DEL", "^?",    "DELETE"),
    0x80: AsciiCc("PC",  "\\200", "PADDING CHARACTER"),
    0x81: AsciiCc("HOP", "\\201", "HIGH OCTET PRESET"),
    0x82: AsciiCc("BPH", "\\202", "BREAK PERMITTED HERE"),
    0x83: AsciiCc("NBH", "\\203", "NO BREAK HERE"),
    0x84: AsciiCc("IND", "\\204", "INDEX"),
    0x85: AsciiCc("NEL", "\\205", "NEXT LINE"),
    0x86: AsciiCc("SSA", "\\206", "START OF SELECTED AREA"),
    0x87: AsciiCc("ESA", "\\207", "END OF SELECTED AREA"),
    0x88: AsciiCc("HTS", "\\210", "HORIZONTAL TABULATION SET"),
    0x89: AsciiCc("HTJ", "\\211", "HORIZONTAL TABULATION WITH JUSTIFICATION"),
    0x8A: AsciiCc("LTS", "\\212", "LINE TABULATION SET"),
    0x8B: AsciiCc("PLD", "\\213", "PARTIAL LINE DOWN"),
    0x8C: AsciiCc("PLU", "\\214", "PARTIAL LINE UP"),
    0x8D: AsciiCc("RI",  "\\215", "REVERSE INDEX"),
    0x8E: AsciiCc("SS2", "\\216", "SINGLE-SHIFT TWO"),
    0x8F: AsciiCc("SS3", "\\217", "SINGLE-SHIFT THREE"),
    0x90: AsciiCc("DCS", "\\220", "DEVICE CONTROL STRING"),
    0x91: AsciiCc("PU1", "\\221", "PRIVATE USE ONE"),
    0x92: AsciiCc("PU2", "\\222", "PRIVATE USE TWO"),
    0x93: AsciiCc("STS", "\\223", "SET TRANSMIT STATE"),
    0x94: AsciiCc("CCH", "\\224", "CANCEL CHARACTER"),
    0x95: AsciiCc("MW",  "\\225", "MESSAGE WAITING"),
    0x96: AsciiCc("SPA", "\\226", "START OF PROTECTED AREA"),
    0x97: AsciiCc("EPA", "\\227", "END OF PROTECTED AREA"),
    0x98: AsciiCc("SOS", "\\230", "START OF STRING"),
    0x99: AsciiCc("SGCI","\\231", "SINGLE GRAPHIC CHARACTER INTRODUCER"),
    0x9A: AsciiCc("SCI", "\\232", "SINGLE CHARACTER INTRODUCER"),
    0x9B: AsciiCc("CSI", "\\233", "CONTROL SEQUENCE INTRODUCER"),
    0x9C: AsciiCc("ST",  "\\234", "STRING TERMINATOR"),
    0x9D: AsciiCc("OSC", "\\235", "OPERATING SYSTEM COMMAND"),
    0x9E: AsciiCc("PM",  "\\236", "PRIVATE MESSAGE"),
    0x9F: AsciiCc("APC", "\\237", "APPLICATION PROGRAM COMMAND"),
})
# fmt: on


def resolve_ascii_cc(value: int) -> AsciiCc:
    if cc := _ASCII_CCS.get(value, None):
        return cc
    raise LookupError(f"Invalid ASCII control code: {value:X}")

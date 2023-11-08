# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

from collections import namedtuple

AsciiCc = namedtuple('AsciiCc', ['abbr', 'name'])


_ASCII_CCS = dict[int, AsciiCc]({
    0x00:  AsciiCc("NUL", "NULL"),
    0x01:  AsciiCc("SOH", "START OF HEADING"),
    0x02:  AsciiCc("STX", "START OF TEXT"),
    0x03:  AsciiCc("ETX", "END OF TEXT"),
    0x04:  AsciiCc("EOT", "END OF TRANSMISSION"),
    0x05:  AsciiCc("ENQ", "ENQUIRY"),
    0x06:  AsciiCc("ACK", "ACKNOWLEDGE"),
    0x07:  AsciiCc("BEL", "BELL"),
    0x08:  AsciiCc("BS", "BACKSPACE"),
    0x09:  AsciiCc("HT", "HORIZONTAL TABULATION"),
    0x0A:  AsciiCc("LF", "LINE FEED"),
    0x0B:  AsciiCc("VT", "VERTICAL TABULATION"),
    0x0C:  AsciiCc("FF", "FORM FEED"),
    0x0D:  AsciiCc("CR", "CARRIAGE RETURN"),
    0x0E:  AsciiCc("SO", "SHIFT OUT"),
    0x0F:  AsciiCc("SI", "SHIFT IN"),
    0x10:  AsciiCc("DLE", "DATA LINK ESCAPE"),
    0x11:  AsciiCc("DC1", "DEVICE CONTROL ONE"),
    0x12:  AsciiCc("DC2", "DEVICE CONTROL TWO"),
    0x13:  AsciiCc("DC3", "DEVICE CONTROL THREE"),
    0x14:  AsciiCc("DC4", "DEVICE CONTROL FOUR"),
    0x15:  AsciiCc("NAK", "NEGATIVE ACKNOWLEDGE"),
    0x16:  AsciiCc("SYN", "SYNCHRONOUS IDLE"),
    0x17:  AsciiCc("ETB", "END OF TRANSMISSION BLOCK"),
    0x18:  AsciiCc("CAN", "CANCEL"),
    0x19:  AsciiCc("EM", "END OF MEDIUM"),
    0x1A:  AsciiCc("SUB", "SUBSTITUTE"),
    0x1B:  AsciiCc("ESC", "ESCAPE"),
    0x1C:  AsciiCc("FS", "FILE SEPARATOR"),
    0x1D:  AsciiCc("GS", "GROUP SEPARATOR"),
    0x1E:  AsciiCc("RS", "RECORD SEPARATOR"),
    0x1F:  AsciiCc("US", "UNIT SEPARATOR"),
    0x7F:  AsciiCc("DEL", "DELETE"),
    0x80:  AsciiCc("PC", "PADDING CHARACTER"),
    0x81:  AsciiCc("HOP", "HIGH OCTET PRESET"),
    0x82:  AsciiCc("BPH", "BREAK PERMITTED HERE"),
    0x83:  AsciiCc("NBH", "NO BREAK HERE"),
    0x84:  AsciiCc("IND", "INDEX"),
    0x85:  AsciiCc("NEL", "NEXT LINE"),
    0x86:  AsciiCc("SSA", "START OF SELECTED AREA"),
    0x87:  AsciiCc("ESA", "END OF SELECTED AREA"),
    0x88:  AsciiCc("HTS", "HORIZONTAL TABULATION SET"),
    0x89:  AsciiCc("HTJ", "HORIZONTAL TABULATION WITH JUSTIFICATION"),
    0x8A:  AsciiCc("LTS", "LINE TABULATION SET"),
    0x8B:  AsciiCc("PLD", "PARTIAL LINE DOWN"),
    0x8C:  AsciiCc("PLU", "PARTIAL LINE UP"),
    0x8D:  AsciiCc("RI", "REVERSE INDEX"),
    0x8E:  AsciiCc("SS2", "SINGLE-SHIFT TWO"),
    0x8F:  AsciiCc("SS3", "SINGLE-SHIFT THREE"),
    0x90:  AsciiCc("DCS", "DEVICE CONTROL STRING"),
    0x91:  AsciiCc("PU1", "PRIVATE USE ONE"),
    0x92:  AsciiCc("PU2", "PRIVATE USE TWO"),
    0x93:  AsciiCc("STS", "SET TRANSMIT STATE"),
    0x94:  AsciiCc("CCH", "CANCEL CHARACTER"),
    0x95:  AsciiCc("MW", "MESSAGE WAITING"),
    0x96:  AsciiCc("SPA", "START OF PROTECTED AREA"),
    0x97:  AsciiCc("EPA", "END OF PROTECTED AREA"),
    0x98:  AsciiCc("SOS", "START OF STRING"),
    0x99:  AsciiCc("SGCI", "SINGLE GRAPHIC CHARACTER INTRODUCER"),
    0x9A:  AsciiCc("SCI", "SINGLE CHARACTER INTRODUCER"),
    0x9B:  AsciiCc("CSI", "CONTROL SEQUENCE INTRODUCER"),
    0x9C:  AsciiCc("ST", "STRING TERMINATOR"),
    0x9D:  AsciiCc("OSC", "OPERATING SYSTEM COMMAND"),
    0x9E:  AsciiCc("PM", "PRIVATE MESSAGE"),
    0x9F:  AsciiCc("APC", "APPLICATION PROGRAM COMMAND"),
})


def resolve_ascii_cc(value: int) -> AsciiCc:
    if cc := _ASCII_CCS.get(value, None):
        return cc
    raise LookupError(f"Invalid ASCII control code: {value:X}")

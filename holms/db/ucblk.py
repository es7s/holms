# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

from bisect import bisect_right
from functools import lru_cache, cache
from operator import attrgetter
from typing import TypeVar

import pytermor as pt

_KT = TypeVar("_KT", int, float, str)
_VT = TypeVar("_VT")


class UnicodeBlock:
    def __init__(self, start: int, end: int, abbr: str, name: str):
        self.start = start
        self.end = end
        self.abbr = abbr
        self.name = name

    def __repr__(self):
        return f"<{pt.get_qname(self)}[{self.start:06X}-{self.end:06X}:{self.abbr}:{self.name}]>"


# fmt: off
_BLOCKS: list[UnicodeBlock] = [
    # @AUTOUPDATE_START
    UnicodeBlock( 0x0000,  0x007F,  'BaL', "Basic Latin"),
    UnicodeBlock( 0x0080,  0x00FF, 'La1ˢ', "Latin-1 Supplement"),
    UnicodeBlock( 0x0100,  0x017F, 'Latᵃ', "Latin Extended-A"),
    UnicodeBlock( 0x0180,  0x024F, 'Latᵇ', "Latin Extended-B"),
    UnicodeBlock( 0x0250,  0x02AF,  'IPA', "IPA Extensions"),
    UnicodeBlock( 0x02B0,  0x02FF,  'SML', "Spacing Modifier Letters"),
    UnicodeBlock( 0x0300,  0x036F,  'CDM', "Combining Diacritical Marks"),
    UnicodeBlock( 0x0370,  0x03FF,  'GrC', "Greek and Coptic"),
    UnicodeBlock( 0x0400,  0x04FF,  'Cyr', "Cyrillic"),
    UnicodeBlock( 0x0500,  0x052F, 'Cyrˢ', "Cyrillic Supplement"),
    UnicodeBlock( 0x0530,  0x058F,  'Arm', "Armenian"),
    UnicodeBlock( 0x0590,  0x05FF,  'Heb', "Hebrew"),
    UnicodeBlock( 0x0600,  0x06FF,  'Ara', "Arabic"),
    UnicodeBlock( 0x0700,  0x074F,  'Syr', "Syriac"),
    UnicodeBlock( 0x0750,  0x077F, 'Araˢ', "Arabic Supplement"),
    UnicodeBlock( 0x0780,  0x07BF,  'Thn', "Thaana"),
    UnicodeBlock( 0x07C0,  0x07FF,  'NKo', "NKo"),
    UnicodeBlock( 0x0800,  0x083F,  'Sam', "Samaritan"),
    UnicodeBlock( 0x0840,  0x085F,  'Man', "Mandaic"),
    UnicodeBlock( 0x0860,  0x086F, 'Syrˢ', "Syriac Supplement"),
    UnicodeBlock( 0x0870,  0x089F, 'Araᵇ', "Arabic Extended-B"),
    UnicodeBlock( 0x08A0,  0x08FF, 'Araᵃ', "Arabic Extended-A"),
    UnicodeBlock( 0x0900,  0x097F,  'Dev', "Devanagari"),
    UnicodeBlock( 0x0980,  0x09FF,  'Ben', "Bengali"),
    UnicodeBlock( 0x0A00,  0x0A7F,  'Gur', "Gurmukhi"),
    UnicodeBlock( 0x0A80,  0x0AFF,  'Guj', "Gujarati"),
    UnicodeBlock( 0x0B00,  0x0B7F,  'Ori', "Oriya"),
    UnicodeBlock( 0x0B80,  0x0BFF,  'Tam', "Tamil"),
    UnicodeBlock( 0x0C00,  0x0C7F,  'Tel', "Telugu"),
    UnicodeBlock( 0x0C80,  0x0CFF,  'Knn', "Kannada"),
    UnicodeBlock( 0x0D00,  0x0D7F,  'Mal', "Malayalam"),
    UnicodeBlock( 0x0D80,  0x0DFF,  'Sin', "Sinhala"),
    UnicodeBlock( 0x0E00,  0x0E7F,  'Tha', "Thai"),
    UnicodeBlock( 0x0E80,  0x0EFF,  'Lao', "Lao"),
    UnicodeBlock( 0x0F00,  0x0FFF,  'Tib', "Tibetan"),
    UnicodeBlock( 0x1000,  0x109F,  'Mya', "Myanmar"),
    UnicodeBlock( 0x10A0,  0x10FF,  'Geo', "Georgian"),
    UnicodeBlock( 0x1100,  0x11FF,  'HaJ', "Hangul Jamo"),
    UnicodeBlock( 0x1200,  0x137F,  'Eth', "Ethiopic"),
    UnicodeBlock( 0x1380,  0x139F, 'Ethˢ', "Ethiopic Supplement"),
    UnicodeBlock( 0x13A0,  0x13FF,  'Che', "Cherokee"),
    UnicodeBlock( 0x1400,  0x167F,  'UCA', "Unified Canadian Aboriginal Syllabics"),
    UnicodeBlock( 0x1680,  0x169F,  'Ogh', "Ogham"),
    UnicodeBlock( 0x16A0,  0x16FF,  'Run', "Runic"),
    UnicodeBlock( 0x1700,  0x171F,  'Tgl', "Tagalog"),
    UnicodeBlock( 0x1720,  0x173F,  'Han', "Hanunoo"),
    UnicodeBlock( 0x1740,  0x175F,  'Buh', "Buhid"),
    UnicodeBlock( 0x1760,  0x177F,  'Tgb', "Tagbanwa"),
    UnicodeBlock( 0x1780,  0x17FF,  'Khm', "Khmer"),
    UnicodeBlock( 0x1800,  0x18AF,  'Mon', "Mongolian"),
    UnicodeBlock( 0x18B0,  0x18FF, 'UCAˣ', "Unified Canadian Aboriginal Syllabics Extended"),
    UnicodeBlock( 0x1900,  0x194F,  'Lim', "Limbu"),
    UnicodeBlock( 0x1950,  0x197F,  'TaL', "Tai Le"),
    UnicodeBlock( 0x1980,  0x19DF,  'NTL', "New Tai Lue"),
    UnicodeBlock( 0x19E0,  0x19FF, 'Khme', "Khmer Symbols"),
    UnicodeBlock( 0x1A00,  0x1A1F,  'Bug', "Buginese"),
    UnicodeBlock( 0x1A20,  0x1AAF,  'TaT', "Tai Tham"),
    UnicodeBlock( 0x1AB0,  0x1AFF, 'CDMˣ', "Combining Diacritical Marks Extended"),
    UnicodeBlock( 0x1B00,  0x1B7F,  'Bal', "Balinese"),
    UnicodeBlock( 0x1B80,  0x1BBF,  'Sun', "Sundanese"),
    UnicodeBlock( 0x1BC0,  0x1BFF,  'Bat', "Batak"),
    UnicodeBlock( 0x1C00,  0x1C4F,  'Lep', "Lepcha"),
    UnicodeBlock( 0x1C50,  0x1C7F,  'OlC', "Ol Chiki"),
    UnicodeBlock( 0x1C80,  0x1C8F, 'Cyrᶜ', "Cyrillic Extended-C"),
    UnicodeBlock( 0x1C90,  0x1CBF, 'Geoˣ', "Georgian Extended"),
    UnicodeBlock( 0x1CC0,  0x1CCF, 'Sunˢ', "Sundanese Supplement"),
    UnicodeBlock( 0x1CD0,  0x1CFF,  'VeE', "Vedic Extensions"),
    UnicodeBlock( 0x1D00,  0x1D7F,  'PhE', "Phonetic Extensions"),
    UnicodeBlock( 0x1D80,  0x1DBF, 'PhEˢ', "Phonetic Extensions Supplement"),
    UnicodeBlock( 0x1DC0,  0x1DFF, 'CDMˢ', "Combining Diacritical Marks Supplement"),
    UnicodeBlock( 0x1E00,  0x1EFF, 'Lat⁺', "Latin Extended Additional"),
    UnicodeBlock( 0x1F00,  0x1FFF, 'Greˣ', "Greek Extended"),
    UnicodeBlock( 0x2000,  0x206F,  'GeP', "General Punctuation"),
    UnicodeBlock( 0x2070,  0x209F,  'SuS', "Superscripts and Subscripts"),
    UnicodeBlock( 0x20A0,  0x20CF,  'Cur', "Currency Symbols"),
    UnicodeBlock( 0x20D0,  0x20FF, 'CoDM', "Combining Diacritical Marks for Symbols"),
    UnicodeBlock( 0x2100,  0x214F,  'Let', "Letterlike Symbols"),
    UnicodeBlock( 0x2150,  0x218F,  'NuF', "Number Forms"),
    UnicodeBlock( 0x2190,  0x21FF,  'Arr', "Arrows"),
    UnicodeBlock( 0x2200,  0x22FF,  'MaO', "Mathematical Operators"),
    UnicodeBlock( 0x2300,  0x23FF,  'MiT', "Miscellaneous Technical"),
    UnicodeBlock( 0x2400,  0x243F,  'CoP', "Control Pictures"),
    UnicodeBlock( 0x2440,  0x245F,  'OCR', "Optical Character Recognition"),
    UnicodeBlock( 0x2460,  0x24FF,  'EnA', "Enclosed Alphanumerics"),
    UnicodeBlock( 0x2500,  0x257F,  'BoD', "Box Drawing"),
    UnicodeBlock( 0x2580,  0x259F,  'BlE', "Block Elements"),
    UnicodeBlock( 0x25A0,  0x25FF,  'GeS', "Geometric Shapes"),
    UnicodeBlock( 0x2600,  0x26FF,  'Mis', "Miscellaneous Symbols"),
    UnicodeBlock( 0x2700,  0x27BF,  'Din', "Dingbats"),
    UnicodeBlock( 0x27C0,  0x27EF, 'MiMᵃ', "Miscellaneous Mathematical Symbols-A"),
    UnicodeBlock( 0x27F0,  0x27FF, 'Arrᵃ', "Supplemental Arrows-A"),
    UnicodeBlock( 0x2800,  0x28FF,  'BrP', "Braille Patterns"),
    UnicodeBlock( 0x2900,  0x297F, 'Arrᵇ', "Supplemental Arrows-B"),
    UnicodeBlock( 0x2980,  0x29FF, 'MiMᵇ', "Miscellaneous Mathematical Symbols-B"),
    UnicodeBlock( 0x2A00,  0x2AFF, 'MaOˢ', "Supplemental Mathematical Operators"),
    UnicodeBlock( 0x2B00,  0x2BFF,  'MSA', "Miscellaneous Symbols and Arrows"),
    UnicodeBlock( 0x2C00,  0x2C5F,  'Gla', "Glagolitic"),
    UnicodeBlock( 0x2C60,  0x2C7F, 'Latᶜ', "Latin Extended-C"),
    UnicodeBlock( 0x2C80,  0x2CFF,  'Cop', "Coptic"),
    UnicodeBlock( 0x2D00,  0x2D2F, 'Geoˢ', "Georgian Supplement"),
    UnicodeBlock( 0x2D30,  0x2D7F,  'Tif', "Tifinagh"),
    UnicodeBlock( 0x2D80,  0x2DDF, 'Ethˣ', "Ethiopic Extended"),
    UnicodeBlock( 0x2DE0,  0x2DFF, 'Cyrᵃ', "Cyrillic Extended-A"),
    UnicodeBlock( 0x2E00,  0x2E7F, 'Punˢ', "Supplemental Punctuation"),
    UnicodeBlock( 0x2E80,  0x2EFF, 'CJRˢ', "CJK Radicals Supplement"),
    UnicodeBlock( 0x2F00,  0x2FDF,  'KaR', "Kangxi Radicals"),
    UnicodeBlock( 0x2FF0,  0x2FFF,  'IDC', "Ideographic Description Characters"),
    UnicodeBlock( 0x3000,  0x303F, 'CJSP', "CJK Symbols and Punctuation"),
    UnicodeBlock( 0x3040,  0x309F,  'Hir', "Hiragana"),
    UnicodeBlock( 0x30A0,  0x30FF,  'Kat', "Katakana"),
    UnicodeBlock( 0x3100,  0x312F,  'Bop', "Bopomofo"),
    UnicodeBlock( 0x3130,  0x318F,  'HCJ', "Hangul Compatibility Jamo"),
    UnicodeBlock( 0x3190,  0x319F,  'Kan', "Kanbun"),
    UnicodeBlock( 0x31A0,  0x31BF, 'Bopˣ', "Bopomofo Extended"),
    UnicodeBlock( 0x31C0,  0x31EF,  'CJS', "CJK Strokes"),
    UnicodeBlock( 0x31F0,  0x31FF,  'KPE', "Katakana Phonetic Extensions"),
    UnicodeBlock( 0x3200,  0x32FF,  'ECJ', "Enclosed CJK Letters and Months"),
    UnicodeBlock( 0x3300,  0x33FF,  'CJC', "CJK Compatibility"),
    UnicodeBlock( 0x3400,  0x4DBF, 'CJUᵃ', "CJK Unified Ideographs Extension A"),
    UnicodeBlock( 0x4DC0,  0x4DFF,  'YiH', "Yijing Hexagram Symbols"),
    UnicodeBlock( 0x4E00,  0x9FFF,  'CJU', "CJK Unified Ideographs"),
    UnicodeBlock( 0xA000,  0xA48F,  'YiS', "Yi Syllables"),
    UnicodeBlock( 0xA490,  0xA4CF,  'YiR', "Yi Radicals"),
    UnicodeBlock( 0xA4D0,  0xA4FF,  'Lis', "Lisu"),
    UnicodeBlock( 0xA500,  0xA63F,  'Vai', "Vai"),
    UnicodeBlock( 0xA640,  0xA69F, 'Cyrᵇ', "Cyrillic Extended-B"),
    UnicodeBlock( 0xA6A0,  0xA6FF,  'Bam', "Bamum"),
    UnicodeBlock( 0xA700,  0xA71F,  'MTL', "Modifier Tone Letters"),
    UnicodeBlock( 0xA720,  0xA7FF, 'Latᵈ', "Latin Extended-D"),
    UnicodeBlock( 0xA800,  0xA82F,  'SyN', "Syloti Nagri"),
    UnicodeBlock( 0xA830,  0xA83F,  'CIN', "Common Indic Number Forms"),
    UnicodeBlock( 0xA840,  0xA87F,  'Pha', "Phags-pa"),
    UnicodeBlock( 0xA880,  0xA8DF,  'Sau', "Saurashtra"),
    UnicodeBlock( 0xA8E0,  0xA8FF, 'Devˣ', "Devanagari Extended"),
    UnicodeBlock( 0xA900,  0xA92F,  'KaL', "Kayah Li"),
    UnicodeBlock( 0xA930,  0xA95F,  'Rej', "Rejang"),
    UnicodeBlock( 0xA960,  0xA97F, 'HaJᵃ', "Hangul Jamo Extended-A"),
    UnicodeBlock( 0xA980,  0xA9DF,  'Jav', "Javanese"),
    UnicodeBlock( 0xA9E0,  0xA9FF, 'Myaᵇ', "Myanmar Extended-B"),
    UnicodeBlock( 0xAA00,  0xAA5F,  'Cha', "Cham"),
    UnicodeBlock( 0xAA60,  0xAA7F, 'Myaᵃ', "Myanmar Extended-A"),
    UnicodeBlock( 0xAA80,  0xAADF,  'TaV', "Tai Viet"),
    UnicodeBlock( 0xAAE0,  0xAAFF,  'MME', "Meetei Mayek Extensions"),
    UnicodeBlock( 0xAB00,  0xAB2F, 'Ethᵃ', "Ethiopic Extended-A"),
    UnicodeBlock( 0xAB30,  0xAB6F, 'Latᵉ', "Latin Extended-E"),
    UnicodeBlock( 0xAB70,  0xABBF, 'Cheˢ', "Cherokee Supplement"),
    UnicodeBlock( 0xABC0,  0xABFF,  'MeM', "Meetei Mayek"),
    UnicodeBlock( 0xAC00,  0xD7AF,  'HaS', "Hangul Syllables"),
    UnicodeBlock( 0xD7B0,  0xD7FF, 'HaJᵇ', "Hangul Jamo Extended-B"),
    UnicodeBlock( 0xD800,  0xDB7F, 'Hig$', "High Surrogates"),
    UnicodeBlock( 0xDB80,  0xDBFF, 'HPU$', "High Private Use Surrogates"),
    UnicodeBlock( 0xDC00,  0xDFFF, 'Low$', "Low Surrogates"),
    UnicodeBlock( 0xE000,  0xF8FF,  'PUA', "Private Use Area"),
    UnicodeBlock( 0xF900,  0xFAFF, 'CJCI', "CJK Compatibility Ideographs"),
    UnicodeBlock( 0xFB00,  0xFB4F,  'APF', "Alphabetic Presentation Forms"),
    UnicodeBlock( 0xFB50,  0xFDFF, 'APFᵃ', "Arabic Presentation Forms-A"),
    UnicodeBlock( 0xFE00,  0xFE0F,  'VaS', "Variation Selectors"),
    UnicodeBlock( 0xFE10,  0xFE1F,  'VeF', "Vertical Forms"),
    UnicodeBlock( 0xFE20,  0xFE2F,  'CHM', "Combining Half Marks"),
    UnicodeBlock( 0xFE30,  0xFE4F, 'CJCF', "CJK Compatibility Forms"),
    UnicodeBlock( 0xFE50,  0xFE6F,  'SFV', "Small Form Variants"),
    UnicodeBlock( 0xFE70,  0xFEFF, 'APFᵇ', "Arabic Presentation Forms-B"),
    UnicodeBlock( 0xFF00,  0xFFEF,  'HFF', "Halfwidth and Fullwidth Forms"),
    UnicodeBlock( 0xFFF0,  0xFFFF,  'Spe', "Specials"),
    UnicodeBlock(0x10000, 0x1007F,  'LBS', "Linear B Syllabary"),
    UnicodeBlock(0x10080, 0x100FF,  'LBI', "Linear B Ideograms"),
    UnicodeBlock(0x10100, 0x1013F,  'AeN', "Aegean Numbers"),
    UnicodeBlock(0x10140, 0x1018F,  'AGN', "Ancient Greek Numbers"),
    UnicodeBlock(0x10190, 0x101CF,  'Anc', "Ancient Symbols"),
    UnicodeBlock(0x101D0, 0x101FF,  'PhD', "Phaistos Disc"),
    UnicodeBlock(0x10280, 0x1029F,  'Lyc', "Lycian"),
    UnicodeBlock(0x102A0, 0x102DF,  'Car', "Carian"),
    UnicodeBlock(0x102E0, 0x102FF,  'CEN', "Coptic Epact Numbers"),
    UnicodeBlock(0x10300, 0x1032F, 'Itaₒ', "Old Italic"),
    UnicodeBlock(0x10330, 0x1034F,  'Got', "Gothic"),
    UnicodeBlock(0x10350, 0x1037F, 'Perₒ', "Old Permic"),
    UnicodeBlock(0x10380, 0x1039F,  'Uga', "Ugaritic"),
    UnicodeBlock(0x103A0, 0x103DF, 'Prsₒ', "Old Persian"),
    UnicodeBlock(0x10400, 0x1044F,  'Des', "Deseret"),
    UnicodeBlock(0x10450, 0x1047F,  'Sha', "Shavian"),
    UnicodeBlock(0x10480, 0x104AF,  'Osm', "Osmanya"),
    UnicodeBlock(0x104B0, 0x104FF,  'Osa', "Osage"),
    UnicodeBlock(0x10500, 0x1052F,  'Elb', "Elbasan"),
    UnicodeBlock(0x10530, 0x1056F,  'CaA', "Caucasian Albanian"),
    UnicodeBlock(0x10570, 0x105BF,  'Vit', "Vithkuqi"),
    UnicodeBlock(0x10600, 0x1077F,  'LiA', "Linear A"),
    UnicodeBlock(0x10780, 0x107BF, 'Latᶠ', "Latin Extended-F"),
    UnicodeBlock(0x10800, 0x1083F,  'CyS', "Cypriot Syllabary"),
    UnicodeBlock(0x10840, 0x1085F,  'ImA', "Imperial Aramaic"),
    UnicodeBlock(0x10860, 0x1087F,  'Pal', "Palmyrene"),
    UnicodeBlock(0x10880, 0x108AF,  'Nab', "Nabataean"),
    UnicodeBlock(0x108E0, 0x108FF,  'Hat', "Hatran"),
    UnicodeBlock(0x10900, 0x1091F,  'Pho', "Phoenician"),
    UnicodeBlock(0x10920, 0x1093F,  'Lyd', "Lydian"),
    UnicodeBlock(0x10980, 0x1099F,  'MeH', "Meroitic Hieroglyphs"),
    UnicodeBlock(0x109A0, 0x109FF,  'MeC', "Meroitic Cursive"),
    UnicodeBlock(0x10A00, 0x10A5F,  'Kha', "Kharoshthi"),
    UnicodeBlock(0x10A60, 0x10A7F, 'SoAₒ', "Old South Arabian"),
    UnicodeBlock(0x10A80, 0x10A9F, 'NoAₒ', "Old North Arabian"),
    UnicodeBlock(0x10AC0, 0x10AFF,  'Mnc', "Manichaean"),
    UnicodeBlock(0x10B00, 0x10B3F,  'Ave', "Avestan"),
    UnicodeBlock(0x10B40, 0x10B5F, 'InsP', "Inscriptional Parthian"),
    UnicodeBlock(0x10B60, 0x10B7F,  'InP', "Inscriptional Pahlavi"),
    UnicodeBlock(0x10B80, 0x10BAF,  'PsP', "Psalter Pahlavi"),
    UnicodeBlock(0x10C00, 0x10C4F, 'Turₒ', "Old Turkic"),
    UnicodeBlock(0x10C80, 0x10CFF, 'Hunₒ', "Old Hungarian"),
    UnicodeBlock(0x10D00, 0x10D3F,  'HaR', "Hanifi Rohingya"),
    UnicodeBlock(0x10E60, 0x10E7F,  'RuN', "Rumi Numeral Symbols"),
    UnicodeBlock(0x10E80, 0x10EBF,  'Yez', "Yezidi"),
    UnicodeBlock(0x10EC0, 0x10EFF, 'Araᶜ', "Arabic Extended-C"),
    UnicodeBlock(0x10F00, 0x10F2F, 'Sogₒ', "Old Sogdian"),
    UnicodeBlock(0x10F30, 0x10F6F,  'Sog', "Sogdian"),
    UnicodeBlock(0x10F70, 0x10FAF, 'Uygₒ', "Old Uyghur"),
    UnicodeBlock(0x10FB0, 0x10FDF,  'Cho', "Chorasmian"),
    UnicodeBlock(0x10FE0, 0x10FFF,  'Ely', "Elymaic"),
    UnicodeBlock(0x11000, 0x1107F,  'Bra', "Brahmi"),
    UnicodeBlock(0x11080, 0x110CF,  'Kai', "Kaithi"),
    UnicodeBlock(0x110D0, 0x110FF,  'SoS', "Sora Sompeng"),
    UnicodeBlock(0x11100, 0x1114F,  'Chk', "Chakma"),
    UnicodeBlock(0x11150, 0x1117F,  'Mah', "Mahajani"),
    UnicodeBlock(0x11180, 0x111DF,  'Shr', "Sharada"),
    UnicodeBlock(0x111E0, 0x111FF,  'SAN', "Sinhala Archaic Numbers"),
    UnicodeBlock(0x11200, 0x1124F,  'Kho', "Khojki"),
    UnicodeBlock(0x11280, 0x112AF,  'Mul', "Multani"),
    UnicodeBlock(0x112B0, 0x112FF,  'Khu', "Khudawadi"),
    UnicodeBlock(0x11300, 0x1137F,  'Gra', "Grantha"),
    UnicodeBlock(0x11400, 0x1147F,  'New', "Newa"),
    UnicodeBlock(0x11480, 0x114DF,  'Tir', "Tirhuta"),
    UnicodeBlock(0x11580, 0x115FF,  'Sid', "Siddham"),
    UnicodeBlock(0x11600, 0x1165F,  'Mod', "Modi"),
    UnicodeBlock(0x11660, 0x1167F, 'Monˢ', "Mongolian Supplement"),
    UnicodeBlock(0x11680, 0x116CF,  'Tak', "Takri"),
    UnicodeBlock(0x11700, 0x1174F,  'Aho', "Ahom"),
    UnicodeBlock(0x11800, 0x1184F,  'Dog', "Dogra"),
    UnicodeBlock(0x118A0, 0x118FF,  'WaC', "Warang Citi"),
    UnicodeBlock(0x11900, 0x1195F,  'DiA', "Dives Akuru"),
    UnicodeBlock(0x119A0, 0x119FF,  'Nan', "Nandinagari"),
    UnicodeBlock(0x11A00, 0x11A4F,  'ZaS', "Zanabazar Square"),
    UnicodeBlock(0x11A50, 0x11AAF,  'Soy', "Soyombo"),
    UnicodeBlock(0x11AB0, 0x11ABF, 'UCAᵃ', "Unified Canadian Aboriginal Syllabics Extended-A"),
    UnicodeBlock(0x11AC0, 0x11AFF,  'PCH', "Pau Cin Hau"),
    UnicodeBlock(0x11B00, 0x11B5F, 'Devᵃ', "Devanagari Extended-A"),
    UnicodeBlock(0x11C00, 0x11C6F,  'Bha', "Bhaiksuki"),
    UnicodeBlock(0x11C70, 0x11CBF,  'Mar', "Marchen"),
    UnicodeBlock(0x11D00, 0x11D5F,  'MaG', "Masaram Gondi"),
    UnicodeBlock(0x11D60, 0x11DAF,  'GuG', "Gunjala Gondi"),
    UnicodeBlock(0x11EE0, 0x11EFF,  'Mak', "Makasar"),
    UnicodeBlock(0x11F00, 0x11F5F,  'Kaw', "Kawi"),
    UnicodeBlock(0x11FB0, 0x11FBF, 'Lisˢ', "Lisu Supplement"),
    UnicodeBlock(0x11FC0, 0x11FFF, 'Tamˢ', "Tamil Supplement"),
    UnicodeBlock(0x12000, 0x123FF,  'Cun', "Cuneiform"),
    UnicodeBlock(0x12400, 0x1247F,  'CNP', "Cuneiform Numbers and Punctuation"),
    UnicodeBlock(0x12480, 0x1254F,  'EDC', "Early Dynastic Cuneiform"),
    UnicodeBlock(0x12F90, 0x12FFF,  'CyM', "Cypro-Minoan"),
    UnicodeBlock(0x13000, 0x1342F,  'EgH', "Egyptian Hieroglyphs"),
    UnicodeBlock(0x13430, 0x1345F,  'EHF', "Egyptian Hieroglyph Format Controls"),
    UnicodeBlock(0x14400, 0x1467F,  'AnH', "Anatolian Hieroglyphs"),
    UnicodeBlock(0x16800, 0x16A3F, 'Bamˢ', "Bamum Supplement"),
    UnicodeBlock(0x16A40, 0x16A6F,  'Mro', "Mro"),
    UnicodeBlock(0x16A70, 0x16ACF,  'Tan', "Tangsa"),
    UnicodeBlock(0x16AD0, 0x16AFF,  'BaV', "Bassa Vah"),
    UnicodeBlock(0x16B00, 0x16B8F,  'PaH', "Pahawh Hmong"),
    UnicodeBlock(0x16E40, 0x16E9F,  'Med', "Medefaidrin"),
    UnicodeBlock(0x16F00, 0x16F9F,  'Mia', "Miao"),
    UnicodeBlock(0x16FE0, 0x16FFF,  'ISP', "Ideographic Symbols and Punctuation"),
    UnicodeBlock(0x17000, 0x187FF,  'Tng', "Tangut"),
    UnicodeBlock(0x18800, 0x18AFF,  'TaC', "Tangut Components"),
    UnicodeBlock(0x18B00, 0x18CFF,  'KSS', "Khitan Small Script"),
    UnicodeBlock(0x18D00, 0x18D7F, 'Tanˢ', "Tangut Supplement"),
    UnicodeBlock(0x1AFF0, 0x1AFFF, 'Kanᵇ', "Kana Extended-B"),
    UnicodeBlock(0x1B000, 0x1B0FF, 'Kanˢ', "Kana Supplement"),
    UnicodeBlock(0x1B100, 0x1B12F, 'Kanᵃ', "Kana Extended-A"),
    UnicodeBlock(0x1B130, 0x1B16F,  'SKE', "Small Kana Extension"),
    UnicodeBlock(0x1B170, 0x1B2FF,  'Nus', "Nushu"),
    UnicodeBlock(0x1BC00, 0x1BC9F,  'Dup', "Duployan"),
    UnicodeBlock(0x1BCA0, 0x1BCAF,  'SFC', "Shorthand Format Controls"),
    UnicodeBlock(0x1CF00, 0x1CFCF,  'ZMN', "Znamenny Musical Notation"),
    UnicodeBlock(0x1D000, 0x1D0FF,  'ByM', "Byzantine Musical Symbols"),
    UnicodeBlock(0x1D100, 0x1D1FF,  'Mus', "Musical Symbols"),
    UnicodeBlock(0x1D200, 0x1D24F,  'AGM', "Ancient Greek Musical Notation"),
    UnicodeBlock(0x1D2C0, 0x1D2DF,  'KaN', "Kaktovik Numerals"),
    UnicodeBlock(0x1D2E0, 0x1D2FF,  'MaN', "Mayan Numerals"),
    UnicodeBlock(0x1D300, 0x1D35F,  'TXJ', "Tai Xuan Jing Symbols"),
    UnicodeBlock(0x1D360, 0x1D37F,  'CRN', "Counting Rod Numerals"),
    UnicodeBlock(0x1D400, 0x1D7FF,  'MaA', "Mathematical Alphanumeric Symbols"),
    UnicodeBlock(0x1D800, 0x1DAAF,  'SSW', "Sutton SignWriting"),
    UnicodeBlock(0x1DF00, 0x1DFFF, 'Latᵍ', "Latin Extended-G"),
    UnicodeBlock(0x1E000, 0x1E02F, 'Glaˢ', "Glagolitic Supplement"),
    UnicodeBlock(0x1E030, 0x1E08F, 'Cyrᵈ', "Cyrillic Extended-D"),
    UnicodeBlock(0x1E100, 0x1E14F,  'NPH', "Nyiakeng Puachue Hmong"),
    UnicodeBlock(0x1E290, 0x1E2BF,  'Tot', "Toto"),
    UnicodeBlock(0x1E2C0, 0x1E2FF,  'Wan', "Wancho"),
    UnicodeBlock(0x1E4D0, 0x1E4FF,  'NaM', "Nag Mundari"),
    UnicodeBlock(0x1E7E0, 0x1E7FF, 'Ethᵇ', "Ethiopic Extended-B"),
    UnicodeBlock(0x1E800, 0x1E8DF,  'MeK', "Mende Kikakui"),
    UnicodeBlock(0x1E900, 0x1E95F,  'Adl', "Adlam"),
    UnicodeBlock(0x1EC70, 0x1ECBF,  'ISN', "Indic Siyaq Numbers"),
    UnicodeBlock(0x1ED00, 0x1ED4F,  'OSN', "Ottoman Siyaq Numbers"),
    UnicodeBlock(0x1EE00, 0x1EEFF,  'AMA', "Arabic Mathematical Alphabetic Symbols"),
    UnicodeBlock(0x1F000, 0x1F02F,  'MaT', "Mahjong Tiles"),
    UnicodeBlock(0x1F030, 0x1F09F,  'DoT', "Domino Tiles"),
    UnicodeBlock(0x1F0A0, 0x1F0FF,  'PlC', "Playing Cards"),
    UnicodeBlock(0x1F100, 0x1F1FF, 'EnAˢ', "Enclosed Alphanumeric Supplement"),
    UnicodeBlock(0x1F200, 0x1F2FF, 'EnIˢ', "Enclosed Ideographic Supplement"),
    UnicodeBlock(0x1F300, 0x1F5FF,  'MSP', "Miscellaneous Symbols and Pictographs"),
    UnicodeBlock(0x1F600, 0x1F64F,  'Emo', "Emoticons"),
    UnicodeBlock(0x1F650, 0x1F67F,  'OrD', "Ornamental Dingbats"),
    UnicodeBlock(0x1F680, 0x1F6FF,  'TrM', "Transport and Map Symbols"),
    UnicodeBlock(0x1F700, 0x1F77F,  'Alc', "Alchemical Symbols"),
    UnicodeBlock(0x1F780, 0x1F7FF, 'GeSˣ', "Geometric Shapes Extended"),
    UnicodeBlock(0x1F800, 0x1F8FF, 'Arrᶜ', "Supplemental Arrows-C"),
    UnicodeBlock(0x1F900, 0x1F9FF, 'SyPˢ', "Supplemental Symbols and Pictographs"),
    UnicodeBlock(0x1FA00, 0x1FA6F,  'Chs', "Chess Symbols"),
    UnicodeBlock(0x1FA70, 0x1FAFF, 'SyPᵃ', "Symbols and Pictographs Extended-A"),
    UnicodeBlock(0x1FB00, 0x1FBFF,  'SLC', "Symbols for Legacy Computing"),
    UnicodeBlock(0x20000, 0x2A6DF, 'CJUᵇ', "CJK Unified Ideographs Extension B"),
    UnicodeBlock(0x2A700, 0x2B73F, 'CJUᶜ', "CJK Unified Ideographs Extension C"),
    UnicodeBlock(0x2B740, 0x2B81F, 'CJUᵈ', "CJK Unified Ideographs Extension D"),
    UnicodeBlock(0x2B820, 0x2CEAF, 'CJUᵉ', "CJK Unified Ideographs Extension E"),
    UnicodeBlock(0x2CEB0, 0x2EBEF, 'CJUᶠ', "CJK Unified Ideographs Extension F"),
    UnicodeBlock(0x2EBF0, 0x2EE5F, 'CJUⁱ', "CJK Unified Ideographs Extension I"),
    UnicodeBlock(0x2F800, 0x2FA1F, 'CJCˢ', "CJK Compatibility Ideographs Supplement"),
    UnicodeBlock(0x30000, 0x3134F, 'CJUᵍ', "CJK Unified Ideographs Extension G"),
    UnicodeBlock(0x31350, 0x323AF, 'CJUʰ', "CJK Unified Ideographs Extension H"),
    UnicodeBlock(0xE0000, 0xE007F,  'Tag', "Tags"),
    UnicodeBlock(0xE0100, 0xE01EF, 'VaSˢ', "Variation Selectors Supplement"),
    UnicodeBlock(0xF0000, 0xFFFFF, 'PUAᵃ', "Supplementary Private Use Area-A"),
    UnicodeBlock(0x100000, 0x10FFFF, 'PUAᵇ', "Supplementary Private Use Area-B"),
    # @AUTOUPDATE_END
]
# fmt: on


def get_blocks() -> list[UnicodeBlock]:
    return _BLOCKS


@lru_cache(maxsize=256)
def find_block(number: int) -> UnicodeBlock:
    idx = bisect_right(_BLOCKS, number, key=attrgetter("start"))
    if idx:
        block = _BLOCKS[idx - 1]
        return block


@cache
def get_max_block_abbr_length() -> int:
    return max(len(b.abbr) for b in _BLOCKS)


@cache
def get_max_block_name_length() -> int:
    return max(len(b.name) for b in _BLOCKS)

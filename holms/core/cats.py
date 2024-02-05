# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from collections import namedtuple

import pytermor as pt

CharOverride = namedtuple("CharOverride", ["char", "style"])


class CategoryStyles(dict[str, dict[str, pt.FrozenStyle]]):
    BASE = pt.FrozenStyle()

    C_DEFAULT = pt.FrozenStyle(BASE, fg=pt.cv.RED)
    C_CUSTOM = pt.FrozenStyle(BASE, fg=pt.cv.HI_RED)
    Z_CUSTOM = pt.FrozenStyle(BASE, fg=pt.cv.HI_CYAN)

    _CATEGORY_STYLE_MAP = [
        ("Cc", C_DEFAULT),
        ("Cf", C_DEFAULT),
        ("Cs", pt.FrozenStyle(BASE, fg=pt.cv.HI_YELLOW, bg=pt.cv.DARK_RED)),
        ("Co", pt.FrozenStyle(BASE, fg=pt.cv.BLACK, bg=pt.cv.RED)),
        ("Cn", pt.FrozenStyle(BASE, fg=pt.cv.GRAY)),
        ("Z*", pt.FrozenStyle(BASE, fg=pt.cv.CYAN)),
        ("N*", pt.FrozenStyle(BASE, fg=pt.cv.BLUE)),
        ("P*", pt.FrozenStyle(BASE, fg=pt.cv.YELLOW)),
        ("S*", pt.FrozenStyle(BASE, fg=pt.cv.GREEN)),
        ("M*", pt.FrozenStyle(BASE, fg=pt.cv.HI_YELLOW)),
        ("-*", pt.FrozenStyle(BASE, fg=pt.cv.MAGENTA)),  # non-utf8
        ("C*", C_DEFAULT),
    ]

    def __init__(self):
        super().__init__()
        for cat, st in self._CATEGORY_STYLE_MAP:
            k1, k2 = self._category_to_key(cat)
            subdict = super().get(k1, dict())
            if not subdict:
                self.update({k1: subdict})
            subdict.update({k2: st})

    def get(self, cat: str, default: pt.Style = pt.NOOP_STYLE) -> pt.Style:
        k1, k2 = self._category_to_key(cat)
        if k1 not in self.keys():
            return default
        subdict = super().get(k1)
        if k2 in subdict.keys():
            return subdict.get(k2)
        if "*" in subdict.keys():
            return subdict.get("*")
        return default

    @classmethod
    def _category_to_key(cls, cat: str) -> tuple[str, str]:
        if len(cat) == 1:
            return cat[0], " "
        if len(cat) != 2:
            raise ValueError(f"Category mapping key should be 1/2-char long: {cat!r}")
        return cat[0], cat[1]


_cc_styles = CategoryStyles()
OVERRIDE_CHARS = dict[int, CharOverride](
    {
        0x00: CharOverride("Ø", CategoryStyles.C_CUSTOM),
        0x08: CharOverride("←", CategoryStyles.C_CUSTOM),
        0x09: CharOverride("⇥", CategoryStyles.C_CUSTOM),
        0x0A: CharOverride("↵", CategoryStyles.C_CUSTOM),
        0x0B: CharOverride("⤓", CategoryStyles.C_CUSTOM),
        0x0C: CharOverride("↡", CategoryStyles.C_CUSTOM),
        0x0D: CharOverride("⇤", CategoryStyles.C_CUSTOM),
        0x1B: CharOverride("ə", CategoryStyles.C_CUSTOM),
        0x1C: CharOverride("⁜", CategoryStyles.C_CUSTOM),
        0x1D: CharOverride("⋮", CategoryStyles.C_CUSTOM),
        0x1E: CharOverride("∻", CategoryStyles.C_CUSTOM),
        0x1F: CharOverride("·", CategoryStyles.C_CUSTOM),
        0x7F: CharOverride("→", CategoryStyles.C_CUSTOM),
        0x20: CharOverride("␣", CategoryStyles.Z_CUSTOM),
        0xA0: CharOverride("⇋", CategoryStyles.Z_CUSTOM),
    }
)

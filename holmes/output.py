import math
import sys
import unicodedata
from collections.abc import Iterable

from holmes.core import Char
import pytermor as pt


class CategoryStyles(dict[str, pt.FrozenStyle]):
    _BASE = pt.FrozenStyle()
    C = pt.FrozenStyle(_BASE, fg=pt.cv.RED)
    CS = pt.FrozenStyle(_BASE, fg=pt.cv.HI_YELLOW, bg=pt.cv.DARK_RED)
    CO = pt.FrozenStyle(_BASE, fg=pt.cv.BLACK, bg=pt.cv.RED)
    CN = pt.FrozenStyle(_BASE, fg=pt.cv.GRAY)
    Z = pt.FrozenStyle(_BASE, fg=pt.cv.CYAN)
    N = pt.FrozenStyle(_BASE, fg=pt.cv.BLUE)
    P = pt.FrozenStyle(_BASE, fg=pt.cv.YELLOW)
    S = pt.FrozenStyle(_BASE, fg=pt.cv.GREEN)
    M = pt.FrozenStyle(_BASE, fg=pt.cv.HI_YELLOW)
    NOT_UTF_8 = pt.FrozenStyle(_BASE, fg=pt.cv.MAGENTA)

    def __init__(self):
        super().__init__({
            'Cc': self.C,
            'Cf': self.C,
            'Cs': self.CS,
            'Co': self.CO,
            'Cn': self.CN,
            'Zs': self.Z,
            'Zl': self.Z,
            'Zp': self.Z,
            'Nd': self.N,
            'Nl': self.N,
            'No': self.N,
            'Pc': self.P,
            'Pd': self.P,
            'Ps': self.P,
            'Pe': self.P,
            'Pi': self.P,
            'Pf': self.P,
            'Po': self.P,
            'Sm': self.S,
            'Sc': self.S,
            'Sk': self.S,
            'So': self.S,
            'Mn': self.M,
            'Mc': self.M,
            'Me': self.M,
            ' ?': self.NOT_UTF_8,
        })


class CliWriter:
    IDX_SEP_STYLE = pt.FrozenStyle(fg=pt.cv.WHITE, bg=pt.cv.BLACK, overlined=True)
    IDX_STYLE = pt.FrozenStyle(fg=pt.cv.GRAY, bg=pt.cv.BLACK)
    CHAR_STYLE = pt.FrozenStyle(fg=0xFFFFFF, bg=0, bold=True)

    def __init__(self, io=sys.stdout, decimal_idx: bool = False):
        self._io = io
        pt.RendererManager.set_default(pt.SgrRenderer(pt.OutputMode.XTERM_256))
        self._decimal_idx = decimal_idx
        self._max_idx_len = 4
        self._styles = CategoryStyles()

    def print_string(self, cc: Iterable[Char]):
        for idx, c in enumerate(cc):
            self._max_idx_len = max(self._max_idx_len, len(self._format_idx(idx)))
            self.print_char(c, idx)

    def print_char(self, c: Char, idx: int):
        idx_str, idx_st = self._format_idx(idx, self._max_idx_len)
        if idx % self._base > 0:
            idx_str = ' '*(len(idx_str)-1) + idx_str[-1]
            idx_st = self.IDX_STYLE

        text = pt.Text(
            idx_str, idx_st,  "│",
            self._format_cpnum(c), "▕",
            self._format_char(c), "▏",
            self._format_category(c), " ",
            self._format_name(c),
        )
        pt.echo(text, file=self._io)

    @property
    def _base(self) -> int:
        return [0x10, 10][self._decimal_idx]

    def _format_idx(self, idx: int, max_len: int = None) -> tuple[str, pt.Style]:
        fmt = 'xd'[self._decimal_idx]
        if max_len is not None:
            fill = '0-'[self._decimal_idx]
            return f'{idx:{fill}{max_len}{fmt}}', self.IDX_SEP_STYLE
        result = f'{idx:{fmt}}'
        if self._decimal_idx:
            return result, self.IDX_STYLE
        return pt.fit(result, 2 * math.ceil(len(result) / 2), fill='0'), self.IDX_STYLE

    def _format_cpnum(self, c: Char) -> str:
        if c.is_invalid:
            return f'0x{c.cpnum:<6X}'
        result = f'{c.cpnum:02X}'
        return f'U+{result:>6s}'

    def _format_char(self, c: Char) -> str:
        char = c.char
        st = pt.merge_styles(self.CHAR_STYLE, overwrites=[self._styles._BASE, self._styles.get(c.category, pt.NOOP_STYLE)])
        aux = ''

        if c.is_control or c.is_invalid or c.is_surrogate or c.is_unassigned:
            char = '▯'
            charlen = 1
        else:
            charlen = pt.get_char_width(c.char, block=False)
            if unicodedata.combining(c.char):
                aux = ' '
                charlen += 1
        return ' '*(2-max(-1, charlen))+pt.render(aux+char, st)+' '

    def _format_category(self, c: Char) -> str:
        if not c.category:
            return ""
        return pt.render(c.category, self._styles.get(c.category, self._styles._BASE))

    def _format_name(self, c: Char) -> str:
        return c.name or ''

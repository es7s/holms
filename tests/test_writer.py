# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import re

import pytermor as pt
import pytest
from es7s_commons import Regex
from pytermor import OutputMode as OM

from holms.core import Char, Attribute, Options
from holms.core.writer import CliWriter
from test_cli import assert_streq


@pytest.fixture(scope="function")
def opt(request):
    mark = request.node.get_closest_marker("opt")
    if not mark:
        opt = Options()
    else:
        opt = Options(**(mark.kwargs or {}))
    yield opt


@pytest.fixture(scope="function", autouse=True, params=[OM.NO_ANSI, OM.XTERM_256])
def renderer(request):
    pt.RendererManager.override(pt.SgrRenderer(request.param))


@pytest.fixture(scope="function", params=[True, False])
def buffered(request):
    yield request.param


def getout(cap) -> str:
    return pt.apply_filters(cap.readouterr().out, pt.SgrStringReplacer)


class TestFormat:
    # fmt: off
    @pytest.mark.parametrize("opt, expected", [
        (Options(_columns=[Attribute.OFFSET]), Regex(R'([0246]\s*){4}')),
        (Options(_columns=[Attribute.INDEX]), Regex(R'(#\s*[0-3]\s*){4}')),
        (Options(_columns=[Attribute.RAW]), Regex(R'(0x\s*(d1\s*8f|d0\s*af)\s*){4}')),
        (Options(_columns=[Attribute.NUMBER]), Regex(R'(U\+\s*(44F|42F)\s*){4}')),
        (Options(_columns=[Attribute.CHAR]), Regex(R'([яЯ]){4}')),
        (Options(_columns=[Attribute.COUNT]), Regex(R'^(\n){3}')),
        (Options(_columns=[Attribute.CAT]), Regex(R'((L[lu])\s*){4}')),
        (Options(_columns=[Attribute.CAT], _names=True), ["Lowercase_Letter"]*2+["Uppercase_Letter"]*2),
        (Options(_columns=[Attribute.NAME]), Regex(R'(CYRILLIC (SMALL|CAPITAL) LETTER YA\s*){4}')),
        (Options(_columns=[Attribute.BLOCK]), Regex(R'(Cyr\s*){4}')),
        (Options(_columns=[Attribute.BLOCK], _names=True), ["Cyrillic"]*4),
        (Options(_columns=[]), Regex(R'^\s*0+\s+U\+\s*44F\s+▕ я ▏.+Ll\s+CYRILLIC SMALL LETTER YA')),
    ])
    # fmt: on
    def test_columns(self, opt, buffered, capsys, expected):
        CliWriter(opt, buffered).write(Char.parse("яяЯЯ"))
        stdout = getout(capsys)
        assert_streq(stdout, expected)

    def test_all_columns(self, capsys):
        CliWriter(Options(all_columns=True), buffered=True).write(Char.parse("яяЯЯ"))
        stdout = getout(capsys)
        assert_streq(stdout, ["0  #0   0x d1 8f U+44F ▕ я ▏‎ Cyr Ll CYRILLIC SMALL LETTER YA",
                              "2  #1   0x d1 8f U+44F ▕ я ▏‎ Cyr Ll CYRILLIC SMALL LETTER YA",
                              "4  #2   0x d0 af U+42F ▕ Я ▏‎ Cyr Lu CYRILLIC CAPITAL LETTER YA",
                              "6  #3   0x d0 af U+42F ▕ Я ▏‎ Cyr Lu CYRILLIC CAPITAL LETTER YA"], ignore_ws=True)

    @pytest.mark.opt(_merge=True, _columns=[Attribute.COUNT, Attribute.CHAR])
    def test_merge(self, opt, buffered, capsys):
        CliWriter(opt, buffered).write(Char.parse("aaabaabbbc123333a"))
        expected_regex = Regex(R"^3a b 2a 3b c 1 2 43 a\s*$")
        out = re.sub(R"([× ▏▕\u200e]+)|(\n)", lambda m: ["", " "][bool(m.group(2))], getout(capsys))
        assert expected_regex.match(out)

    @pytest.mark.opt(group_level=1, _columns=[Attribute.COUNT, Attribute.CHAR])
    def test_group(self, opt, capsys):
        CliWriter(opt, buffered=True).write(Char.parse("aaabaabbbc123333a"))
        expected_regex = Regex(R"^ 35% 6× a 24% 4× b 24% 4× 3 59% 1× c 59% 1× 1 59% 1× 2\s*$")
        sub_regex = Regex(R"([ \n]+)|([^\d%abc×]+)", dotall=True)
        outraw = getout(capsys)
        out = sub_regex.sub(lambda m: ["", " "][bool(m.group(1))], outraw)
        assert expected_regex.match(out)

    @pytest.mark.opt(decimal_offset=True)
    def test_decimal_offset(self, opt, buffered, capsys):
        CliWriter(opt, buffered).write(Char.parse("a"))
        assert getout(capsys).startswith("⏨")

    # fmt: off
    @pytest.mark.parametrize("rigid, buffered, expected_str", [
        # dynamic, unbuffered:
        (False, False, '0000  U+   1  0x    01|'
                       '0001  U+  81  0x c2 81|'
                       '0003  U+  AB  0x c2 ab|'
                       '0005  U+ 112  0x c4 92|'
                       '0007  U+ F22  e0 bc a2|'
                       '000a  U+1E22  e1 b8 a2|'
                       '000d  U1F333  f09f8cb3|'
                       '0011  10FFFF  f48fbfbf|'),
        # rigid, unbuffered:
        (True,  False, '0000  U+     1  0x       01|'
                       '0001  U+    81  0x    c2 81|'
                       '0003  U+    AB  0x    c2 ab|'
                       '0005  U+   112  0x    c4 92|'
                       '0007  U+   F22  0x e0 bc a2|'
                       '000a  U+  1E22  0x e1 b8 a2|'
                       '000d  U+ 1F333  0xf0 9f 8c b3|'
                       '0011  U+10FFFF  0xf4 8f bf bf|'),
        # rigid, buffered
        (True,  True,  '00  U+     1  0x         01|'
                       '01  U+    81  0x      c2 81|'
                       '03  U+    AB  0x      c2 ab|'
                       '05  U+   112  0x      c4 92|'
                       '07  U+   F22  0x   e0 bc a2|'
                       '0a  U+  1E22  0x   e1 b8 a2|'
                       '0d  U+ 1F333  0xf0 9f 8c b3|'
                       '11  U+10FFFF  0xf4 8f bf bf|'),
        # dynamic, buffered
        (False,  True, '00  U+   1  0x    01|'
                       '01  U+  81  0x c2 81|'
                       '03  U+  AB  0x c2 ab|'
                       '05  U+ 112  0x c4 92|'
                       '07  U+ F22  e0 bc a2|'
                       '0a  U+1E22  e1 b8 a2|'
                       '0d  U1F333  f09f8cb3|'
                       '11  10FFFF  f48fbfbf|'),
    ])
    # fmt: on
    def test_rigid(self, rigid, buffered, expected_str, capsys):
        columns = [Attribute.OFFSET, Attribute.NUMBER, Attribute.RAW]
        inp_ints = [0x1, 0x81, 0xAB, 0x112, 0xF22, 0x1E22, 0x1F333, 0x10FFFF]
        opt = Options(_columns=columns, _rigid=rigid)
        CliWriter(opt, buffered).write(Char.parse(map(chr, inp_ints)))
        assert "|".join(map(str.strip, getout(capsys).splitlines() + [""])) == expected_str

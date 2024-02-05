# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import re
from collections.abc import Iterable
from pathlib import Path

import pytermor as pt
import pytest
from click.testing import CliRunner as BaseCliRunner, Result
from es7s_commons import Regex

from holms import APP_NAME
from holms.cli.entrypoint import entrypoint__, CliCommand
from holms.db.uccat import get_categories


def assert_streq(str1: str | Iterable[str] | re.Pattern, str2: str | Iterable[str] | re.Pattern, sort=False, ignore_ws=False):
    def __norm(ss: str | Iterable[str]) -> Iterable[str]:
        if not pt.isiterable(ss):
            ss = ss.splitlines()
        if sort:
            ss = sorted(ss)
        for line in ss:
            if ignore_ws:
                yield re.sub(r"\s+", "", line)
            else:
                yield line.strip()

    def __search(ss: str | Iterable[str], pat: re.Pattern):
        ss = '\n'.join(__norm(ss))
        if pat.search(ss):
            return
        raise AssertionError(f"{pat.pattern} doesnt match {ss!r}")

    if isinstance(str1, re.Pattern):
        __search(str2, str1)
        return
    elif isinstance(str2, re.Pattern):
        __search(str1, str2)
        return

    norm1 = [*__norm(str1)]
    norm2 = [*__norm(str2)]
    for n1, n2 in zip(norm1 , norm2):
        assert n1 == n2
    if len(norm1) != len(norm2):
        raise AssertionError(f"Actual/expected lines count mismatch: {len(norm1)} != {len(norm2)}")


class CliRunner(BaseCliRunner):
    def __init__(self) -> None:
        super().__init__(mix_stderr=False)

    def invoke(
        self,
        cli,
        args=None,
        input=None,
        env=None,
        catch_exceptions=False,
        color=False,
        **extra,
    ) -> Result:
        return super().invoke(cli, args, input, env, catch_exceptions, color, **extra)

    def get_default_prog_name(self, cli: "BaseCommand") -> str:
        return APP_NAME


@pytest.fixture(scope="function")
def crun() -> CliRunner:
    yield CliRunner()


@pytest.fixture(scope="function")
def ep() -> CliCommand:
    yield entrypoint__
    pt.ConfigManager.set(pt.Config())


@pytest.fixture(scope="function")
def filepath_ascii() -> str:
    return str(Path(__file__).parent / "data" / "ascii.txt")


class TestCommands:
    def test_entrypoint(self, crun: CliRunner, ep: CliCommand):
        rs = crun.invoke(ep, "-?")
        assert rs.exit_code == 0
        assert not rs.stderr

        assert "Options" in rs.stdout
        assert "Commands" in rs.stdout

    def test_version(self, crun: CliRunner, ep: CliCommand):
        rs = crun.invoke(ep, ["-c", "version"])
        assert rs.exit_code == 0
        assert not rs.stderr

        assert "holms" in rs.stdout
        assert Regex(R"ₑ.*ₛ.*₇.*ₛ").search(rs.stdout)

    def test_legend(self, crun: CliRunner, ep: CliCommand):
        rs = crun.invoke(ep, ["-c", "legend"])
        assert rs.exit_code == 0
        assert not rs.stderr

        assert Regex(R"CODE.POINT.CATEGORY.EXAMPLES").search(rs.stdout)
        for cat in get_categories():
            if len(cat.abbr) < 2:
                continue
            assert Regex(cat.name).search(rs.stdout)

    def test_format(self, crun: CliRunner, ep: CliCommand):
        rs = crun.invoke(ep, ["-c", "format"])
        assert rs.exit_code == 0
        assert not rs.stderr

        assert Regex(R"OUTPUT.+FORMAT").search(rs.stdout)
        assert Regex(R"COLUMN.+VISIBILITY").search(rs.stdout)

    def test_path(self, crun: CliRunner, ep: CliCommand):
        rs = crun.invoke(ep, ["-c", "path"])
        assert rs.exit_code == 0
        assert not rs.stderr

        assert Regex(R"Executable:\s*").search(rs.stdout)
        assert Regex(R"Entrypoint:\s*").search(rs.stdout)


class TestRunCommand:
    def test_file_input(self, crun: CliRunner, ep: CliCommand, filepath_ascii: str):
        rs = crun.invoke(ep, ["-c", "run", filepath_ascii])
        assert rs.exit_code == 0
        assert not rs.stderr
        assert len(rs.stdout.splitlines()) == 0x80

    def test_stdin_input(self, crun: CliRunner, ep: CliCommand):
        s = "\n".join(map(str, range(10))) + "\n"
        rs = crun.invoke(ep, ["-c", "run", "-"], input=s)
        assert rs.exit_code == 0
        assert not rs.stderr
        assert len(rs.stdout.splitlines()) == 20

    @pytest.mark.parametrize(
        "opt, exp_out, should_be_same_width",
        [
            [
                "-ur",
                (
                    " 0000  #   0   0x       00 U+     0 ▕ Ø ▏\u200e BaL Cc ASCII C0 [NUL] NULL \n"
                    " 0001  #   1   0x    c2 a1 U+    A1 ▕ ¡ ▏\u200e La1ˢPo INVERTED EXCLAMATION MARK \n"
                    " 0003  #   2   0x e2 80 9d U+  201D ▕ ” ▏\u200e GeP Pf RIGHT DOUBLE QUOTATION MARK \n"
                ),
                False,
            ],
            [
                "-u",
                (
                    " 0000  #   0   0x    00 U+   0 ▕ Ø ▏\u200e BaL Cc ASCII C0 [NUL] NULL \n"
                    " 0001  #   1   0x c2 a1 U+  A1 ▕ ¡ ▏\u200e La1ˢPo INVERTED EXCLAMATION MARK \n"
                    " 0003  #   2   e2 80 9d U+201D ▕ ” ▏\u200e GeP Pf RIGHT DOUBLE QUOTATION MARK \n"
                ),
                False,
            ],
            [
                "-br",
                (
                    " 0  #0   0x       00 U+   0 ▕ Ø ▏\u200e BaL Cc ASCII C0 [NUL] NULL         \n"
                    " 1  #1   0x    c2 a1 U+  A1 ▕ ¡ ▏\u200e La1ˢPo INVERTED EXCLAMATION MARK   \n"
                    " 3  #2   0x e2 80 9d U+201D ▕ ” ▏\u200e GeP Pf RIGHT DOUBLE QUOTATION MARK \n"
                ),
                True,
            ],
            [
                "-b",
                (
                    " 0  #0   0x    00 U+   0 ▕ Ø ▏\u200e BaL Cc ASCII C0 [NUL] NULL         \n"
                    " 1  #1   0x c2 a1 U+  A1 ▕ ¡ ▏\u200e La1ˢPo INVERTED EXCLAMATION MARK   \n"
                    " 3  #2   e2 80 9d U+201D ▕ ” ▏\u200e GeP Pf RIGHT DOUBLE QUOTATION MARK \n"
                ),
                True,
            ],
        ],
    )
    def test_buffering_and_rigid_output(
        self,
        crun: CliRunner,
        ep: CliCommand,
        opt: str,
        exp_out: str,
        should_be_same_width: bool,
    ):
        rs = crun.invoke(ep, ["run", "-a", opt], input="\0¡”")
        assert rs.exit_code == 0
        assert not rs.stderr
        assert_streq(rs.stdout, exp_out)
        widths = {len(line) for line in rs.stdout.splitlines()}
        assert len(widths) == (3, 1)[should_be_same_width]

    def test_merge(self, crun: CliRunner, ep: CliCommand):
        s = "a" * 9 + "Щ" + "a" * 7 + "!" * 6
        rs = crun.invoke(ep, ["run", "-m", "-f", "count,number"], input=s)

        assert rs.exit_code == 0
        assert not rs.stderr
        assert_streq(rs.stdout, ["9×U+61", "U+429", "7×U+61", "6×U+21"], ignore_ws=True)

    def test_group(self, crun: CliRunner, ep: CliCommand):
        s = "a" * 9 + "Щ" + "a" * 7 + "!" * 6
        rs = crun.invoke(ep, ["run", "-g", "-f", "block,count,number"], input=s)

        assert rs.exit_code == 0
        assert not rs.stderr
        assert_streq(
            rs.stdout, ["BaL70%███16×U+61", "BaL26%█▏6×U+21", "Cyr4.3%▏1×U+429"], ignore_ws=True
        )

    def test_group_cat(self, crun: CliRunner, ep: CliCommand):
        s = "a" * 9 + "Щ" + "a" * 7 + "!" * 6
        rs = crun.invoke(ep, ["run", "-gg", "-f", "count,cat"], input=s)

        assert rs.exit_code == 0
        assert not rs.stderr

        assert_streq(
            rs.stdout,
            [
                "70%██████████16×Lowercase_Letter",
                "26%███▊6×Other_Punctuation",
                "4.3%▋1×Uppercase_Letter",
            ],
            ignore_ws=True,
        )

    def test_group_super_cat(self, crun: CliRunner, ep: CliCommand):
        s = "a" * 9 + "Щ" + "a" * 7 + "!" * 6
        rs = crun.invoke(ep, ["run", "-ggg", "-f", "count,cat"], input=s)

        assert rs.exit_code == 0
        assert not rs.stderr

        assert_streq(rs.stdout, ["74%██████████17×Letter", "26%███▌6×Punctuation"], ignore_ws=True)

    @pytest.mark.parametrize(
        "opts, exp_out",
        [
            [["-f", "offset"], [" 0000", "0004", "0008", "000c"]],
            [["-f", "offset", "--decimal"], ["⏨   0", "⏨   4", "⏨   8", "⏨  12"]],
            [["-f", "index"], ["#   0", "#   1", "#   2", "#   3"]],
            [["-f", "raw"], [" f09f9191", "f09f9191", "f09f9191", "f09f8d83"]],
            [["-f", "number"], ["U1F451", "U1F451", "U1F451", "U1F343"]],
            [["-f", "char"], "👑👑👑🍃"],
            [["-f", "cat"], ["So", "So", "So", "So"]],
            [["-f", "name"], ["CROWN", "CROWN", "CROWN", "LEAF FLUTTERING IN WIND"]],
            [["-f", "cat", "-n"], ["Other_Symbol"] * 4],
            [["-f", "block"], ["MSP"] * 4],
            [["-f", "block", "-n"], ["Miscellaneous S‥"] * 4],
        ],
    )
    def test_format_custom(self, crun: CliRunner, ep: CliCommand, opts: list[str], exp_out: str):
        rs = crun.invoke(ep, ["run", *opts], input="👑" * 3 + "🍃")
        assert rs.exit_code == 0
        assert not rs.stderr
        assert_streq(rs.stdout, exp_out)

    @pytest.mark.parametrize(
        "opts, exp_out",
        [
            [["-c"], "\x1b[33mPo\x1b[39m MIDDLE DOT"],
            [["-C"], "Po MIDDLE DOT"],
            [["-c"], "\x1b[33mPo\x1b[39m MIDDLE DOT"],
        ],
    )
    def test_color(self, crun: CliRunner, ep: CliCommand, opts: list[str], exp_out: str):
        rs = crun.invoke(ep, [*opts, "run", "-f", "cat,name"], input="·")
        assert rs.exit_code == 0
        assert not rs.stderr
        assert_streq(rs.stdout, exp_out)

    @pytest.mark.parametrize(
        "opts, exp_out",
        [
            [
                [],
                [
                    "LATIN CAPITAL LETTER A",
                    "ASCII C0 [LF] LINE FEED",
                    "LATIN CAPITAL LETTER B",
                    "LATIN CAPITAL LETTER C",
                    "ASCII C0 [LF] LINE FEED",
                    "ASCII C0 [LF] LINE FEED",
                    "LATIN CAPITAL LETTER D",
                ],
            ],
            [
                ["--oneline"],
                [
                    "LATIN CAPITAL LETTER A",
                    "LATIN CAPITAL LETTER B",
                    "LATIN CAPITAL LETTER C",
                    "LATIN CAPITAL LETTER D",
                ],
            ],
        ],
    )
    def test_oneline(self, crun: CliRunner, ep: CliCommand, opts: list[str], exp_out: str):
        rs = crun.invoke(ep, ["run", "-f", "name", *opts], input="A\nBC\n\nD")
        assert rs.exit_code == 0
        assert not rs.stderr
        assert_streq(rs.stdout, exp_out)

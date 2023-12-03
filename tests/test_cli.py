# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from collections.abc import Iterator
from pathlib import Path

import pytest
from click.testing import CliRunner
from es7s_commons import Regex

import holms.cli
from holms.cli import Command
from holms.common import Char
from holms.uccat import get_categories


def getin() -> Iterator[Char]:
    yield from Char.parse("\x01\x02\t !#123@ABC\x7f\u0080\u0081\u00ff")
    yield from Char.parse("\u0100АБВ\u0800\u2000\u8000\U00020000\U0001FFFF")
    yield from Char.parse([0x00, 0x7F, 0x80])


@pytest.fixture(scope="function")
def cli_runner() -> CliRunner:
    yield CliRunner(mix_stderr=False)


@pytest.fixture(scope="function")
def entrypoint() -> Command:
    yield holms.cli.entrypoint


@pytest.fixture(scope="function")
def filepath_ascii() -> str:
    return str(Path(__file__).parent / "data" / "ascii.txt")


class TestCliModes:
    def test_help(self, cli_runner: CliRunner, entrypoint: Command):
        rs = cli_runner.invoke(entrypoint, "-?")
        assert rs.exit_code == 0
        assert not rs.stderr

        assert "Buffering" in rs.stdout
        assert "Options" in rs.stdout

    def test_version(self, cli_runner: CliRunner, entrypoint: Command):
        rs = cli_runner.invoke(entrypoint, ["--version", "-c"])
        assert rs.exit_code == 0
        assert not rs.stderr

        assert "holms" in rs.stdout
        assert Regex(R"ₑ.+ₛ.+₇.+ₛ").search(rs.stdout)

    def test_legend(self, cli_runner: CliRunner, entrypoint: Command):
        rs = cli_runner.invoke(entrypoint, ["--legend", "-c"])
        assert rs.exit_code == 0
        assert not rs.stderr

        assert Regex(R"OUTPUT.+FORMAT").search(rs.stdout)
        assert Regex(R"COLUMN.+VISIBILITY").search(rs.stdout)
        assert Regex(R"CODE.+POINT.+CATEGORY.+EXAMPLES").search(rs.stdout)

        for cat in get_categories():
            if len(cat.abbr) < 2:
                continue
            assert Regex(Rf"{cat.abbr}(?:\x1b\[[0-9:;]*m|\s+)*{cat.name}").search(rs.stdout)


class TestCliMainMode:
    def test_file_input(self, cli_runner: CliRunner, entrypoint: Command, filepath_ascii: str):
        rs = cli_runner.invoke(entrypoint, [filepath_ascii, "-c"])
        assert rs.exit_code == 0
        assert not rs.stderr
        assert len(rs.stdout.splitlines()) == 0x80

    def test_stdin_input(self, cli_runner: CliRunner, entrypoint: Command):
        s = "\n".join(map(str, range(10))) + "\n"
        rs = cli_runner.invoke(entrypoint, ["-", "-c"], input=s)
        assert rs.exit_code == 0
        assert not rs.stderr
        assert len(rs.stdout.splitlines()) == 20

    def test_buffered(self):
        ...

    def test_unbuffered(self):
        ...

    def test_merge(self):
        ...

    def test_group(self):
        ...

    def test_group_cat(self):
        ...

    def test_group_super_cat(self):
        ...

    def test_format_default(self):
        ...

    def test_format_custom(self):
        ...

    def test_format_single_char(self):
        ...

    def test_format_all(self):
        ...

    def test_static(self):
        ...

    def test_color(self):
        ...

    def test_no_color(self):
        ...

    def test_decimal(self):
        ...

# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import io
import sys
import unicodedata
from collections.abc import Iterable
from dataclasses import asdict
from functools import partial
from importlib.resources import open_binary

import click
import pytermor as pt
from click import pass_context
from es7s_commons import GROUP_SEPARATOR as SECTION_SEP

from holms import APP_NAME
from holms.core import Attribute, OVERRIDE_CHARS, Options, resolve_cat_style
from holms.core.writer import Styles
from holms.db import get_max_block_abbr_length, get_max_block_name_length, UnicodeBlock


@pass_context
class LegendCommand:
    def __init__(self, ctx: click.Context, **kwargs):
        self._buffer = io.StringIO()
        self._echo = partial(pt.echo, file=self._buffer)
        self._ctx = ctx
        self._opts = Options(
            _columns=[
                Attribute.CAT,
                Attribute.CAT,
                Attribute.CHAR,
                Attribute.NUMBER,
                Attribute.NAME,
            ],
            _rigid=True,
            _names=True,
        )
        kwargs.update({**asdict(self._opts), "buffered": True, "output": self._buffer})

        self._run(**kwargs)

    def _run(self, **kwargs):
        self._print_blocks(**kwargs.copy())
        self._print_cats(**kwargs.copy())
        self._print_overrides(**kwargs.copy())

        self._buffer.seek(0)
        for line in self._buffer.readlines():
            if SECTION_SEP not in line:
                line = 2 * " " + line
            line = line.replace(SECTION_SEP, "").rstrip() + " "  # padding
            pt.echo(line, file=sys.stdout)
        pt.echo(file=sys.stdout)

    def _print_blocks(self, **kwargs):
        from holms.db import get_blocks

        letter_cats = {"Lu", "Ll"}

        self._echo_header("UNICODE BLOCKS")
        for b in get_blocks():
            cats = set()
            cats_full = dict()
            assigned = 0
            total = b.end + 1 - b.start

            for i in range(b.start, b.end + 1):
                cat = unicodedata.category(chr(i))
                if cat != "Cn":
                    assigned += 1
                    cats.add(cat[0])
                    cats_full[cat[0]] = cat
            if all(lc in cats for lc in letter_cats):
                cats -= {*letter_cats, "Lo"}
                cats.add("LC")

            unassigned = total - assigned
            has_assigned = assigned > 0

            gap = pt.pad(2)
            row = [
                *self._format_number(b, has_assigned),
                gap,
                pt.Fragment(
                    f"{assigned:>5d}",
                    [pt.Styles.WARNING, Styles.ASSIGNED_COUNT][has_assigned],
                ),
                pt.Fragment(f"+{unassigned:<4d}" if unassigned else pt.pad(5), Styles.INVALID),
                gap,
                *self._render_block(b, has_assigned),
                gap,
                *self._format_supercats(cats, cats_full),
            ]
            self._echo(pt.Text(*row))

    @classmethod
    def _render_block(cls, block: UnicodeBlock, has_assigned: bool):
        st = [Styles.INVALID, Styles.PLAIN][has_assigned]

        yield pt.Fragment(pt.fit(block.abbr, get_max_block_abbr_length()), st)
        yield " "
        yield pt.Fragment(pt.fit(block.name, get_max_block_name_length()), st)

    @classmethod
    def _format_number(cls, block: UnicodeBlock, has_assigned: bool) -> Iterable[pt.RT]:
        st = [Styles.INVALID, pt.NOOP_STYLE][has_assigned]
        yield pt.Fragment(f"{block.start:>6X}", st)
        yield pt.Fragment("-", Styles.CPNUM_PREFIX)
        yield pt.Fragment(f"{block.end:<6X}", st)

    @classmethod
    def _format_supercats(cls, cats: set, cats_full: dict) -> Iterable[pt.RT]:
        from holms.db import get_super_categories

        for supercat in get_super_categories():
            if supercat in cats:
                yield pt.Fragment(supercat, resolve_cat_style(cats_full[supercat]))
            else:
                yield pt.Fragment("-", Styles.INVALID)

    def _print_cats(self, **kwargs):
        from holms.cmd import invoke_run

        cats_input = open_binary(f"{APP_NAME}.data", "all-cats.bin")
        kwargs.update({"input": cats_input, "_names": True})
        self._echo_header("CODE POINT CATEGORY EXAMPLES")
        self._ctx.invoke(invoke_run, **kwargs)
        cats_input.close()

    def _print_overrides(self, **kwargs):
        from holms.cmd import invoke_run

        over_input = io.BytesIO()
        for ov in OVERRIDE_CHARS.keys():
            over_input.write(chr(ov).encode())
        over_input.seek(0)
        kwargs.update({"input": over_input})
        self._echo_header("SPECIAL OVERRIDES")
        self._ctx.invoke(invoke_run, **kwargs)
        over_input.close()

    def _echo_header(self, title: str):
        self._echo(f"\n{SECTION_SEP}{title}\n", pt.Styles.BOLD)

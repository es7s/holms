# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import io
import sys
import unicodedata
from dataclasses import asdict
from functools import partial
from importlib.resources import open_binary

import click
import pytermor as pt
from click import pass_context

from holms import APP_NAME
from holms.core import Attribute, OVERRIDE_CHARS, Options, Char, CategoryStyles
from holms.core.writer import BlockView, Row, Column, Styles
from holms.db import get_categories

_SECTION_SEP = "\u001d"


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
            all_columns=False,
            _merge=False,
            group_level=0,
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
            if _SECTION_SEP not in line:
                line = pt.pad(2) + line
            line = line.replace(_SECTION_SEP, "").rstrip() + " "  # padding
            pt.echo(line, file=sys.stdout)
        pt.echo(file=sys.stdout)

    def _print_blocks(self, **kwargs):
        from holms.db import get_blocks, get_max_block_name_length
        from holms.core.view import get_view

        letter_cats = {"Lu", "Ll"}
        _cc_styles = CategoryStyles()

        render_block = lambda c, names: get_view(Attribute.BLOCK).render(
            Options(_names=names, _rigid=True),
            Row(c, 0, 0),
            Column(Attribute.BLOCK, 0, get_max_block_name_length(), align_override=pt.Align.LEFT),
        )
        render_number = lambda c, first: get_view(Attribute.NUMBER).render(
            Options(),
            Row(c, 0, 0),
            Column(Attribute.NUMBER, 0, 5),
        )

        supercats = []
        for cat in get_categories():
            if len(cat.abbr) == 1:
                supercats.append(cat.abbr)
        supercats = sorted(supercats)

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
            c1, cn = Char(chr(b.start)), Char(chr(b.end))
            unassigned = total - assigned
            row = [
                render_number(c1, True).rstrip(),
                pt.Text("-", Styles.CPNUM_PREFIX, f"{b.end:<6X} "),
                pt.Fragment(f"{assigned:>5d}", Styles.ASSIGNED_COUNT if assigned else pt.Styles.WARNING),
                pt.Fragment(f"+{unassigned:<4d}" if unassigned else pt.pad(5), Styles.INVALID),
                " " + render_block(c1, False),
                " " + render_block(c1, True),
                " ",
            ]
            for supercat in supercats:
                if supercat in cats:
                    row.append(pt.Fragment(supercat, _cc_styles.get(cats_full[supercat])))
                else:
                    row.append(pt.Fragment('-', Styles.INVALID))
            self._echo(pt.Text(*row))

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
        self._echo(f"\n{_SECTION_SEP}{title}\n", pt.Styles.BOLD)

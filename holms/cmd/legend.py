# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import io
import sys
from dataclasses import asdict
from functools import partial
from importlib.resources import open_binary

import click
import pytermor as pt
from click import pass_context

from holms import APP_NAME
from holms.core import Attribute, OVERRIDE_CHARS, Options


@pass_context
def invoke_legend(ctx: click.Context, **kwargs):
    from holms.cmd import invoke_run

    buffer = io.StringIO()
    opts = Options(
        _columns=[
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
    kwargs.update({**asdict(opts), 'buffered': True, 'output': buffer})

    echo = partial(pt.echo, file=buffer)

    over_input = io.BytesIO()
    for ov in OVERRIDE_CHARS.keys():
        over_input.write(chr(ov).encode())
    echo("SPECIAL OVERRIDES", pt.Styles.WARNING_LABEL)
    echo()
    over_input.seek(0)
    kwargs.update({"input": over_input})
    ctx.invoke(invoke_run, **kwargs)

    cats_input = open_binary(f"{APP_NAME}.data", "all-cats.bin")
    echo()
    echo("CODE POINT CATEGORY EXAMPLES", pt.Styles.WARNING_LABEL)
    echo()
    kwargs.update({"input": cats_input, '_names': True})
    ctx.invoke(invoke_run, **kwargs)

    buffer.seek(0)
    for line in buffer.readlines():
        pt.echo("  " + line.rstrip() + " ", file=sys.stdout)  # padding
    pt.echo(file=sys.stdout)

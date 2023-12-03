# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import io
import re
import sys
from functools import partial
from importlib.resources import read_text, open_binary
from io import UnsupportedOperation
from pty import STDIN_FILENO

import click
import es7s_commons
import pytermor as pt
from click import pass_context
from es7s_commons import format_path

from holms import APP_NAME, APP_VERSION, APP_UPDATED
from holms.common import Char, Attribute
from holms.reader import CliReader
from holms.writer import CliWriter, Setup


@pass_context
def invoke_legend(ctx: click.Context, **kwargs):
    echo = partial(pt.echo, file=sys.stdout)

    raw = read_text(f"{__package__}.data", "legend.ptpl")
    rendered = pt.template.render(raw, pt.RendererManager.get_default())
    echo(rendered)

    cats_input = open_binary(f"{__package__}.data", "all-cats.bin")
    cats_output = io.StringIO()

    override = {  # @REFACTORME would be better to make Setup() here, not a dict
        "buffered": True,
        "input": cats_input,
        "output": cats_output,
        "columns": [Attribute.TYPE, Attribute.TYPE_NAME, Attribute.CHAR, Attribute.NUMBER, Attribute.NAME],
        "all_columns": False,
        "merge": False,
        "group": 0,
        "static": True,
    }
    kwargs.update(override)
    ctx.invoke(invoke_defualt, **kwargs)

    cats_output.seek(0)
    for line in cats_output.read().split("\n"):
        echo("  " + line + " ")  # padding

    # @TODO add special cps overrides


@pass_context
def invoke_version(ctx: click.Context, value: int, **kwargs):
    # fmt: off
    """
             ███████
    ₑₛ₇ₛ  ║███╔═══╗███║
   ┏━┓┏━┓═╣███║ ║█████╠═┏━┓════┏━┓═┏━┓════════┏━━━━┓
   ┃ ┗┛ ┃ ║███║▐█▌╗███║ ┃ ┃    ┃ ┗┳┛ ┃ ╎ -┬-╵ ┃ ━━━┫
   ┃ ┏┓ ┃ ║█████╔╝║███║ ┃ ┗━━┓ ┃ ┣━┫ ┃ ╎ -┴-┐ ┣━━━ ┃
   ┗━┛┗━┛ ║███╔═╝ ║███║ ┗━━━━┛ ┗━┛ ┗━┛ '╌╌╌╌╵ ┗━━━━┛
          ╚═╗███████╔═╝
            ╚═══════╝
    """
    # fmt: on
    if not value or ctx.resilient_parsing:
        return
    echo = partial(pt.echo, file=sys.stdout)

    vfmt = lambda s: pt.Fragment(s, "green")
    ufmt = lambda s: pt.Fragment(s, "gray")
    regex = re.compile("([▐█▌]+)|([┃━┏┳┓┣╋┫┗┻┛]+)|([╎╌└╵╴╷┘,'┐┴┬-]+)|(.+?)")
    group_colors = [pt.cv.DARK_RED, pt.NOOP_COLOR, pt.cv.GRAY, pt.cv.DARK_GOLDENROD]

    def replace(m: re.Match) -> str:
        def _iter(m: re.Match) -> str:
            for g, st in zip(m.groups(), group_colors):
                yield "".join(pt.render(g or "", st))

        return "".join(_iter(m))

    echo(regex.sub(replace, invoke_version.__doc__))

    echo(f"{APP_NAME:>12s}  {vfmt(APP_VERSION):<14s}  {ufmt(APP_UPDATED)}")
    echo(f"{'pytermor':>12s}  {vfmt(pt.__version__):<14s}  {ufmt(pt.__updated__)}")
    echo(f"{'es7s-commons':>12s}  {vfmt(es7s_commons.PKG_VERSION):<14s}  {ufmt(es7s_commons.PKG_UPDATED)}")

    def _echo_path(label: str, path: str):
        echo(
            pt.Composite(
                pt.Text(label + ":", width=17),
                format_path(path, color=True, repr=False),
            )
        )

    if value > 1:
        echo(file=io)
        _echo_path("Executable", sys.executable)
        _echo_path("Entrypoint", __file__)
    ctx.exit()


@pass_context
def invoke_defualt(
    ctx: click.Context,
    buffered: bool,
    input: io.BufferedReader,
    output: io.BufferedWriter = None,
    **kwargs,
):
    if input is None:
        ctx.fail(
            "INPUT is required when running in the default mode. "
            "Specify a file or '-' to read from stdin."
        )
    if buffered is None:
        try:
            buffered = input.fileno() != STDIN_FILENO
        except UnsupportedOperation:
            pass  # looks like input is not a fp => testing environment

    setup = Setup(**kwargs)
    if setup.group:
        buffered = True

    r = CliReader(io.TextIOWrapper(input))
    w = CliWriter(setup, buffered, output)

    chars = Char.parse(r.read())
    w.write(chars)

# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import io
import re

import pytermor as pt
import click
import sys

from es7s_commons import format_path

from . import APP_NAME, APP_VERSION, APP_UPDATED
from .common import MultiChoice
from .core import parse, Attribute
from .reader import CliReader
from .writer import CliWriter


class Context(click.Context):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("terminal_width", min(120, pt.get_terminal_width()))
        super().__init__(*args, **kwargs)


class Command(click.Command):
    context_class = Context
    pass


class VersionOption(click.Option):
    def __init__(self, *args, **kwargs):
        # fmt: off
        """
              ███████                                                                   
   ₑₛ₇ₛ    ║███╔═══╗███║                  
   ═┏━┓┏━┓═╣███║ ║█████╠═┏━┓════┏━┓═┏━┓════════┏━━━━┓
    ┃ ┗┛ ┃ ║███║ ╚═╗███║ ┃ ┃    ┃ ┗┳┛ ┃ ╎ -┬-╵ ┃ ━━━┫
    ┃ ┏┓ ┃ ║█████║ ║███║ ┃ ┗━━┓ ┃ ┣━┫ ┃ ╎ -┴-┐ ┣━━━ ┃
    ┗━┛┗━┛ ║███╔═╝ ║███║ ┗━━━━┛ ┗━┛ ┗━┛ '╌╌╌╌╵ ┗━━━━┛
           ╚═╗███████╔═╝                                                                
             ╚═══════╝
        """
        # fmt: on

        kwargs.setdefault("count", True)
        kwargs.setdefault("expose_value", False)
        kwargs.setdefault("is_eager", True)
        kwargs["callback"] = self.callback
        super().__init__(*args, **kwargs)

    def callback(self, ctx: click.Context, param: click.Parameter, value: int):
        if not value or ctx.resilient_parsing:
            return
        vfmt = lambda s: pt.Fragment(s, "green")
        ufmt = lambda s: pt.Fragment(s, "gray")
        pt.echo(
            re.sub(
                "(█+)|([┃━┏┳┓┣╋┫┗┻┛]+)|([╎╌└╵╴╷┘,'┐┴┬-]+)|(.+?)",
                lambda m: "".join(
                    pt.render(g or "", st)
                    for g, st in zip(
                        m.groups(),
                        [
                            pt.cv.DARK_RED,
                            pt.NOOP_COLOR,
                            pt.cv.GRAY,
                            pt.cv.DARK_GOLDENROD,
                        ],
                    )
                ),
                VersionOption.__init__.__doc__,
            )
        )
        pt.echo(f"{APP_NAME:>12s}  {vfmt(APP_VERSION):<14s}  {ufmt(APP_UPDATED)}")
        pt.echo(f"{'pytermor':>12s}  {vfmt(pt.__version__):<14s}  {ufmt(pt.__updated__)}")
        # pt.echo(f"{'es7s-commons':>12s}  {vfmt((ec := util.find_spec('es7s_commons._version').loader.load_module('es7s_commons._version')).__version__):<14s}  {ufmt(ec.__updated__)}")

        if value > 1:
            pt.echo()
            self._echo_path("Executable", sys.executable)
            self._echo_path("Entrypoint", __file__)
        ctx.exit()

    def _echo_path(self, label: str, path: str):
        pt.echo(
            pt.Composite(
                pt.Text(label + ":", width=17),
                format_path(path, color=True, repr=False),
            )
        )


@click.command(
    cls=Command,
    no_args_is_help=True,
    help="Read data from FILE, find all valid UTF-8 byte sequences, decode them and display as separate Unicode code "
    "points. Use '-' as FILE to read from stdin instead.\n\n"
    "\b\bBuffering\n\n"
    "The application works in two modes: buffered (the default) and unbuffered. In buffered "
    "mode the result begins to appear only after EOF is encountered. This is suitable for relatively short and "
    "predictable inputs (e.g. from a file) and allows to produce the most compact output (because all the "
    "column sizes are known from the start). When input is not a file and can proceed infinitely (e.g. a piped "
    "stream), the unbuffered mode comes in handy: the application prints the results in real time, as soon "
    "as the type of each byte sequence is determined. Despite the name, it actually uses a tiny input buffer "
    "(size is 4 bytes), but it's the only way to handle UTF-8 stream and distinguish valid sequences from "
    "broken ones; in truly unbuffered mode the output would consist of ASCII-7 characters (0x00-0x7F) and "
    "unrecognized binary data (0x80-0xFF) only, which is not something the application was made for.",
)
@click.argument("file", type=click.File("rb"), nargs=1, required=True)
@click.option(
    "-f",
    "--format",
    type=MultiChoice(Attribute.list()),
    default=",".join(Attribute),
    help="Comma-separated list of columns to show. The order of items determines the order of columns in the "
    "output. Default is to show all columns in the order specified above, one code point per line. Note that 'count' "
    "column requires '--squash' or '--count' mode, while 'offset' column is hidden when '--count' is active. "
    "'number' is the ID of code point (U+xxxx). Newline separators are disabled if the format specified as a single "
    "'char' column.",
)
@click.option(
    "-u",
    "--unbuffered",
    is_flag=True,
    help="Start streaming the result as soon as possible, do not read the whole input preemptively. See BUFFERING "
    "paragraph above for the details.",
)
@click.option(
    "-s",
    "--squash",
    is_flag=True,
    help="Replace all sequences of repeating characters with the first character from each, followed by a length of "
    "the sequence.",
)
@click.option(
    "-c",
    "--count",
    is_flag=True,
    help="Count unique code points, sort ascending and display totals instead of normal output. Disables unbuffered "
         "mode. Implies '--squash'.",
)
@click.option("--decimal", is_flag=True, help="Use decimal offsets instead of hexadecimal.")
@click.option("--version", "-V", cls=VersionOption, help="Show the version and exit.")
def entrypoint(file: io.BufferedReader, unbuffered: bool, **kwargs):
    if kwargs.get("count", None):
        kwargs.update({
            "squash": True,
        })
        unbuffered = False

    r = CliReader(io.TextIOWrapper(file))
    w = CliWriter(**kwargs)
    if unbuffered:
        w.write(parse(r.read()))
    else:
        w.write([*parse(r.read())])

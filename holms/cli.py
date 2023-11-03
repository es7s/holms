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
        kwargs.setdefault("terminal_width", min(100, pt.get_terminal_width()))
        kwargs.setdefault("help_option_names", ["-?", "--help"])
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
    "\b\bColumns\n\n"
    "List of valid column names for '--format' option and example output string:\n\n"
    "  \b  0x0aa‥ # 190 U+2588 ▕ █ ▏1218x So FULL BLOCK\n\n"
    "  \b  offset index number char count type name\n\n"
    "By default each code point is printed on a new line and formatted as a set of fields from the list above, in that "
    "exact order. Note that '--squash' mode is required for 'count' column to appear, while '--total' mode hides "
    "'offset' and 'index' columns. 'number' is the ID of code point (U+xxxx). Newline separators are disabled if the "
    f"format is a single 'char' column.\n\nDefault: '--format={','.join(Attribute)}'.\n\n"
    "\n\n"
    "@TODO: typename utf8\n\n"
    "\n\n"
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
    "-u",
    "--unbuffered",
    is_flag=True,
    help="Do not wait for EOF, start to stream the results as soon as possible. See BUFFERING section above "
    "for the details.",
)
@click.option(
    "-s",
    "--squash",
    is_flag=True,
    help="Replace all sequences of repeating characters with one of each, together with initial length of "
    "the sequence.",
)
@click.option(
    "-t",
    "--total",
    is_flag=True,
    help="Count unique code points, sort ascending and display totals instead of normal output. Implies '--squash' "
    " and forces buffered mode.",
)
@click.option(
    "-f",
    "--format",
    type=MultiChoice(Attribute.list(), hide_choices=True),
    default=",".join(Attribute),
    help="Comma-separated list of columns to show (order is preserved). See COLUMNS section above.",
)
@click.option(
    "-c",
    "--color",
    "output_mode",
    flag_value=pt.OutputMode.XTERM_256.value,
    help="Explicitly turn on colored results; usually this is applied by the app automatically, when output/receiving "
    "device is a terminal emulator with corresponding capabilities.",
)
@click.option(
    "-C",
    "--no-color",
    "output_mode",
    flag_value=pt.OutputMode.NO_ANSI.value,
    help="Explicitly turn off colored results; usually this is applied by the app automatically, when the output "
    "is being piped or redirected elsewhere.",
)
@click.option("--decimal", is_flag=True, help="Use decimal offsets instead of hexadecimal.")
@click.option("--legend", "-L", cls=VersionOption, help="@TODO")
@click.option("--version", "-V", cls=VersionOption, help="Show the version and exit.")
def entrypoint(file: io.BufferedReader, unbuffered: bool, **kwargs):
    if kwargs.get("total", None):
        kwargs.update({"squash": True})
        unbuffered = False

    r = CliReader(io.TextIOWrapper(file))
    w = CliWriter(**kwargs)
    if unbuffered:
        w.write(parse(r.read()))
    else:
        w.write([*parse(r.read())])

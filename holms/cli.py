# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click
import pytermor as pt

from .cmd import invoke_defualt, invoke_legend, invoke_version
from .common import Attribute, HiddenIntRange
from .common import MultiChoice


class AppMode(pt.ExtendedEnum):
    DEFAULT = "default"
    VERSION = "version"
    LEGEND = "legend"


class Context(click.Context):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("terminal_width", min(100, pt.get_terminal_width()))
        kwargs.setdefault("help_option_names", ["--help", "-?"])
        super().__init__(*args, **kwargs)


class Command(click.Command):
    context_class = Context
    pass


@click.command(
    cls=Command,
    no_args_is_help=True,
    help="Read data from INPUT file, find all valid UTF-8 byte sequences, decode them and display as separate "
    "Unicode code points. Use '-' as INPUT to read from stdin instead."
    "\n\n\n\n"
    "\b\bBuffering"
    "\n\n"
    "The application works in two modes: buffered (the default if INPUT is a file) and unbuffered (default when "
    "reading from stdin). Options '-b'/'-u' explicitly override output mode regardless of the default setting."
    "\n\n"
    "In buffered mode the result begins to appear only after EOF is encountered (i.e., the WHOLE file has been read "
    "to the buffer). This is suitable for short and predictable inputs and produces the most compact output with fixed "
    "column sizes."
    "\n\n"
    "The unbuffered mode comes in handy when input is an endless piped stream: the results will be displayed in "
    "real time, as soon as the type of each byte sequence is determined, but the output column widths are not fixed "
    "and can vary as the process goes further.",
)
@click.argument("input", type=click.File("rb"), nargs=1, required=False)
@click.option(
    "-b/-u",
    "--buffered/--unbuffered",
    default=None,
    help="Explicitly set to wait for EOF before processing the output (buffered), or to stream the results in parallel "
    "with reading, as soon as possible (unbuffered). See BUFFERING section above for the details.",
)
@click.option(
    "-m",
    "--merge",
    is_flag=True,
    help="Replace all sequences of repeating characters with one of each, together with initial length of "
    "the sequence.",
)
@click.option(
    "-g",
    "--group",
    count=True,
    type=HiddenIntRange(0, 3, clamp=True),
    help="Group the input by code points (=count unique), sort descending and display counts instead of "
    "normal output. Implies '--merge' and forces buffered mode. Specifying the option twice ('-gg') "
    "results in grouping by code point category instead, while doing it thrice ('-ggg') makes the app "
    "group the input by super categories.",
)
@click.option(
    "-f",
    "--format",
    "_columns",
    type=MultiChoice(Attribute.list(), hide_choices=True),
    help="Comma-separated list of columns to show (order is preserved). Run 'holms --legend' to see the details.",
)
@click.option(
    "-F",
    "--full",
    "_all_columns",
    is_flag=True,
    help="Display ALL columns.",
)
@click.option(
    "-S",
    "--static",
    is_flag=True,
    help="Do not shrink columns by collapsing the prefix when possible.",
)
@click.option(
    "-c/-C",
    "--color/--no-color",
    default=None,
    help="Explicitly turn colored results on or off; if not specified, will be selected automatically "
    "depending on the type and capabilities of receiving device (e.g. colors will be enabled for a terminal "
    "emulator and disabled for piped/redirected output).",
)
@click.option(
    "--decimal",
    "decimal_offset",
    is_flag=True,
    help="Use decimal byte offsets instead of hexadecimal.",
)
@click.option(
    "--legend",
    "-L",
    "mode_legend",
    is_flag=True,
    help="Show detailed info on an output format and code point category chromacoding, and exit.",
)
@click.option(
    "--version",
    "-V",
    "mode_version",
    count=True,
    is_eager=True,
    help="Show the version and exit.",
)
def entrypoint(color: bool|None, mode_legend: bool, mode_version: bool, **kwargs):
    output_mode = pt.OutputMode.AUTO
    if color is not None:
        output_mode = [pt.OutputMode.NO_ANSI, pt.OutputMode.XTERM_256][color]
    pt.RendererManager.set_default(pt.SgrRenderer(output_mode))

    if mode_legend:
        invoke_legend(**kwargs)
        return
    if mode_version:
        invoke_version(value=mode_version, **kwargs)
        return

    invoke_defualt(**kwargs)

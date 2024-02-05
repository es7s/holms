# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import time

import click
import pytermor as pt

from holms import APP_NAME
from holms.cmd import invoke_run, invoke_version, invoke_legend, invoke_format, invoke_path
from holms.core import Attribute
from .common import MultiChoice, HiddenIntRange, Context, CliGroup, CliCommand
from holms.shared import logger
from holms.shared.log import init_log, destroy_log


def entrypoint_fn(*args, **kwargs):
    ts_start = time.time_ns()
    try:
        # _init_io is called from entrypoint__
        # so that click can parse all cli args
        entrypoint__(*args, **kwargs)
    finally:
        ts_delta = time.time_ns() - ts_start
        logger(require=False).debug(f"Total time: {pt.format_si(ts_delta/1e9, unit='s')}")

    _destroy_io()


def _init_io(color: bool | None, verbose: int = 0, **kwargs):
    init_log(verbose)
    if color is not None:
        output_mode = [pt.OutputMode.NO_ANSI, pt.OutputMode.XTERM_256][color]
        pt.ConfigManager.get().force_output_mode = output_mode


def _destroy_io():
    pt.ConfigManager.get().force_output_mode = ""
    destroy_log()


@click.command(
    cls=CliCommand,
    short_help="break input down to unicode codepoints",
    help="Read data from INPUT file, find all valid UTF-8 byte sequences, decode them and display as separate "
    "Unicode code points. Use '-' as INPUT to read from stdin instead."
    "\n\n\n\n"
    "\b\bBuffering"
    "\n\n"
    "The application works in two modes: buffered (default if INPUT is a file) and unbuffered (default when "
    "reading from stdin). Options '-b'/'-u' explicitly override output mode regardless of the default setting."
    "\n\n"
    "In buffered mode the result begins to appear only after EOF is encountered (i.e., the WHOLE file has been read "
    "to the buffer). This is suitable for short and predictable inputs and produces the most compact output with fixed "
    "column sizes."
    "\n\n"
    "Unbuffered mode comes in handy when input is an endless piped stream: the results will be shown in "
    "real time, as soon as the type of each byte sequence is determined, but the output columns are dynamic "
    "and can expand as the process goes further. Strictly speaking, this mode is also buffered, but the buffer "
    "has a minimum possible size for working with UTF-8 encoded data (4 bytes).",
)
@click.argument(
    "input",
    type=click.File("rb"),
    nargs=1,
    required=False,
)
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
    "_merge",
    is_flag=True,
    help="Replace all sequences of repeating characters with one of each, together with initial length of "
    "the sequence.",
)
@click.option(
    "-g",
    "--group",
    "group_level",
    count=True,
    type=HiddenIntRange(0, 3, clamp=True),
    help="Group the input by code points (=count unique), sort descending and display counts instead of "
    "normal output. Implies '--merge' and forces buffered ('-b') mode. Specifying the option twice ('-gg') "
    "results in grouping by code point category instead, while doing it thrice ('-ggg') makes the app "
    "group the input by super categories.",
)
@click.option(
    "-o",
    "--oneline",
    is_flag=True,
    help="Remove all newline characters (0x0a LINE FEED) from the output.",
)
@click.option(
    "-f",
    "--format",
    "_columns",
    type=MultiChoice(Attribute.list(), hide_choices=True),
    help="Comma-separated list of columns to show (order is preserved). Run 'holms format' to see the details.",
)
@click.option(
    "-n",
    "--names",
    "_names",
    is_flag=True,
    help="Display names instead of abbreviations. Affects `cat` and `block` columns, but only if "
         "column in question is already present on the screen. Note that these columns can still "
         "display only the beginning of the attribute, unless '-r' is provided.",
)
@click.option(
    "-a",
    "--all",
    "all_columns",
    is_flag=True,
    help="Display ALL columns.",
)
@click.option(
    "-r",
    "--rigid",
    "_rigid",
    is_flag=True,
    help="By default some columns can be compressed beyond the nominal width, if all current values fit and there "
         "is still space left. This option disables column shrinking (but they still will be expanded when needed).",
)
@click.option(
    "--decimal",
    "decimal_offset",
    is_flag=True,
    help="Use decimal byte offsets instead of hexadecimal.",
)
def run(**kwargs):
    invoke_run(**kwargs)


@click.command(cls=CliCommand, short_help="show code point category chromacoding details")
def legend(**kwargs):
    """Show details on code point category chromacoding."""
    invoke_legend(**kwargs)


@click.command(cls=CliCommand, short_help="show column names and format details")
def format(**kwargs):
    """Show format details and output column names."""
    invoke_format(**kwargs)


@click.command(cls=CliCommand, short_help="show application version")
@click.option("-s", "--short", is_flag=True, help="Display the version number only.")
def version(short: bool, **kwargs):
    """Show application version."""
    invoke_version(short, **kwargs)


@click.command(cls=CliCommand, short_help="show application paths")
def path(**kwargs):
    """Show application paths."""
    invoke_path(**kwargs)


@click.group(
    name="cli",
    cls=CliGroup,
    commands=[run, version, format, legend, path],
    context_settings=Context.DEFAULT_SETTINGS,
)
@click.option(
    "-c/-C",
    "--color/--no-color",
    default=None,
    help=f"""Explicitly turn colored results on or off; if not specified, will
    be selected automatically depending on the type and capabilities of
    receiving device (e.g. colors will be enabled for a terminal emulator and
    disabled for piped/redirected output). Should be defined before the command:
    '{APP_NAME} -c run ...'""",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    type=HiddenIntRange(0, 1, clamp=True),
    help=f"Display additional information about what is going on. ",
)
def entrypoint__(**kwargs):
    _init_io(**kwargs)

import io
import sys
import threading
from collections import deque

import click

from .common import MultiChoice
from .core import parse, Attribute, Char
from .reader import CliReader
from .writer import CliWriter


@click.command(
    no_args_is_help=True,
    help="Read data from FILE, find all valid UTF-8 byte sequences, decode them and display as separate Unicode code "
    "points. Use '-' as FILE to read from stdin instead.",
)
@click.argument("file", type=click.File("rb"), nargs=1, required=True)
@click.option(
    "-f",
    "--format",
    type=MultiChoice(Attribute.list()),
    default=",".join(Attribute),
    help="Comma-separated list of attributes to show. Default is to show all of them. The order of attributes determines the order of columns in the output. Note that 'count' is shown only "
         "if '-s' is specified. 'number' is the ID of code point (U+xxxx).",
)
@click.option(
    "-u",
    "--unbuffered",
    is_flag=True,
    help="Start streaming the result as soon as possible, do not read the whole file preemptively. See BUFFERING "
         "below for the details.",
)
@click.option(
    "-s",
    "--squash",
    is_flag=True,
    help="Replace all sequences of repeating characters with the first character from each, followed by a length of "
    "the sequence.",
)
@click.option("--decimal", is_flag=True, help="Use decimal offsets instead of hexadecimal.")
def entrypoint(file: io.BufferedReader, unbuffered: bool, **kwargs):
    ic = deque[Char|None]()
    read_next = threading.Event()
    read_end = threading.Event()
    r = CliReader(io.TextIOWrapper(file), ic, read_next, read_end)
    if unbuffered:
        w = CliWriter(sys.stdout, ic, read_next, read_end,unbuffered,  **kwargs)
    else:
        raise NotImplementedError
        w = CliWriter(sys.stdout, [*ic], read_next, read_end,unbuffered,  **kwargs)
    w.start()
    r.read()

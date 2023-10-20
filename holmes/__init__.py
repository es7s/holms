import io

import click

from holmes.core import parse
from holmes.input import CliReader
from holmes.output import CliWriter


@click.command(no_args_is_help=True, help="")
@click.argument("file", type=click.File("rb"), nargs=1, required=True)
@click.option(
    "-D",
    "--decimal",
    is_flag=True,
    help="Use decimal addresses instead of hexadecimal.",
)
@click.option(
    "-s",
    "--squash",
    is_flag=True,
    help="Replace all sequences of repeating characters with the first character from each, followed by a length of "
         "the sequence.",
)
def entrypoint(file: io.BufferedReader, **kwargs):
    r = CliReader(io.TextIOWrapper(file))
    w = CliWriter(**kwargs)
    w.print_string(parse(r.read()))


entrypoint()

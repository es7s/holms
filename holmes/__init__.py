import io

import click

from holmes.core import parse
from holmes.input import CliReader
from holmes.output import CliWriter


@click.command(no_args_is_help=True, help="")
@click.argument("file", type=click.File('rb'), nargs=1, required=True)
@click.option("--decimal", is_flag=True, help="Use decimal addresses instead of hexadecimal.")
def entrypoint(file: io.BufferedReader, decimal: bool):
    r = CliReader(io.TextIOWrapper(file))
    w = CliWriter(decimal_idx=decimal)
    w.print_string(parse(r.read()))


entrypoint()

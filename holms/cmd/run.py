# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import io
import sys
from io import UnsupportedOperation
from pty import STDIN_FILENO

from holms.core import Char, Options
from holms.core.writer import RunStats
from holms.shared import logger


def invoke_run(
    buffered: bool,
    input: io.BufferedReader,
    output: io.BufferedWriter = None,
    **kwargs,
) -> RunStats:
    if input is None:
        input = sys.stdin.buffer

    if buffered is None:
        try:
            buffered = input.fileno() != STDIN_FILENO
        except UnsupportedOperation:
            pass  # looks like input is not a fp => its probably testing environment

    opt = Options(**kwargs)
    if opt.group:
        buffered = True

    from holms.core.reader import CliReader
    from holms.core.writer import CliWriter

    r = CliReader(io.TextIOWrapper(input))
    w = CliWriter(opt, buffered, output)

    chars = Char.parse(r.read())
    stats = w.write(chars)
    logger().info(f"Processed {stats.proc_bytes} bytes, {stats.proc_chars} chars")

    return stats

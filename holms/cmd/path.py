# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import sys
from functools import partial

import pytermor as pt
from es7s_commons import format_path


def invoke_path(**kwargs):
    echo = partial(pt.echo, file=sys.stdout)

    def _echo_path(label: str, path: str):
        echo(
            pt.Composite(
                pt.Text(label + ":", width=17),
                format_path(path, color=True, repr=False),
            )
        )

    _echo_path("Executable", sys.executable)
    _echo_path("Entrypoint", __file__)

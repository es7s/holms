# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import sys
from functools import partial
from importlib.resources import read_text

import pytermor as pt

from holms import APP_NAME


def invoke_format(**kwargs):
    echo = partial(pt.echo, file=sys.stdout)

    raw = read_text(f"{APP_NAME}.data", "format.ptpl")
    rendered = pt.template.render(raw, pt.RendererManager.get())
    echo(rendered)

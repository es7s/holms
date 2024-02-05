# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import re
import sys
from functools import partial

import es7s_commons
import pytermor as pt

from holms import APP_NAME, APP_VERSION, APP_UPDATED


def invoke_version(short: bool, **kwargs):
    # fmt: off
    """
             ███████
    ₑₛ₇ₛ  ║███╔═══╗███║
   ┏━┓┏━┓═╣███║ ║█████╠═┏━┓════┏━┓═┏━┓════════┏━━━━┓
   ┃ ┗┛ ┃ ║███║▐█▌╗███║ ┃ ┃    ┃ ┗┳┛ ┃ ╎ -┬-╵ ┃ ━━━┫
   ┃ ┏┓ ┃ ║█████╔╝║███║ ┃ ┗━━┓ ┃ ┣━┫ ┃ ╎ -┴-┐ ┣━━━ ┃
   ┗━┛┗━┛ ║███╔═╝ ║███║ ┗━━━━┛ ┗━┛ ┗━┛ '╌╌╌╌╵ ┗━━━━┛
          ╚═╗███████╔═╝
            ╚═══════╝
    """
    # fmt: on
    echo = partial(pt.echo, file=sys.stdout)

    if short:
        echo(APP_VERSION)
        return

    vfmt = lambda s: pt.Fragment(s, "green")
    ufmt = lambda s: pt.Fragment(s, "gray")
    regex = re.compile("([▐█▌]+)|([┃━┏┳┓┣╋┫┗┻┛]+)|([╎╌└╵╴╷┘,'┐┴┬-]+)|(.+?)")
    group_colors = [pt.cv.DARK_RED, pt.NOOP_COLOR, pt.cv.GRAY, pt.cv.DARK_GOLDENROD]

    def replace(m: re.Match) -> str:
        def _iter(m: re.Match) -> str:
            for g, st in zip(m.groups(), group_colors):
                yield "".join(pt.render(g or "", st))

        return "".join(_iter(m))

    echo(regex.sub(replace, invoke_version.__doc__))

    echo(f"{APP_NAME:>12s}  {vfmt(APP_VERSION):<14s}  {ufmt(APP_UPDATED)}")
    echo(f"{'pytermor':>12s}  {vfmt(pt.__version__):<14s}  {ufmt(pt.__updated__)}")
    echo(f"{'es7s-commons':>12s}  {vfmt(es7s_commons.PKG_VERSION):<14s}  {ufmt(es7s_commons.PKG_UPDATED)}")

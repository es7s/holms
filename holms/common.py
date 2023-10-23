# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click
import typing as t


class MultiChoice(click.Choice):
    def convert(self, value: t.Any, *args, **kwargs) -> t.Any:
        return [super(MultiChoice, self).convert(v, *args, **kwargs) for v in value.split(",")]

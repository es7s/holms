# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import click
import typing as t


class MultiChoice(click.Choice):
    def __init__(self, choices: t.Sequence[str], case_sensitive: bool = True, hide_choices: bool = False) -> None:
        self._hide_choices = hide_choices
        super().__init__(choices, case_sensitive)

    def convert(self, value: t.Any, *args, **kwargs) -> t.Any:
        return [super(MultiChoice, self).convert(v, *args, **kwargs) for v in value.split(",")]

    def get_metavar(self, param: click.Parameter) -> str:
        if self._hide_choices:
            return ""
        return super().get_metavar(param)

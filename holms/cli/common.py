# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations
import typing as t

import click
import pytermor as pt


class MultiChoice(click.Choice):
    def __init__(
        self,
        choices: t.Sequence[str],
        case_sensitive: bool = True,
        hide_choices: bool = False,
    ) -> None:
        self._hide_choices = hide_choices
        super().__init__(choices, case_sensitive)

    def convert(self, value: t.Any, *args, **kwargs) -> t.Any:
        return [super(MultiChoice, self).convert(v, *args, **kwargs) for v in value.split(",")]

    def get_metavar(self, param: click.Parameter) -> str:
        if self._hide_choices:
            return ""
        return super().get_metavar(param)


class HiddenIntRange(click.IntRange):
    def _describe_range(self) -> str:
        return ""


class Formatter(click.HelpFormatter):
    def write_dl(self, rows, col_max: int = 20, col_spacing: int = 2) -> None:
        super().write_dl(rows, col_max, col_spacing)


class Context(click.Context):
    DEFAULT_SETTINGS = {
        "terminal_width": min(90, pt.get_terminal_width()),
        "help_option_names": ("-?", "--help"),
    }
    formatter_class = Formatter


class CliCommand(click.Command):
    context_class = Context
    ...


class CliGroup(click.Group):
    context_class = Context
    ...

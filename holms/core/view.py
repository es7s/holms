# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import abc
from abc import abstractmethod
from logging import shutdown

import pytermor as pt

from holms.shared import CacheInfo, logger
from .attr import Attribute
from .char import Groups
from .opt import Options
from .writer import Column, Row


class _ViewRegistry:
    _views = dict()

    @classmethod
    def get(cls, attr: Attribute) -> IView:
        if fmt := cls._views.get(attr, None):
            return fmt
        raise RuntimeError(f"No view defined for {attr!r}")

    @classmethod
    def add(cls, v: IView, attr: Attribute):
        if not attr:
            raise RuntimeError(f"No attr defined for {v!r}: {attr!r}")
        if attr in cls._views.keys():
            raise RuntimeError(
                f"There is an already registered view for {attr!r}."
                f"IView inheritors should not be instantiated directly."
            )
        cls._views.update({attr: v})

    @classmethod
    def reset(cls):
        for v in cls._views.values():
            v.reset(shutdown=True)


class _ViewMeta(abc.ABCMeta):
    def __new__(__mcls: type[_ViewMeta], __name, __bases, __namespace, **kwargs):
        cls: _ViewMeta | type[IView] = super().__new__(
            __mcls, __name, __bases, __namespace, **kwargs
        )
        if len(__bases):
            cls(cls.attr())  # <- instantiate
        return cls


class IView(metaclass=_ViewMeta):
    def __new__(cls, attr: Attribute):
        inst = super().__new__(cls)
        if not isinstance(attr, Attribute):
            raise RuntimeError(f"Invalid attr type for {inst}: {attr!r}")
        _ViewRegistry.add(inst, attr)
        return inst

    def __init__(self, *args):
        super().__init__()
        self._cache_stats: dict[str, CacheInfo] = {}

    @staticmethod
    @abstractmethod
    def attr() -> Attribute:
        ...

    def reset(self, shutdown=False):
        for m in self.__dir__():
            if m.startswith("__"):
                continue
            a = getattr(self, m)
            if hasattr(a, "cache_clear"):
                cur_info_fn = getattr(a, "cache_info")
                clear_fn = getattr(a, "cache_clear")
                if not (cum := self._cache_stats.get(m)):
                    self._cache_stats.update({m:  (cum := CacheInfo())})
                cum.upd_from_tuple(cur_info_fn())
                clear_fn()

        if shutdown:
            for k in sorted(self._cache_stats.keys()):
                self._cache_stats.get(k).debug(f"{self.attr():>12s}  {k:>18s}")

    def format(self, opt: Options, row: Row, column: Column = None) -> str | None:
        """
        :returns: None if the value should be rendered as-is, without
                  any processing
        """
        return None

    @abstractmethod
    def render(self, opt: Options, row: Row, column: Column = None, grp: Groups = None) -> str:
        ...


def get_view(attr: Attribute) -> IView:
    return _ViewRegistry.get(attr)


def reset_views():
    _ViewRegistry.reset()

# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations
from dataclasses import dataclass
import pytermor as pt
from . import logger


@dataclass
class CacheInfo:
    hits: int = 0
    misses: int = 0
    maxsize: int = 0
    currsize: int = 0
    resets: int = 0

    def upd_from_tuple(self, origin: "_CacheInfo") -> CacheInfo:
        self.hits += origin.hits
        self.misses += origin.misses
        self.maxsize = origin.maxsize
        self.currsize = max(self.currsize, origin.currsize)
        self.resets += 1
        return self

    def debug(self, origin: str):
        resets_str = f"{self.resets:>2d}"
        hits_str = f"{self.hits:>6d}"
        misses_str = f"{self.misses:>6d}"
        hratio_str = f"unused"
        size_str = f"{self.currsize:>4d}"
        hits_st = None
        misses_st = None
        size_st = None

        if self.hits == 0 and self.misses == 0:
            st = pt.cv.GRAY_42
            resets_str += " requests"
            hits_str, misses_str, size_str = ("--",) * 3
        else:
            resets_str += " resets"
            st = pt.NOOP_STYLE
            hratio = self.hits / (self.hits + self.misses)

            if hratio < 0.5:
                misses_st = pt.cv.RED
            elif hratio < 2:
                hits_st = pt.cv.GREEN

            hratio_str = pt.format_auto_float(hratio * 100, 3) + "% HR"

        if self.currsize == self.maxsize and self.currsize > 1:
            size_st = pt.cv.YELLOW

        sep = pt.pad(2)
        frags = [
            (f"{origin:>36s}{sep}|{sep}", st),
            (f"{hratio_str:>8s}{sep}", misses_st or hits_st or st),
            (f"{resets_str:<11s}{sep}", st),
            (f"{hits_str:>6s} hits{sep}", hits_st or st),
            (f"{misses_str:>6s} misses{sep}", misses_st or st),
            (f"{size_str:>4s}/{self.maxsize:4d} size", size_st or st),
        ]
        logger().debug(pt.render(pt.Text(*frags)))

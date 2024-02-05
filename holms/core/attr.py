# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import pytermor as pt


class Attribute(str, pt.ExtendedEnum):
    OFFSET = "offset"
    INDEX = "index"
    RAW = "raw"
    NUMBER = "number"
    CHAR = "char"
    COUNT = "count"
    CAT = "cat"
    NAME = "name"
    BLOCK = "block"

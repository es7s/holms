# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import io
import sys
import typing
from codecs import BufferedIncrementalDecoder
from collections.abc import Iterable


class SurrogateAwareDecoder(BufferedIncrementalDecoder):
    def __init__(self):
        super().__init__(errors="surrogatepass")

    def _buffer_decode(self, input, errors, final):
        try:
            return input.decode(errors=errors), len(input)
        except UnicodeDecodeError as e:
            if e.start == 0:
                return bytes((input[0],)), 1
            else:
                return input[: e.start].decode(errors=errors), e.start


class CliReader:
    _BUF_SIZE = 4

    def __init__(self, io_: io.TextIOWrapper = sys.stdin):
        self._io = io_

    def read(self) -> Iterable[typing.AnyStr]:
        buf = SurrogateAwareDecoder()

        while buf.getstate()[0] or not self._io.closed:
            if self._io.closed:
                yield from buf.decode(b"", True)
            elif b := self._io.buffer.read(self._BUF_SIZE):
                yield from buf.decode(b)
            else:
                self._io.close()

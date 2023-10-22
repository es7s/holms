import io
import sys
import typing
from codecs import BufferedIncrementalDecoder
from collections import deque
from collections.abc import Iterable
from threading import Thread, Event

from h0lmes import Char


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
    _BUF_SIZE = 16

    def __init__(self, io_: io.TextIOWrapper, ic: deque[Char | None], read_next: Event, read_end: Event):
        self._io = io_
        self._ic = ic
        self._read_next = read_next
        self._read_end = read_end

    def read(self):
        buf = SurrogateAwareDecoder()

        def _loop():
            while buf.getstate()[0] or not self._io.closed:
                if self._io.closed:
                    yield from buf.decode(b"", True)
                elif b := self._io.buffer.read(self._BUF_SIZE):
                    yield from buf.decode(b)
                else:
                    self._io.close()

        for c in _loop():
            self._ic.append(Char(c))
            self._read_next.set()
        self._read_end.set()

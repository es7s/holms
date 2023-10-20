import io
import sys
import typing
from codecs import BufferedIncrementalDecoder
from collections.abc import Iterable


class Decoder(BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final):
        try:
            return input.decode(errors=errors), len(input)
        except UnicodeDecodeError as e:
            if e.start == 0:
                return bytes((input[0],)), 1
            else:
                return input[:e.start].decode(errors=errors), e.start


class CliReader:
    _BUF_SIZE = 6401

    def __init__(self, io_: io.TextIOWrapper = sys.stdin):
        self._io = io_

    def read(self) -> Iterable[typing.AnyStr]:
        buf = Decoder(errors='surrogatepass')
        while buf.getstate()[0] or not self._io.closed:
            if self._io.closed:
                yield from buf.decode(b"", True)
                continue
            if b := self._io.buffer.read(self._BUF_SIZE):
                yield from buf.decode(b)
                continue
            self._io.close()

    def read2(self) -> Iterable[typing.AnyStr]:
        b = io.BytesIO()
        while True:
            pos = b.tell()
            try:
                yield from b.read().decode(errors='surrogatepass')
            except UnicodeDecodeError as e:
                b.seek(pos)
                print(e)
                if e.start == 0:
                    yield b.read(1)  # as byte
                else:
                    yield from b.read(e.start).decode(errors='surrogatepass')
            else:
                if not (n := self._io.buffer.read(self._BUF_SIZE)):
                    break
                b.seek(-b.write(n), io.SEEK_CUR)

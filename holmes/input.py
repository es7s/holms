import io
import sys
import typing
from collections.abc import Iterable


class CliReader:
    _BUF_SIZE = 6401

    def __init__(self, io_: io.TextIOWrapper = sys.stdin):
        self._io = io_

    def read(self) -> Iterable[typing.AnyStr]:
        b = io.BytesIO()
        while True:
            pos = b.tell()
            try:
                yield from b.read().decode(errors='surrogatepass')
            except UnicodeDecodeError as e:
                b.seek(pos)
                if e.start == 0:
                    yield b.read(1)
                else:
                    yield from b.read(e.start).decode(errors='surrogatepass')
            else:
                if not (n := self._io.buffer.read(self._BUF_SIZE)):
                    break
                b.seek(-b.write(n), io.SEEK_CUR)

# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import os
import sys


class _Main:
    def __init__(self, data_path, *args):
        self._data_path = data_path

    def run(self):
        f = open(os.path.join(self._data_path, 'unicode.bin'), 'wb')
        f_nosur = open(os.path.join(self._data_path, 'unicode_nosur.bin'), 'wb')
        f_oneline = open(os.path.join(self._data_path, 'unicode_oneline.bin'), 'wb')
        f_oneline_nosur = open(os.path.join(self._data_path, 'unicode_oneline_nosur.bin'), 'wb')
        for i in range(0, sys.maxunicode+1):
            f.write(chr(i).encode('utf8', errors='surrogatepass')+b'\n')
            f_nosur.write(chr(i).encode('utf8', errors='ignore')+b'\n')
            f_oneline.write(chr(i).encode('utf8', errors='surrogatepass'))
            f_oneline_nosur.write(chr(i).encode('utf8', errors='ignore'))
        f_oneline.close()
        f_oneline_nosur.close()


if __name__ == "__main__":
    args = [
        os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else "./misc"),
    ]
    _Main(*args).run()

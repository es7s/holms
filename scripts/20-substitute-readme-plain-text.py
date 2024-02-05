#!/bin/env python3
# -------------------------------------------------------------------------------
# es7s/holms
# (c) 2023 A. Shavykin <0.delameter@gmail.com>
# -------------------------------------------------------------------------------
import os.path
import re
import shutil
import sys


class _Main:
    def __init__(self, readme_path, data_path):
        self._readme_path = readme_path
        self._data_path = data_path

    def run(self):
        with open(self._readme_path, "rt") as fsrc:
            data = fsrc.read()
        shutil.copy(self._readme_path, self._readme_path + ".old")

        result = ""
        buf = None
        for line in data.splitlines(keepends=True):
            if m := re.search(R"@sub:([\w.-]+)", line):
                if buf:
                    print("ERROR: Nested substitute directive are not allowed")
                    exit(1)
                buf = line
                buf += "".join(["\n", *self._include(m.group(1)), "\n"])
            elif re.search(R"@sub[^:]", line):
                result += buf + line
                buf = None
            else:
                if not buf:
                    result += line

        with open(self._readme_path, "wt") as fdst:
            fdst.write(result)

    def _include(self, filename: str) -> str:
        source_path = os.path.join(self._data_path, filename)
        if os.path.exists(source_path):
            with open(source_path, "rt") as f:
                for line in f.readlines():
                    yield "    " + line.rstrip() + '\n'
        else:
            print(f"WARNING: File doesn't exist: {source_path!r}", file=sys.stderr)
        return ""


if __name__ == "__main__":
    args = [
        os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else "./README.md"),
        os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else "./misc"),
    ]
    _Main(*args).run()

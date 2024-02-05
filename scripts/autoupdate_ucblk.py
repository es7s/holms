# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import copy
import importlib.resources
import os
import re
import shutil
import sys
from collections.abc import Iterable
from typing import TextIO

import pytermor as pt
from es7s_commons import to_superscript, to_subscript

from holms.db import ucblk


def _cutout(string: str, span: tuple[int, int]) -> str:
    return string[: span[0]] + string[span[1] :]


def _extract_suffix(string: str) -> tuple[str, str | None]:
    old = ""
    letter = ""
    extension = ""
    marks = ""

    if m := re.search(r"^(Old)\b", string):
        old = "o"
        string = _cutout(string, m.span(0))

    if m := re.search(r"\b(\w+[- ])?([A-Z])\b", string):
        complem = m.group(1).lower()
        if "linear" not in complem:
            letter = m.group(2).lower()
            if complem.startswith("ext"):
                string = _cutout(string, m.span(0))
            else:
                string = _cutout(string, m.span(2)).removesuffix("-")

    while m := re.search(r"(Extend|Suppl|Addition)(\w+)", string, flags=re.IGNORECASE):
        if not letter:
            extension += (m.group(1)).lower()[:1].replace("e", "x")
            if "a" in extension and len(extension) > 1:
                extension = "+"
        string = _cutout(string, m.span(0))

    if m := re.search(r"Surrogates", string, flags=re.IGNORECASE):
        marks = "$"
        string = _cutout(string, m.span(0))

    return string, (marks + to_subscript(old) + to_superscript(extension + letter))


# noinspection SpellCheckingInspection
def _break_to_words(string: str) -> Iterable[str]:
    # ─────────────────────────────────────────┊────┊─
    # CJK Unified Ideographs                   ⎡CJU ⎤
    # CJK Unified Ideographs Extension A       ⎣CJUI⎦ᵃ  ← problem 1
    # CJK Radicals Supplement                  ┊CJRˢ┊
    # CJK Symbols and Punctuation              ┊CJSP┊
    # CJK Compatibility Forms                  ┊CJCF┊
    # CJK Compatibility                        ⎡CJC ⎤
    # CJK Compatibility Ideographs             ⎢CJCI⎥
    # CJK Compatibility Ideographs Supplement  ⎣CJCI⎦ˢ  ← problem 2
    # ─────────────────────────────────────────┊────┊─
    #                                          ┊¹²³⁴┊⁵
    repl = [
        ("CJK Unified Ideographs", "CJU"),  # CJUIᵃ → ┊CJUᵃ┊
        ("CJK Compatibility Ideographs ", "CJC"),  # CJCIˢ → ┊CJCˢ┊
        ("CJK", "CJ"),  # otherwise its impossible to fit these into 4 ch
    ]
    for s, d in repl:
        string = string.replace(s, d)

    if len(string) <= 3:
        yield string
        return
    for w in re.split(r"([A-Z\d][a-z-]*)", string):
        w = w.strip(" -")
        if not w or w in ["and", "for"]:
            continue
        yield w


def _filter_words(w: list[str]) -> list[str]:
    if w[-1].lower() in ["symbols"]:
        w = w[:-1]
    return [*pt.filtere(w)]


def _renew_abbrs():
    abbrs = dict()
    for ub in sorted(ucblk._BLOCKS, key=lambda a: len(a.name)):
        name_orig = ub.name
        name, suffix = _extract_suffix(name_orig)
        words = _filter_words([*_break_to_words(name)])

        if len(suffix) > 1:
            raise RuntimeError(
                f"Ruleset should provide the resulting "
                f"abbrs with max. 1-char suffix: {suffix!r} for {abbr}"
            )

        # wnum = len(words)
        # is_cjk = "CJK" in name_orig
        attempt = 0
        conflicts = []

        while True:
            base = ""
            word_buf = copy.copy(words)

            ####################################################
            #                                                  #
            #  dynamic implementation: 2-4 variadic lengths    #
            #  hard capped with MAX_LEN (currently 4)          #
            #                                                  #
            # ------------------------------------------------ #
            #                                                  #
            #  abbr_len =                                      #
            #    (word_num + 1 if CJK)     #   ≥ 1, cap at 3   #
            #    + (2, if only one word)   # [0-2]             #
            #    + attempt_number          # [0-2], usually 0  #
            #                                                  #
            #       word num | 1   2   3   4  ..               #
            #  --------------|-------------------              #
            #       abbr_len | 3   2   3   3  ..               #
            #   CJK abbr_len | 4   3   3   3  ..               #
            #                                                  #
            ####################################################
            #                                                  #
            #  from_words =  min(3 + (0, 1)[is_cjk], wnum)     #
            #  if_one_word = (0, 2)[wnum == 1]                 #
            #                                                  #
            #  opt_len = from_words + if_one_word + attempt    #
            #                                                  #
            ####################################################

            ####################################################
            #                                                  #
            #  fixed implementation: 3 characters as a base    #
            #                                                  #
            # ------------------------------------------------ #

            opt_len = 3 + max(0, attempt - 1)

            if attempt == 1:
                # try to compose an unique abbr
                # from consonants only, as a last resort
                word_buf = [*map(lambda w: re.sub(r"(?i)(?<=.)[aeiou]+", "", w), word_buf)]
            #
            ####################################################

            while len(base) < opt_len and len(word_buf) > 0:
                capitals_left = len(word_buf)
                moved = 0
                word = word_buf.pop(0)
                while (moved == 0 or opt_len - len(base) >= capitals_left) and word:
                    moved += 1
                    base += word[0]
                    word = word[1:]

            abbr = base + suffix
            if abbr in abbrs.keys():
                conflicts.append(abbrs.get(abbr))
                attempt += 1
                if attempt > 2:
                    raise RuntimeError(f"Could not pick a suitable abbr for: {ub!r} ({abbr})")
                continue

            if len(abbr) > MAX_LEN:
                conflicts_msg = (
                    ", conflicts: " + (", ".join(repr(c) for c in conflicts))
                    if conflicts
                    else " (no conflicts)"
                )

                raise RuntimeError(
                    f"Found a solution, but exceeded max length {MAX_LEN} for: "
                    f"{ub!r} ({abbr}){conflicts_msg}"
                )

            abbrs.update({abbr: ub})
            if ub.abbr != abbr:
                print(f"Updated {ub.abbr!r} -> {abbr!r} for {ub!r}", end="", file=sys.stderr)
                print(f" in {attempt} attempts" if attempt > 0 else "", file=sys.stderr)
                ub.abbr = abbr
            break


def _print_abbrs(file: TextIO):
    vardef = 'UnicodeBlock({start:>7s}, {end:>7s}, {abbr:>6s}, "{name}"),'
    for b in ucblk._BLOCKS:
        print(
            pt.pad(4)
            + vardef.format(
                start=f"0x{b.start:04X}",
                end=f"0x{b.end:04X}",
                abbr=repr(b.abbr),
                name=b.name,
            ),
            file=file,
        )


MAX_LEN = 4

if __name__ == "__main__":
    try:
        _renew_abbrs()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        exit(1)

    skipping = False
    src_file = str(importlib.resources.path("holms.db", "ucblk.py"))
    temp_dest_file = src_file + ".tmp"
    src_size = os.stat(src_file).st_size

    with open(src_file, "rt") as fsrc, open(temp_dest_file, "wt") as fdest:
        while line := fsrc.readline():
            if "@AUTOUPDATE_START" in line:
                skipping = True
                fdest.write(line)
                _print_abbrs(fdest)
            if "@AUTOUPDATE_END" in line:
                skipping = False
            if not skipping:
                fdest.write(line)
    target = shutil.move(temp_dest_file, src_file)
    print(f'Updated {target!r}: {src_size} -> {os.stat(target).st_size} bytes', file=sys.stderr)

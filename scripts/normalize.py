#!/usr/bin/env python3
"""Normalize narration text for round-trip comparison.

Lowercases, strips punctuation, and canonicalizes numbers so that spoken
number words ("nine hundred twenty four") and transcribed digits ("924")
compare equal. Reads stdin, writes one token per line to stdout.
"""

from __future__ import annotations

import re
import sys

UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}
SCALES = {"hundred": 100, "thousand": 1_000, "million": 1_000_000}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = text.replace("%", " percent ")
    text = re.sub(r"(\d),(\d)", r"\1\2", text)  # 10,000 -> 10000
    # 8.2 -> 8 2, and 59.26 -> 59 2 6: decimals are spoken digit by digit.
    text = re.sub(r"(\d)\.(\d+)", lambda m: m.group(1) + " " + " ".join(m.group(2)), text)
    tokens = re.split(r"[^a-z0-9]+", text)
    return [t for t in tokens if t]


def fold_numbers(tokens: list[str]) -> list[str]:
    out: list[str] = []
    current = 0
    total = 0
    in_number = False

    def flush() -> None:
        nonlocal current, total, in_number
        if in_number:
            out.append(str(total + current))
        current = 0
        total = 0
        in_number = False

    for token in tokens:
        if token == "point":
            # "sixty point seven" is "60 7", the same as the digit split of
            # "60.7" above; the word itself is dropped on both sides.
            flush()
        elif token == "zero":
            # "zero" is always its own digit: "zero two" is "0 2", and
            # "generation zero, thirty six" keeps the 0.
            flush()
            out.append("0")
        elif token in UNITS:
            # A unit may extend a number only after a tens or scale word,
            # so digit-by-digit speech like "one two" stays "1 2".
            if in_number and current % 10 != 0:
                flush()
            current += UNITS[token]
            in_number = True
        elif token in TENS:
            if in_number and current % 100 != 0:
                flush()
            current += TENS[token]
            in_number = True
        elif token.isdigit():
            # Transcribed digits start a number too, so "25 million" folds
            # the same way as "twenty five million".
            flush()
            current = int(token)
            in_number = True
        elif token == "hundred" and in_number:
            current *= 100
        elif token in SCALES and token != "hundred" and in_number:
            total += current * SCALES[token]
            current = 0
        else:
            flush()
            out.append(token)
    flush()
    return out


def main() -> None:
    tokens = fold_numbers(tokenize(sys.stdin.read()))
    sys.stdout.write("\n".join(tokens) + "\n")


if __name__ == "__main__":
    main()

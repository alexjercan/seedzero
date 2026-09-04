#!/usr/bin/env python3
"""Pi race: the Leibniz series against Ramanujan's 1914 series, with honest
term counters and digits that lock in on screen.

Leibniz: pi = 4 - 4/3 + 4/5 - 4/7 + ... Every partial sum is computed in
30-digit integer arithmetic (each term is floor(4 * 10^30 / (2k + 1)), so
the accumulated rounding is below N * 10^-30). A digit is "locked" at the
first term after which it never changes again in the run; the alternating
series bound |pi - S_N| < 4 / (2N + 3) then guarantees it stays locked past
the end of the run. Ramanujan: 1/pi = (2 sqrt 2 / 9801) * sum over k of
(4k)! (1103 + 26390k) / ((k!)^4 396^(4k)), evaluated exactly as fractions
with sqrt 2 to 30 digits; its partial sums decrease toward pi, so every
matching digit is final.

The reference digits of pi come from Machin's formula, computed here in
the same integer arithmetic to 40 digits.

usage: pirace.py [--measure-only]
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920

BG = (11, 14, 18)
TEAL = (92, 200, 165)
GOLD = (240, 176, 84)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
DIM = (70, 80, 94)
GRIDLINE = (40, 48, 58)

D = 30          # working digits after the point
SHOW = 16       # digits shown on screen (3 plus fifteen decimals)
DENSE = 3_000_000  # partial sums kept for every term up to here

# Layout (captions burned in by compose.sh sit at y 1344..1420).
L_LABEL_Y, L_DIGITS_Y, L_TERMS_Y, L_LOCK_Y = 205.0, 300.0, 400.0, 470.0
LINE_TITLE_Y, LINE_Y, LINE_LABEL_Y = 640.0, 730.0, 790.0
R_LABEL_Y, R_FORMULA_Y, R_DIGITS_Y, R_TERMS_Y, R_LOCK_Y = 920.0, 968.0, 1050.0, 1145.0, 1213.0
CHART_X0, CHART_X1, CHART_Y0, CHART_Y1 = 170, 1000, 1500, 1780
PAYOFF_Y = 1868.0


def machin_pi(digits: int) -> int:
    """pi * 10^digits, floor, by Machin's formula in integer arithmetic."""
    guard = 10
    one = 10 ** (digits + guard)

    def arctan_inv(x: int) -> int:
        total, power, k, sign = 0, one // x, 1, 1
        while power:
            total += sign * (power // k)
            power //= x * x
            k += 2
            sign = -sign
        return total

    pi = 4 * (4 * arctan_inv(5) - arctan_inv(239))
    return pi // 10 ** guard


def digits_str(value: int, digits: int) -> str:
    s = str(value).rjust(digits + 1, "0")
    return s[:-digits] + "." + s[-digits:]


class Prefix:
    """Longest prefix of pi's digits that a scaled value matches."""

    def __init__(self, pi_d: int, digits: int, max_len: int):
        self.pi = pi_d
        self.lo, self.hi = [0], [0]
        for i in range(1, max_len + 1):
            unit = 10 ** (digits - (i - 1))
            floor_i = pi_d // unit * unit
            self.lo.append(floor_i)
            self.hi.append(floor_i + unit)
        self.max_len = max_len

    def ok(self, value: int, i: int) -> bool:
        return self.lo[i] <= value < self.hi[i]

    def length(self, value: int, start: int = 0) -> int:
        i = min(max(start, 0), self.max_len)
        while i > 0 and not self.ok(value, i):
            i -= 1
        while i < self.max_len and self.ok(value, i + 1):
            i += 1
        return i


def leibniz(pi_d: int, n_max: int, prefix: Prefix) -> dict:
    four = 4 * 10 ** D
    scale = 10 ** (D - 18)
    sums18 = np.zeros(DENSE + 1, dtype=np.int64)
    first = {}
    last_wrong = {}
    prefix_at = {}
    s = 0
    length = 0
    report = set([1, 2, 3, 5, 10, 100, 1_000, 10_000, 100_000, 1_000_000])
    for k in range(n_max):
        term = four // (2 * k + 1)
        s = s + term if k % 2 == 0 else s - term
        n = k + 1
        if n <= DENSE:
            sums18[n] = s // scale
        length = prefix.length(s, length)
        for i in range(1, length + 1):
            if i not in first:
                first[i] = n
        for i in range(length + 1, prefix.max_len + 1):
            last_wrong[i] = n
        if n in report:
            prefix_at[n] = (length, digits_str(s // scale, 18))
    tail = Fraction(4, 2 * n_max + 3)
    locked = {}
    for i in range(1, prefix.max_len + 1):
        if i in last_wrong and last_wrong[i] < n_max:
            margin = min(pi_d - prefix.lo[i], prefix.hi[i] - pi_d)
            guaranteed = tail < Fraction(margin, 10 ** D)
            locked[i] = (last_wrong[i] + 1, guaranteed)
    return {"sums18": sums18, "first": first, "locked": locked, "prefix_at": prefix_at, "n_max": n_max, "final_len": length}


def ramanujan(pi_d: int, terms: int, prefix: Prefix) -> list[dict]:
    sqrt2 = math.isqrt(2 * 10 ** (2 * D))  # sqrt(2) * 10^D, floor
    total = Fraction(0)
    out = []
    for k in range(terms):
        term = Fraction(math.factorial(4 * k) * (1103 + 26390 * k), math.factorial(k) ** 4 * 396 ** (4 * k))
        total += term
        # pi = 9801 / (2 sqrt2 total)
        value = Fraction(9801 * 10 ** (2 * D)) / (2 * sqrt2 * total)
        v = int(value)  # floor of pi * 10^D
        out.append({"k": k, "terms": k + 1, "value": v, "len": prefix.length(v), "digits": digits_str(v, D)})
    return out


def measure(man: dict) -> dict:
    pi_d = machin_pi(D)
    pi40 = machin_pi(40)
    prefix = Prefix(pi_d, D, D - 2)
    print(f"reference pi by Machin's formula: {digits_str(pi40, 40)}")
    print(f"working digits {D}, shown {SHOW}")
    lb = leibniz(pi_d, man["leibniz_terms"], prefix)
    print(f"leibniz: {lb['n_max']:,} terms computed; prefix length at the last term {lb['final_len']}")
    for n, (length, s) in sorted(lb["prefix_at"].items()):
        err = abs(int(lb["sums18"][n]) - pi_d // 10 ** (D - 18)) / 1e18
        print(f"  term {n:>9,}: {s}  {length} correct digits, error {err:.6e} = {err * n:.6f} / {n:,}")
    for i in range(1, 12):
        f = lb["first"].get(i)
        lk = lb["locked"].get(i)
        if f is None:
            print(f"  {i:2d} digits: never reached in the run")
        elif lk is None:
            print(f"  {i:2d} digits: first at term {f:,}; not locked by the end of the run")
        else:
            print(f"  {i:2d} digits: first at term {f:,}; locked from term {lk[0]:,}"
                  f" ({'guaranteed' if lk[1] else 'NOT guaranteed'} by the tail bound 4/(2N+3) at N = {lb['n_max']:,})")
    rj = ramanujan(pi_d, man["ramanujan_terms"], prefix)
    print("ramanujan:")
    for r in rj:
        err = Fraction(r["value"] - pi_d, 10 ** D)
        print(f"  {r['terms']} term{'s' if r['terms'] > 1 else ''}: {r['digits'][:SHOW + 1]}...  {r['len']} correct digits"
              f" (error {float(err):.3e}, above pi: {err > 0})")
    assert all(r["value"] > pi_d for r in rj), "Ramanujan partial sums must stay above pi"
    assert all(a["value"] > b["value"] for a, b in zip(rj, rj[1:])), "and decrease"
    target = man["target_digits"]
    l_lock = lb["locked"][target]
    r_terms = next(r["terms"] for r in rj if r["len"] >= target)
    print(f"{target} digits: leibniz locks at term {l_lock[0]:,} (guaranteed {l_lock[1]}); ramanujan at {r_terms} term(s); "
          f"ratio {l_lock[0] / r_terms:,.0f} to 1")
    return {"pi_d": pi_d, "pi18": pi_d // 10 ** (D - 18), "leibniz": lb, "ramanujan": rj, "prefix": prefix}


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.font_digits = ImageFont.truetype(font, 74)
        self.font_terms = ImageFont.truetype(font, 56)
        self.keys = [(t, math.log(n)) for t, n in man["term_keys"]]
        assert man["term_keys"][-1][1] <= DENSE
        self.lock_term = {i: v[0] for i, v in meas["leibniz"]["locked"].items()}
        # Leibniz error curve, log-spaced samples from the stored partial sums.
        sums = meas["leibniz"]["sums18"]
        ns = np.unique(np.round(np.logspace(0, math.log10(man["term_keys"][-1][1]), 400)).astype(int))
        self.err_curve = [(int(k), max(abs(int(sums[k]) - meas["pi18"]) / 1e18, 1e-18)) for k in ns if 1 <= k <= man["term_keys"][-1][1]]

    def leibniz_terms(self, t: float) -> int:
        keys = self.keys
        if t <= keys[0][0]:
            return int(round(math.exp(keys[0][1])))
        for (t0, l0), (t1, l1) in zip(keys, keys[1:]):
            if t <= t1:
                u = (t - t0) / (t1 - t0)
                return int(round(math.exp(l0 + (l1 - l0) * u)))
        return int(round(math.exp(keys[-1][1])))

    def ramanujan_terms(self, t: float) -> int:
        n = 0
        for i, tk in enumerate(self.man["ramanujan_keys"]):
            if t >= tk:
                n = i + 1
        return n

    def draw_digits(self, d, y: float, s18: str, locked: int, col_locked, show_len: int = SHOW):
        """Draw 3.xxxxxxxxxxxxxx digit by digit: locked digits bright, the
        rest dim. s18 is the 18-decimal string."""
        text = s18[: show_len + 1]  # "3." plus decimals to SHOW digits
        widths = [d.textlength(c, font=self.font_digits) for c in text]
        x = (W - sum(widths)) / 2
        digit_i = 0
        for c, w in zip(text, widths):
            if c == ".":
                col = TEXT
            else:
                digit_i += 1
                col = col_locked if digit_i <= locked else DIM
            d.text((x, y), c, font=self.font_digits, fill=col, anchor="lm")
            x += w

    def frame_at(self, f: int) -> np.ndarray:
        man, meas = self.man, self.meas
        t = f / self.fps
        img = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(img)
        started = t >= man["start_t"]
        # Leibniz lane.
        n = self.leibniz_terms(t) if started else 0
        if n > 0:
            s18 = int(meas["leibniz"]["sums18"][n])
            l_str = digits_str(s18, 18)
            l_locked = max([0] + [i for i, lk in self.lock_term.items() if lk <= n and i <= SHOW])
            err = abs(s18 - meas["pi18"]) / 1e18
        else:
            l_str, l_locked, err = "0." + "0" * 18, 0, 1.0
        d.text((60, L_LABEL_Y), "Leibniz", font=self.font, fill=TEXT, anchor="lm")
        d.text((1020, L_LABEL_Y), "pi = 4 - 4/3 + 4/5 - 4/7 + ...", font=self.font_small, fill=MUTED, anchor="rm")
        self.draw_digits(d, L_DIGITS_Y, l_str, l_locked, TEAL)
        d.text((60, L_TERMS_Y), f"{n:,} term{'' if n == 1 else 's'}", font=self.font_terms, fill=TEAL if n else DIM, anchor="lm")
        d.text((1020, L_LOCK_Y), f"{l_locked} of {SHOW} digits locked", font=self.font, fill=TEAL if l_locked else MUTED, anchor="rm")
        if n > 0:
            d.text((60, L_LOCK_Y), "off by " + f"{err:.1e}".replace("e-0", "e-"), font=self.font_small, fill=MUTED, anchor="lm")
        # Ramanujan lane.
        rn = self.ramanujan_terms(t) if started else 0
        rj = meas["ramanujan"]
        if rn > 0:
            r = rj[rn - 1]
            r_str = digits_str(r["value"] // 10 ** (D - 18), 18)
            r_locked = min(r["len"], SHOW)
            r_err = abs(r["value"] - meas["pi_d"]) / 10 ** D
        else:
            r_str, r_locked, r_err = "0." + "0" * 18, 0, 1.0
        d.text((60, R_LABEL_Y), "Ramanujan", font=self.font, fill=TEXT, anchor="lm")
        d.text((1020, R_LABEL_Y), "1/pi = (2 sqrt 2 / 9801) x sum over k of", font=self.font_small, fill=MUTED, anchor="rm")
        d.text((1020, R_FORMULA_Y), "(4k)! (1103 + 26390k) / (k!)^4 396^4k", font=self.font_small, fill=MUTED, anchor="rm")
        self.draw_digits(d, R_DIGITS_Y, r_str, r_locked, GOLD)
        d.text((60, R_TERMS_Y), f"{rn:,} term{'s' if rn != 1 else ''}", font=self.font_terms, fill=GOLD if rn else DIM, anchor="lm")
        done = rn >= len(man["ramanujan_keys"])
        d.text((1020, R_LOCK_Y), f"{r_locked} of {SHOW} digits locked" + ("  |  done" if done else ""),
               font=self.font, fill=GOLD if r_locked else MUTED, anchor="rm")
        if rn > 0:
            d.text((60, R_LOCK_Y), "off by " + f"{r_err:.1e}".replace("e-0", "e-"), font=self.font_small, fill=MUTED, anchor="lm")
        # Number line zoomed on pi: the window follows the Leibniz error.
        half = max(4.0 * err, 4e-15) if n > 0 else 1.0
        pi_f = meas["pi18"] / 1e18
        x0, x1 = 120, 960
        cx = (x0 + x1) / 2

        def x_of(v: float) -> float:
            return min(max(cx + (v - pi_f) / half * (x1 - x0) / 2, x0 - 20), x1 + 20)

        window = f"{half:.3f}" if half >= 1e-3 else f"{half:.1e}".replace("e-0", "e-")
        d.text((W / 2, LINE_TITLE_Y), f"zoom on pi: window plus or minus {window}", font=self.font_small, fill=MUTED, anchor="mm")
        d.line((x0, LINE_Y, x1, LINE_Y), fill=DIM, width=3)
        d.line((cx, LINE_Y - 26, cx, LINE_Y + 26), fill=TEXT, width=3)
        d.text((cx, LINE_LABEL_Y), "pi", font=self.font_small, fill=TEXT, anchor="mm")
        dec = max(2, min(16, int(-math.log10(half)) + 1))
        d.text((x0, LINE_LABEL_Y), f"{pi_f - half:.{dec}f}", font=self.font_tiny, fill=MUTED, anchor="lm")
        d.text((x1, LINE_LABEL_Y), f"{pi_f + half:.{dec}f}", font=self.font_tiny, fill=MUTED, anchor="rm")
        if n > 0:
            xv = x_of(s18 / 1e18)
            d.ellipse((xv - 12, LINE_Y - 12, xv + 12, LINE_Y + 12), fill=TEAL)
        if rn > 0:
            xv = x_of(rj[rn - 1]["value"] / 10 ** D)
            d.ellipse((xv - 9, LINE_Y - 9, xv + 9, LINE_Y + 9), fill=GOLD)
        # Chart: error against terms, both axes logarithmic.
        d.rectangle((CHART_X0, CHART_Y0, CHART_X1, CHART_Y1), outline=GRIDLINE, width=2)
        d.text((CHART_X0, CHART_Y0 - 28), "error against terms", font=self.font_small, fill=MUTED, anchor="lm")
        n_hi = man["term_keys"][-1][1]

        def cx_of(nn: int) -> float:
            return CHART_X0 + (CHART_X1 - CHART_X0) * math.log10(max(nn, 1)) / math.log10(n_hi)

        def cy_of(e: float) -> float:
            lo, hi = -16.0, 1.0
            v = min(max(math.log10(e), lo), hi)
            return CHART_Y1 - (CHART_Y1 - CHART_Y0) * (v - lo) / (hi - lo)

        for e, label in ((1e-1, "0.1"), (1e-4, "1e-4"), (1e-7, "1e-7"), (1e-10, "1e-10"), (1e-13, "1e-13")):
            y = cy_of(e)
            d.line((CHART_X0, y, CHART_X1, y), fill=GRIDLINE, width=1)
            d.text((CHART_X0 - 12, y), label, font=self.font_tiny, fill=MUTED, anchor="rm")
        for nn, label in ((1, "1"), (100, "100"), (10_000, "10,000"), (1_000_000, "1,000,000")):
            if nn <= n_hi:
                d.text((cx_of(nn), CHART_Y1 + 24), label, font=self.font_tiny, fill=MUTED, anchor="mm")
        pts = [(cx_of(nn), cy_of(e)) for nn, e in self.err_curve if nn <= n]
        if n > 0:
            pts.append((cx_of(n), cy_of(max(err, 1e-18))))
        if len(pts) > 1:
            d.line(pts, fill=TEAL, width=4)
        if pts:
            d.ellipse((pts[-1][0] - 7, pts[-1][1] - 7, pts[-1][0] + 7, pts[-1][1] + 7), fill=TEAL)
        for r in rj[:rn]:
            e = abs(r["value"] - meas["pi_d"]) / 10 ** D
            x, y = cx_of(r["terms"]), cy_of(max(e, 1e-18))
            d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=GOLD)
        if t >= man["payoff_t"]:
            alpha = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(GOLD))
            d.text((W / 2, PAYOFF_Y), man["payoff_text"], font=self.font, fill=shade, anchor="mm")
        return np.asarray(img)

    def render(self, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(self.fps), "-i", "-",
             "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-pix_fmt", "yuv420p", str(out_path)],
            stdin=subprocess.PIPE,
        )
        assert proc.stdin is not None
        for f in range(total):
            proc.stdin.write(self.frame_at(f).tobytes())
            if f % 300 == 0:
                print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


def main() -> None:
    man = json.loads((ROOT / "projects/pirace/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/pirace/footage.mp4")


if __name__ == "__main__":
    main()

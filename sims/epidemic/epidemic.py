#!/usr/bin/env python3
"""Epidemic threshold: the same town, the same virus, the same ten first
cases, and one knob: how many people a sick person meets each day.

Model: a town of grid x grid people who stay where they live. Each day
every sick person meets `contacts` people drawn at random from the block
of neighbours within `reach` houses (Chebyshev distance), and passes the
virus to each susceptible contact with probability p_transmit. A person
is sick and contagious for days_sick days, then recovers for good (SIR).
Contacts that fall outside the town are dropped. One seeded stream of
random numbers drives each run; the two panels use the same seed and the
same ten first cases and differ only in the contact count.

Measured and printed for each panel: the realised reproduction number
(mean secondary infections per case) over the first 50, 100 and 200 cases
and over every case, the day the outbreak ends, the peak number of sick
people, and the final case count. A scan over contact counts and many
seeds shows where the threshold sits, so the narration can say how
typical the two seeded runs are.

usage: epidemic.py [--measure-only] [--scan]
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920

BG = (11, 14, 18)
SUSCEPTIBLE = (34, 42, 53)
SICK = (240, 92, 84)
FRESH = (255, 204, 150)
RECOVERED = (84, 168, 140)
TEAL = (92, 200, 165)
GOLD = (240, 176, 84)
RED = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
GRIDLINE = (40, 48, 58)

PANEL_H = 700          # each town panel is at most 700 px tall
TOP_LABEL_Y, TOP_GRID_Y0 = 150.0, 180
BOT_LABEL_Y, BOT_GRID_Y0 = 1055.0, 1085
READ_DY = 25.0         # readout line sits this far under a panel
PAYOFF_Y = 1868.0


def run(man: dict, contacts: int, seed: int, record: bool) -> dict:
    """Run one outbreak to its end (or max_days). Returns the daily
    history (state grid per day when record is set) and the measurements."""
    rng = np.random.RandomState(seed)
    g = man["grid"]
    n = g * g
    reach = man["reach"]
    p = man["p_transmit"]
    d_sick = man["days_sick"]
    # 0 susceptible, 1 sick, 2 recovered. days_left counts the sick days.
    state = np.zeros(n, dtype=np.int8)
    days_left = np.zeros(n, dtype=np.int16)
    infector = np.full(n, -1, dtype=np.int32)
    order = np.full(n, -1, dtype=np.int32)  # case index in order of infection
    secondary = np.zeros(n, dtype=np.int32)
    # The first cases are ten houses drawn from the seeded stream, so both
    # panels start from exactly the same people (the stream is consumed
    # identically up to this point).
    first_idx = np.sort(rng.choice(n, size=man["initial_cases"], replace=False))
    state[first_idx] = 1
    days_left[first_idx] = d_sick
    order[first_idx] = np.arange(len(first_idx))
    cases = len(first_idx)
    # Neighbour offsets within reach, excluding self.
    offs = np.array([(dy, dx) for dy in range(-reach, reach + 1) for dx in range(-reach, reach + 1) if (dy, dx) != (0, 0)])
    history = [state.copy()] if record else None
    sick_curve = [int((state == 1).sum())]
    cases_curve = [cases]
    day = 0
    while day < man["max_days"]:
        sick = np.nonzero(state == 1)[0]
        if len(sick) == 0:
            break
        day += 1
        # Every sick person meets `contacts` neighbours today.
        k = rng.randint(len(offs), size=(len(sick), contacts))
        sy = (sick // g)[:, None] + offs[k, 0]
        sx = (sick % g)[:, None] + offs[k, 1]
        src = np.repeat(sick, contacts)
        sy, sx = sy.ravel(), sx.ravel()
        ok = (sy >= 0) & (sy < g) & (sx >= 0) & (sx < g)
        tgt = sy * g + sx
        u = rng.random_sample(len(tgt))
        hit = ok & (u < p)
        tgt, src = tgt[hit], src[hit]
        # Only susceptible targets catch it; the first hit in stream order wins.
        newly = []
        for t_, s_ in zip(tgt.tolist(), src.tolist()):
            if state[t_] == 0 and infector[t_] == -1:
                infector[t_] = s_
                newly.append(t_)
        # Sick days pass; recoveries happen before the new cases start.
        days_left[sick] -= 1
        recovered = sick[days_left[sick] <= 0]
        state[recovered] = 2
        if newly:
            newly = np.array(newly)
            state[newly] = 1
            days_left[newly] = d_sick
            order[newly] = np.arange(cases, cases + len(newly))
            cases += len(newly)
            np.add.at(secondary, infector[newly], 1)
        if record:
            history.append(state.copy())
        sick_curve.append(int((state == 1).sum()))
        cases_curve.append(cases)
    ended = int((state == 1).sum()) == 0
    # Realised reproduction number over the first m cases (all recovered by the end).
    case_ids = np.nonzero(order >= 0)[0]
    by_order = case_ids[np.argsort(order[case_ids])]
    r_first = {}
    for m in (50, 100, 200):
        if len(by_order) >= m:
            r_first[m] = float(secondary[by_order[:m]].mean())
    r_all = float(secondary[by_order].mean()) if ended else float("nan")
    return {
        "contacts": contacts, "seed": seed, "cases": cases, "days": day, "ended": ended,
        "peak_sick": int(max(sick_curve)), "peak_day": int(np.argmax(sick_curve)),
        "r_first": r_first, "r_all": r_all, "history": history,
        "sick_curve": sick_curve, "cases_curve": cases_curve, "first": first_idx,
    }


def scan(man: dict) -> None:
    print(f"scan: {man['scan_seeds']} seeds per contact count, town {man['grid']}x{man['grid']}, "
          f"{man['initial_cases']} first cases, p {man['p_transmit']}, {man['days_sick']} sick days, reach {man['reach']}")
    print("  contacts  nominal R  mean R(first 100)  took off (>1,000 cases)  median cases  mean cases")
    for k in range(6, 17):
        res = [run(man, k, s, False) for s in range(man["scan_seeds"])]
        cases = np.array([r["cases"] for r in res])
        days = np.array([r["days"] for r in res])
        r100 = np.array([r["r_first"].get(100, np.nan) for r in res])
        took = float((cases > 1000).mean())
        print(f"  {k:8d}  {k * man['p_transmit'] * man['days_sick']:9.2f}  {np.nanmean(r100) if np.isfinite(r100).any() else float('nan'):17.3f}  "
              f"{100 * took:22.1f}%  {int(np.median(cases)):12d}  {cases.mean():10.1f}  days median {int(np.median(days))} max {days.max()}")


def measure(man: dict) -> dict:
    g = man["grid"]
    print(f"town {g}x{g} = {g * g:,} people at seed {man['seed']}, {man['initial_cases']} first cases at seeded houses, "
          f"each contact passes the virus with probability {man['p_transmit']}, sick for {man['days_sick']} days, "
          f"contacts drawn from the {2 * man['reach'] + 1}x{2 * man['reach'] + 1} block of neighbours")
    out = {}
    for name, k in (("below", man["contacts_below"]), ("above", man["contacts_above"])):
        r = run(man, k, man["seed"], True)
        out[name] = r
        rf = ", ".join(f"first {m}: {v:.2f}" for m, v in r["r_first"].items())
        print(f"{name}: {k} contacts a day (nominal R0 = {k * man['p_transmit'] * man['days_sick']:.2f})")
        print(f"  realised R: {rf}; over all {r['cases']:,} cases: {r['r_all']:.3f}")
        print(f"  outbreak {'ended' if r['ended'] else 'STILL RUNNING'} on day {r['days']}; peak {r['peak_sick']:,} sick on day {r['peak_day']}; "
              f"final count {r['cases']:,} cases = {100 * r['cases'] / (g * g):.1f}% of the town")
        for d in (10, 20, 30, 40, 60, 80, 100, 120, 150, 200):
            if d < len(r["cases_curve"]):
                print(f"    day {d}: {r['cases_curve'][d]:,} cases, {r['sick_curve'][d]:,} sick")
    same_first = np.array_equal(out["below"]["first"], out["above"]["first"])
    print(f"same ten first cases in both panels: {same_first}")
    print(f"ratio of final counts: {out['above']['cases'] / out['below']['cases']:.1f}x")
    # How typical are the two seeded runs?
    for name, k in (("below", man["contacts_below"]), ("above", man["contacts_above"])):
        res = [run(man, k, s, False) for s in range(man["scan_seeds"])]
        cases = np.array([r["cases"] for r in res])
        took = float((cases > 1000).mean())
        print(f"{name} over {man['scan_seeds']} seeds: took off (>1,000 cases) in {100 * took:.1f}%; "
              f"cases min {cases.min():,} median {int(np.median(cases)):,} max {cases.max():,}; "
              f"seed {man['seed']} ranks at percentile {100 * (cases < out[name]['cases']).mean():.0f}")
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_small = ImageFont.truetype(font, 32)
        self.font_tiny = ImageFont.truetype(font, 26)
        self.g = man["grid"]
        self.cell = max(1, PANEL_H // self.g)
        self.x0 = (W - self.g * self.cell) // 2
        self.lut = np.array([SUSCEPTIBLE, SICK, RECOVERED, FRESH], dtype=np.uint8)

    def day_at(self, scene_t: float) -> float:
        return max(0.0, (scene_t - self.man["start_t"]) * self.man["days_per_second"])

    def panel(self, name: str, day_f: float) -> tuple[np.ndarray, int, int, int]:
        r = self.meas[name]
        hist = r["history"]
        d = min(int(day_f), len(hist) - 1)
        st = hist[d].copy()
        if d > 0:
            fresh = (hist[d] == 1) & (hist[d - 1] == 0)
            st[fresh] = 3
        img = self.lut[st.reshape(self.g, self.g)]
        img = np.repeat(np.repeat(img, self.cell, 0), self.cell, 1)
        if self.cell >= 5:
            # one-pixel grout between houses; at 3 px a gap leaves 2 px dots
            # that vanish on a phone, so small cells stay solid
            img[self.cell - 1::self.cell, :] = BG
            img[:, self.cell - 1::self.cell] = BG
        return img, d, r["sick_curve"][d], r["cases_curve"][d]

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        scene_t = f / self.fps
        day_f = self.day_at(scene_t)
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        frame[:, :] = BG
        rows = []
        side = self.g * self.cell
        x0, x1 = self.x0, self.x0 + side
        for name, y0 in (("below", TOP_GRID_Y0), ("above", BOT_GRID_Y0)):
            img, d, sick, cases = self.panel(name, day_f)
            frame[y0:y0 + side, x0:x1] = img
            rows.append((d, sick, cases))
        pil = Image.fromarray(frame)
        dr = ImageDraw.Draw(pil)
        for (name, label_y, grid_y0, col, k), (d, sick, cases) in zip(
            (("below", TOP_LABEL_Y, TOP_GRID_Y0, TEAL, man["contacts_below"]),
             ("above", BOT_LABEL_Y, BOT_GRID_Y0, GOLD, man["contacts_above"])), rows):
            r = self.meas[name]
            read_y = grid_y0 + side + READ_DY
            dr.text((x0, label_y), f"{k} contacts a day", font=self.font, fill=col, anchor="lm")
            dr.text((x1, label_y), f"day {d}", font=self.font_small, fill=MUTED, anchor="rm")
            ended = r["ended"] and d >= r["days"]
            status = "over" if ended else f"sick now {sick:,}"
            dr.text((x0, read_y), status, font=self.font_small, fill=RED if not ended else MUTED, anchor="lm")
            dr.text((x1, read_y), f"{cases:,} cases", font=self.font_small, fill=col, anchor="rm")
        if scene_t >= man["payoff_t"]:
            alpha = min(1.0, (scene_t - man["payoff_t"]) / man["payoff_hold"])
            shade = tuple(int(c * alpha + BG[i] * (1 - alpha)) for i, c in enumerate(GOLD))
            dr.text((W / 2, PAYOFF_Y), man["payoff_text"], font=self.font, fill=shade, anchor="mm")
        return np.asarray(pil)

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
    man = json.loads((ROOT / "projects/epidemic/manifest.json").read_text())
    for i, a in enumerate(sys.argv):
        if a == "--reach":
            man["reach"] = int(sys.argv[i + 1])
    if "--scan" in sys.argv:
        scan(man)
        return
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    Renderer(man, meas).render(ROOT / "media/epidemic/footage.mp4")


if __name__ == "__main__":
    main()

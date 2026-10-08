#!/usr/bin/env python3
"""Books past the table edge: can a stack of books hold the top one completely past the table?

Two bands on the same clock, the same table drawn the same way at the same
scale, side view: five identical uniform books, L long and t thick, go on
one at a time from the bottom up at a table edge. The bottom book's front
end sits d1 past the table edge and each next book sits d_i past the front
end of the book under it. Statics, exact in fractions (the book's weight
cancels): the top j books hold on the book under them, or the whole stack
holds on the table, while their combined centre of mass is at or behind
that support's front end; the margin is the support end minus the
sub-stack's centre (cm), and the stack falls at the first negative margin.
Top band, the "equal" case: every step d = 4.44 cm. Bottom band, the
"shrinking" case: steps 1.9, 2.4, 3.2, 4.9, 9.8 cm from the bottom up, each
just under L/10, L/8, L/6, L/4, L/2 (the harmonic steps). Equal steps d
topple a stack of n books once d > L / (n + 1) (the whole stack's centre is
L/2 - d (n + 1) / 2 behind the edge); the most a stack of n books can reach
is half the harmonic sum, (L / 2) H_n.

The fall of the equal stack is a drawing model: the four books as one rigid
body (centre of mass 1.10 cm past the edge, 6.0 cm up), pivoting about the
table's corner while the corner's grip holds (mu chosen for the drawing),
then sliding along the bottom book's face over the corner with kinetic
friction mu, then flying free once the corner's push reaches zero or the
face runs out; integrated by RK4 at steps_per_second with the events located
by bisection inside the step. The corner touches the book's flat bottom
face, so its push is normal to that face; the brief's research run split
the corner force into table-frame horizontal and vertical parts instead,
and that criterion is printed too as the check against the brief. The fall
is drawn at 1/slow speed. Each book slides in from the left along the top
of the stack over slide_s seconds of video and lands at land_s seconds of
the cycle; the run repeats every cycle_s seconds with a crossfade back to
the empty table; the cycle divides the scene length, so the scene is
exactly periodic and the last frame equals the first. Deterministic, no
seed.

Measured and printed: every sub-stack margin after each book goes on, both
stacks' top ends, the exact limits for 4 and 5 books, the equal-step rule,
the variants for the description, the fall of the equal stack (both
criteria, both grips), the brief's checks with an assert on each, the
schedule in video time, the on-screen text widths and the layout
clearances.

usage: bookstack.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import json
import math
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as Fr
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
NAME = "bookstack"
W, H = 1080, 1920

BG = (11, 14, 18)
TEAL = (92, 200, 165)
GOLD = (240, 176, 84)
CORAL = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
WHITE = (236, 240, 244)
DECK_A = (30, 36, 46)
DECK_B = (42, 50, 62)
RIM = (96, 108, 126)
BOOKS = ((168, 86, 74), (72, 112, 160), (184, 148, 82), (86, 140, 104), (138, 98, 152))

# Layout: overlay at y 96..130 (captions.py), three title rows at y 186/244/302 for the first
# seconds, then the legend at y 236 and the clock row at y 290; two bands stacked, the equal
# stack in y 330..880 and the shrinking stack in y 880..1430, each drawn at 2x in its own layer
# (so the falling books are clipped at their band); each band has its label row 40 px under
# the band top and its readout rows at 84 and 120 (left column from x 40, right column to
# x 1040); the table top 470 px under the band top with its edge at x 470, a 20 px slab and one
# leg; the books stack upward from the table top (five books reach 170 px under the band top);
# a dashed line up the table edge from the table top to just under the readout rows; the gold
# centre-of-mass triangle on the table top under the stack; the gold event row under the slab
# (y 520 under the band top); captions at caption_y 0.75 (y 1440..1530); the card from y 1572
# at a 48 px pitch.
LEGEND_Y, CLOCK_Y = 236, 290
TITLE_YS = (186, 244, 302)
SS = 2
PAYOFF_Y, PAYOFF_PITCH = 1572.0, 48
PANELS = ("equal", "shrinking")
BAND_Y = {"equal": 330, "shrinking": 880}
BAND_H = 550
LABEL_DY, SUB_DY, FIX_DY = 40, 84, 120
ROWS_BOTTOM = FIX_DY + 16
ROW_X0, ROW_X1 = 40, 1040
SLAB_PX = 20
LEG_X, LEG_W = 60, 18
EVENT_DY, EVENT_X = 520, 100
DASH_TOP = ROWS_BOTTOM + 10
TRI_W, TRI_H = 20, 17
DIM_DY = 12
COLOUR = {"equal": CORAL, "shrinking": TEAL}
STAND, PIVOT, SLIDE, FLY = "stand", "pivot", "slide", "fly"


def blend(col, a: float, base=BG) -> tuple:
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def fs(x: Fr, nd: int = 3) -> str:
    return f"{float(x):.{nd}f}"


# --- statics (exact) ----------------------------------------------------------
def ends_of(steps: list[Fr]) -> list[Fr]:
    out, c = [], Fr(0)
    for d in steps:
        c += d
        out.append(c)
    return out


def margins(steps: list[Fr], L: Fr, j: int) -> list[Fr]:
    """With the bottom j books placed: the margin of the top (j - k) books on support k (0 the
    table, k the k-th book from the bottom), support end minus the sub-stack's centre, in cm."""
    ends = ends_of(steps[:j])
    centres = [e - L / 2 for e in ends]
    out = []
    for k in range(j):
        sup = Fr(0) if k == 0 else ends[k - 1]
        sub = centres[k:]
        out.append(sup - sum(sub) / len(sub))
    return out


def stack_report(steps: list[Fr], L: Fr) -> dict:
    n = len(steps)
    rows, fall_at = [], None
    for j in range(1, n + 1):
        ms = margins(steps, L, j)
        worst = min(ms)
        kk = ms.index(worst)
        com = sum(e - L / 2 for e in ends_of(steps[:j])) / j    # the whole stack's centre past the edge
        rows.append({"j": j, "ms": ms, "worst": worst, "at": kk, "com": com, "top": ends_of(steps[:j])[-1]})
        if worst < 0 and fall_at is None:
            fall_at = j
    return {"rows": rows, "fall_at": fall_at, "top": ends_of(steps)[-1], "back": ends_of(steps)[-1] - L}


def where(k: int) -> str:
    return "the table" if k == 0 else f"book {k}"


# --- the fall (drawing model) --------------------------------------------------------
def rot(th: float, u: float, v: float) -> tuple[float, float]:
    """Rotate (u, v) clockwise by th (y up)."""
    c, s = math.cos(th), math.sin(th)
    return u * c + v * s, -u * s + v * c


class Body:
    """The fallen books as one rigid body; lengths in metres, y up, origin at the table corner,
    body coordinates (u, v) with the origin at the corner when upright; the mass cancels (m = 1
    per book)."""

    def __init__(self, steps_m: list[float], L: float, t: float, g: float):
        ends = list(np.cumsum(steps_m))
        self.n = len(steps_m)
        self.boxes = [(e - L, e, k * t, (k + 1) * t) for k, e in enumerate(ends)]
        self.M = float(self.n)
        self.xc = sum(e - L / 2 for e in ends) / self.n
        self.yc = sum((k + 0.5) * t for k in range(self.n)) / self.n
        self.I = sum((L * L + t * t) / 12.0 + (e - L / 2 - self.xc) ** 2 + ((k + 0.5) * t - self.yc) ** 2
                     for k, e in enumerate(ends))
        self.Ie = self.I + self.M * (self.xc ** 2 + self.yc ** 2)
        self.g = g
        self.u_back, self.u_front = self.boxes[0][0], self.boxes[0][1]

    # Pivot about the corner: state (th, w).
    def pivot_acc(self, th: float) -> float:
        cx, _ = rot(th, self.xc, self.yc)
        return self.M * self.g * cx / self.Ie

    def pivot_force(self, th: float, w: float) -> tuple[float, float, float, float]:
        """(N, F) normal and along the bottom face, and (Rx, Ry) in the table frame, per the
        stack's weight."""
        cx, cy = rot(th, self.xc, self.yc)
        al = self.pivot_acc(th)
        ax, ay = al * cy - w * w * cx, -al * cx - w * w * cy
        Rx, Ry = self.M * ax, self.M * (ay + self.g)
        n = (math.sin(th), math.cos(th))
        tt = (math.cos(th), -math.sin(th))
        Wt = self.M * self.g
        return (Rx * n[0] + Ry * n[1]) / Wt, (Rx * tt[0] + Ry * tt[1]) / Wt, Rx / Wt, Ry / Wt

    # Slide over the corner along the bottom face: state (p, th, pd, w), C = rot(th, p, yc).
    def slide_rhs(self, y: tuple, mu: float) -> tuple[tuple, float]:
        p, th, pd, w = y
        c, s = math.cos(th), math.sin(th)
        n = (s, c)
        tt = (c, -s)
        Cx, Cy = rot(th, p, self.yc)
        J = (Cy, -Cx)
        Cdx, Cdy = tt[0] * pd + J[0] * w, tt[1] * pd + J[1] * w
        h = (-n[0] * w * pd + Cdy * w, -n[1] * w * pd - Cdx * w)
        e = (n[0] - mu * tt[0], n[1] - mu * tt[1])        # the contact force per unit N (friction against pd > 0)
        M, I = self.M, self.I
        A = np.array([[M * tt[0], M * J[0], -e[0]],
                      [M * tt[1], M * J[1], -e[1]],
                      [0.0, I, -(Cx * e[1] - Cy * e[0])]])
        b = np.array([-M * h[0], -M * self.g - M * h[1], 0.0])
        pdd, al, N = np.linalg.solve(A, b)
        return (pd, w, float(pdd), float(al)), float(N) / (M * self.g)

    def corners(self, C: tuple, th: float) -> list[list[tuple[float, float]]]:
        out = []
        for (u0, u1, v0, v1) in self.boxes:
            box = []
            for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
                dx, dy = rot(th, u - self.xc, v - self.yc)
                box.append((C[0] + dx, C[1] + dy))
            out.append(box)
        return out


def rk4(f, y: tuple, h: float) -> tuple:
    k1 = f(y)
    k2 = f(tuple(a + 0.5 * h * b for a, b in zip(y, k1)))
    k3 = f(tuple(a + 0.5 * h * b for a, b in zip(y, k2)))
    k4 = f(tuple(a + h * b for a, b in zip(y, k3)))
    return tuple(a + h * (b1 + 2 * b2 + 2 * b3 + b4) / 6.0 for a, b1, b2, b3, b4 in zip(y, k1, k2, k3, k4))


def bisect_step(step, y, h, crossed) -> tuple[float, tuple]:
    lo, hi = 0.0, h
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if crossed(step(y, mid)):
            hi = mid
        else:
            lo = mid
    return hi, step(y, hi)


def pivot_run(body: Body, mu: float, dt: float, frame: str) -> dict:
    """RK4 on (th, w) from rest; stops when the corner's push reaches zero or its grip needed
    passes mu, in the face frame (normal to the bottom face) or the table frame (the brief)."""
    f = lambda y: (y[1], body.pivot_acc(y[0]))   # noqa: E731

    def bad(y: tuple) -> bool:
        N, F, Rx, Ry = body.pivot_force(*y)
        if frame == "table":
            N, F = Ry, Rx
        return N <= 0.0 or abs(F) > mu * N

    step = lambda y, h: rk4(f, y, h)   # noqa: E731
    y, t, ts, ys = (0.0, 0.0), 0.0, [0.0], [(0.0, 0.0)]
    while True:
        yn = step(y, dt)
        if bad(yn):
            hh, yn = bisect_step(step, y, dt, bad)
            t += hh
            ts.append(t)
            ys.append(yn)
            break
        y, t = yn, t + dt
        ts.append(t)
        ys.append(y)
    N, F, Rx, Ry = body.pivot_force(*yn)
    return {"t": np.array(ts), "th": np.array([a for a, _ in ys]), "w": np.array([b for _, b in ys]),
            "t_end": t, "th_end": yn[0], "w_end": yn[1], "N": N, "F": F, "Rx": Rx, "Ry": Ry}


def fall_run(body: Body, mu: float, dt: float) -> dict:
    """The drawn fall: the face-frame pivot, the slide along the bottom face, then free flight;
    a table of (t, phase, C, th) for the drawing."""
    piv = pivot_run(body, mu, dt, "face")
    p0 = body.xc
    y = (p0, piv["th_end"], 0.0, piv["w_end"])
    t = piv["t_end"]
    ts, Cs, ths = [], [], []
    for tt, th in zip(piv["t"], piv["th"]):
        ts.append(float(tt))
        Cs.append(rot(float(th), body.xc, body.yc))
        ths.append(float(th))
    f = lambda yy: body.slide_rhs(yy, mu)[0]   # noqa: E731
    step = lambda yy, h: rk4(f, yy, h)   # noqa: E731
    p_off = body.xc - body.u_back       # the corner reaches the bottom book's back end

    def gone(yy: tuple) -> bool:
        return body.slide_rhs(yy, mu)[1] <= 0.0 or yy[0] >= p_off

    t_slide0 = t
    min_pd = 0.0
    while True:
        yn = step(y, dt)
        if gone(yn):
            hh, yn = bisect_step(step, y, dt, gone)
            t += hh
            y = yn
            break
        y, t = yn, t + dt
        min_pd = min(min_pd, y[2])
        ts.append(t)
        Cs.append(rot(y[1], y[0], body.yc))
        ths.append(y[1])
    p, th, pd, w = y
    C = rot(th, p, body.yc)
    tt_ = (math.cos(th), -math.sin(th))
    J = (C[1], -C[0])
    V = (tt_[0] * pd + J[0] * w, tt_[1] * pd + J[1] * w)
    N_end = body.slide_rhs(y, mu)[1]
    why = "the corner's push reached zero" if N_end <= 1e-9 else "the corner reached the bottom book's back end"
    return {"piv": piv, "t_slide0": t_slide0, "t_fly0": t, "slide_dist": p - p0, "th_fly0": th, "w_fly": w,
            "C_fly0": C, "V_fly0": V, "why": why, "min_pd": min_pd,
            "t": np.array(ts), "C": np.array(Cs), "th": np.array(ths)}


def fall_state(fr: dict, g: float, rt: float) -> tuple[str, tuple, float]:
    """(phase, C, th) rt real seconds after the tip starts."""
    if rt <= 0.0:
        return STAND, fr["C"][0], 0.0
    if rt < fr["t_fly0"]:
        ts = fr["t"]
        i = int(np.searchsorted(ts, rt))
        i = max(1, min(i, len(ts) - 1))
        a = (rt - ts[i - 1]) / (ts[i] - ts[i - 1])
        C = tuple((1 - a) * c0 + a * c1 for c0, c1 in zip(fr["C"][i - 1], fr["C"][i]))
        th = (1 - a) * fr["th"][i - 1] + a * fr["th"][i]
        return (PIVOT if rt < fr["t_slide0"] else SLIDE), C, th
    d = rt - fr["t_fly0"]
    C0, V0 = fr["C_fly0"], fr["V_fly0"]
    return FLY, (C0[0] + V0[0] * d, C0[1] + V0[1] * d - 0.5 * g * d * d), fr["th_fly0"] + fr["w_fly"] * d


def point_in_box(q: tuple, box: list, tol: float) -> bool:
    """Is q inside the convex quad box by more than tol?"""
    for a, b in zip(box, box[1:] + box[:1]):
        ex, ey = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(ex, ey)
        cross = (ex * (q[1] - a[1]) - ey * (q[0] - a[0])) / ln
        if cross < tol:
            return False
    return True


def inside(q: tuple, box: list, tol: float) -> bool:
    return point_in_box(q, box, tol) or point_in_box(q, box[::-1], tol)


# --- measurement --------------------------------------------------------------
def measure(man: dict) -> dict:
    g = man["g"]
    L, T = Fr(man["book_cm"]), Fr(man["thick_cm"])
    nb = man["n_books"]
    steps = {m: [Fr(s) for s in man["steps_cm"][m]] for m in PANELS}
    assert all(len(steps[m]) == nb for m in PANELS)
    fps, P, D, F = man["fps"], man["cycle_s"], man["scene_duration"], man["reset_fade"]
    S = man["slow"]
    cycles = D / P
    assert abs(cycles - round(cycles)) < 1e-9, "the cycle must divide the scene length"
    for key in ("cycle_s", "first_cycle_at", "reset_fade", "slide_s"):
        assert abs(man[key] * fps - round(man[key] * fps)) < 1e-9, f"{key} must be a whole number of frames"
    ppm = man["px_per_m"]
    print(f"setup: side view, two bands on one clock, the same table drawn the same way at the same scale: {nb} "
          f"identical uniform books, L = {L} cm long and t = {T} cm thick (the weight cancels), placed one at a time "
          f"from the bottom up at a table edge; the bottom book's front end sits d1 past the table edge and each next "
          f"book sits d_i past the front end of the one below; a sub-stack (the top j books) holds on the book under "
          f"it, or the whole stack holds on the table, while its combined centre of mass is at or behind that "
          f"support's front end; margin = support end minus the sub-stack's centre (cm, exact fractions), the stack "
          f"falls at the first negative margin; top band equal steps {', '.join(str(s) for s in man['steps_cm']['equal'])} "
          f"cm, bottom band shrinking steps {', '.join(man['steps_cm']['shrinking'])} cm from the bottom up; g = {g:g} "
          f"m/s^2; drawn at {ppm:g} px per metre; deterministic, no seed")
    ev: dict = {"L": L, "T": T, "steps": steps, "rep": {}}
    for m in PANELS:
        rep = stack_report(steps[m], L)
        ev["rep"][m] = rep
        print(f"{m} steps ({', '.join(str(s) for s in steps[m])} cm):")
        for r in rep["rows"]:
            ms = "; ".join(f"on {where(k)} {'+' if x >= 0 else ''}{x} = {float(x):+.3f}" for k, x in enumerate(r["ms"]))
            state = "holds" if r["worst"] >= 0 else "FALLS"
            print(f"  after book {r['j']}: margins {ms}; worst {float(r['worst']):+.3f} cm at {where(r['at'])}, {state}; "
                  f"the whole stack's centre {float(-r['com']):.3f} cm {'behind' if r['com'] <= 0 else 'past'} the edge"
                  f"{'' if r['com'] <= 0 else ' (' + fs(r['com'], 2) + ' cm past)'}; top end {float(r['top']):.2f} cm out")
        print(f"  {m}: falls at book {rep['fall_at']}" if rep["fall_at"] else
              f"  {m}: every margin positive, holds; the top book's front end {float(rep['top']):.2f} cm out, its back "
              f"end {float(rep['back']):.2f} cm past the table edge ({'wholly past the table' if rep['back'] > 0 else 'over the table'})")
    # The exact limits.
    Hn = lambda n: sum(Fr(1, k) for k in range(1, n + 1))   # noqa: E731
    lim = {n: Hn(n) / 2 for n in range(1, 9)}
    ev["lim"] = lim
    print("limit (the harmonic stack, every margin zero): n books reach (L / 2) H_n: " + "; ".join(
        f"{n}: {lim[n]} of a book = {float(lim[n] * L):.3f} cm" for n in range(1, 9)))
    print(f"five books: steps L/10, L/8, L/6, L/4, L/2 = {', '.join(fs(L / (2 * k), 3) for k in (5, 4, 3, 2, 1))} cm reach "
          f"{lim[5]} of a book = {float(lim[5] * L):.3f} cm, the top book's back end {float(lim[5] * L - L):.3f} cm past "
          f"the edge; four books reach {lim[4]} = {float(lim[4] * L):.3f} cm, only {float(lim[4] * L - L):.3f} cm clear")
    # The equal-step rule.
    rule = {n: L / (n + 1) for n in range(1, 6)}
    ev["rule"] = rule
    print("equal steps d: the whole stack's centre sits L/2 - d (n + 1) / 2 behind the edge, so n books fall once d > "
          "L / (n + 1): " + "; ".join(f"n = {n}: {rule[n]} = {float(rule[n]):.2f} cm" for n in range(1, 6)))
    d_eq = steps["equal"][0]
    holds = max(n for n in range(1, 6) if d_eq <= rule[n])
    ev["holds_n"] = holds
    print(f"equal {d_eq} cm: holds {holds} books (limit {float(rule[holds]):.2f} cm) and not {holds + 1} (limit "
          f"{float(rule[holds + 1]):.2f} cm)")
    # Variants for the description.
    descr = []
    for lab, st in (("the shrinking steps upside down (9.8 cm at the bottom)", steps["shrinking"][::-1]),
                    ("the exact harmonic steps L/10 .. L/2", [L / (2 * k) for k in (5, 4, 3, 2, 1)]),
                    ("equal 4.00 cm steps", [Fr(4)] * 5),
                    ("equal 3.33 cm steps", [Fr("3.33")] * 5)):
        rp = stack_report(st, L)
        worst = ", ".join(f"{float(r['worst']):+.3f}" for r in rp["rows"])
        descr.append(f"{lab}: worst margins after each book {worst} cm; "
                     + (f"falls at book {rp['fall_at']}" if rp["fall_at"] else
                        f"holds, top end {float(rp['top']):.3f} cm out, back end {float(rp['back']):+.3f} cm"))
        ev.setdefault("variants", {})[lab] = rp
    print("for the description: " + "; ".join(descr))
    # The fall of the equal stack (drawing model).
    fa = ev["rep"]["equal"]["fall_at"]
    Lm, Tm = float(L) / 100.0, float(T) / 100.0
    body = Body([float(s) / 100.0 for s in steps["equal"][:fa]], Lm, Tm, g)
    dt = 1.0 / man["steps_per_second"]
    mu, mu2 = man["mu"], man["mu_alt"]
    tab = {m_: pivot_run(body, m_, dt, "table") for m_ in (mu, mu2)}
    face = {m_: pivot_run(body, m_, dt, "face") for m_ in (mu, mu2)}
    half = pivot_run(body, mu, 0.5 * dt, "face")
    fr = fall_run(body, mu, dt)
    fr_half = fall_run(body, mu, 0.5 * dt)
    ev["body"], ev["fall"] = body, fr
    print(f"the fall (drawing model): the {fa} books as one rigid body, centre of mass {body.xc * 100:.2f} cm past the "
          f"edge and {body.yc * 100:.1f} cm up, I about the centre {body.I * 1e4:.2f} m cm^2 per book mass (books "
          f"(L^2 + t^2) / 12 plus parallel axes), {body.Ie * 1e4:.2f} about the corner; RK4 at dt = {dt:.0e} s, events "
          f"by bisection inside the step")
    for m_ in (mu, mu2):
        a, b = tab[m_], face[m_]
        print(f"  grip {m_:g}, the brief's table-frame split (horizontal over vertical corner force): pivots "
              f"{a['t_end']:.3f} s to {math.degrees(a['th_end']):.1f} deg ({a['w_end']:.2f} rad/s), vertical push "
              f"{a['Ry']:.3f} W; the face frame (normal to the bottom book's face, drawn): pivots {b['t_end']:.3f} s to "
              f"{math.degrees(b['th_end']):.1f} deg ({b['w_end']:.2f} rad/s), push {b['N']:.3f} W, grip needed "
              f"{abs(b['F'] / b['N']):.3f}")
    print(f"  half-step rerun (face, grip {mu:g}): {half['t_end']:.6f} s against {face[mu]['t_end']:.6f} s "
          f"({half['t_end'] - face[mu]['t_end']:+.1e} s), {math.degrees(half['th_end']):.4f} deg")
    print(f"  drawn (grip {mu:g}): pivots {fr['piv']['t_end']:.3f} s to {math.degrees(fr['piv']['th_end']):.1f} deg, then "
          f"slides {fr['slide_dist'] * 100:.2f} cm along the bottom face over the corner (kinetic grip {mu:g}) until "
          f"{fr['t_fly0']:.3f} s at {math.degrees(fr['th_fly0']):.1f} deg ({fr['why']}), then flies free at "
          f"({fr['V_fly0'][0]:.2f}, {fr['V_fly0'][1]:.2f}) m/s turning {fr['w_fly']:.2f} rad/s; half-step rerun leaves "
          f"at {fr_half['t_fly0']:.5f} s ({fr_half['t_fly0'] - fr['t_fly0']:+.1e} s); the slide speed never "
          f"reverses (min {fr['min_pd']:.1e} m/s)")
    assert abs(half["t_end"] - face[mu]["t_end"]) < 1e-4 and abs(fr_half["t_fly0"] - fr["t_fly0"]) < 1e-3
    assert fr["min_pd"] > -1e-9, "the slide reversed"
    # Sample the drawn fall: no book corner inside the table, the table corner inside no book,
    # the highest corner (band px), and when every book has left the band.
    top_px = float(man["table_top_dy"])
    band_bottom = -(BAND_H - top_px) / ppm
    t_out, y_hi, worst_pen = None, -1.0, 0.0
    rt = 0.0
    while rt < 3.0:
        ph, C, th = fall_state(fr, g, rt)
        boxes = body.corners(C, th)
        for box in boxes:
            for (x, y) in box:
                y_hi = max(y_hi, y)
                if x < -1e-4 and y < -1e-4:
                    worst_pen = max(worst_pen, min(-x, -y))
            if inside((0.0, 0.0), box, 1e-4):
                worst_pen = max(worst_pen, 1.0)
        if t_out is None and all(y < band_bottom for box in boxes for (_, y) in box):
            t_out = rt
            break
        rt += 0.001
    assert t_out is not None and worst_pen < 1e-3, "the drawn fall cuts the table or never leaves the band"
    ev["t_out"] = t_out
    y_hi_px = top_px - y_hi * ppm
    print(f"  drawn fall checks: no book corner inside the table and the table corner inside no book over the fall "
          f"(worst {worst_pen * 1000:.2f} mm); the highest corner reaches {y_hi_px:.0f} px under the band top (the "
          f"readout rows end at {ROWS_BOTTOM}); every book is under the band bottom {t_out:.3f} s after the tip starts")
    assert y_hi_px > ROWS_BOTTOM + 8, "the tipping books reach the readout rows"
    # The brief's checks.
    req, rsh = ev["rep"]["equal"], ev["rep"]["shrinking"]
    checks: list[tuple[str, float, float, float]] = []
    exact: list[tuple[str, Fr, Fr]] = []
    for j, want in enumerate(("5.56", "3.34", "1.12", "-1.10", "-3.32")):
        exact.append((f"equal after book {j + 1} worst margin (cm)", req["rows"][j]["worst"], Fr(want)))
    exact.append(("equal four books' centre past the edge (cm)", req["rows"][3]["com"], Fr("1.10")))
    exact.append(("equal falls at book", Fr(req["fall_at"]), Fr(4)))
    exact.append(("rule limit n = 3 (cm)", rule[3], Fr(5)))
    exact.append(("rule limit n = 4 (cm)", rule[4], Fr(4)))
    exact.append(("equal holds books", Fr(holds), Fr(3)))
    for j, want in enumerate(("8.10", "6.90", "5.433", "3.475", "0.200")):
        r = rsh["rows"][j]
        if j == 2:
            checks.append((f"shrinking after book {j + 1} worst margin (cm)", float(r["worst"]), 5.433, 5e-4))
        else:
            exact.append((f"shrinking after book {j + 1} worst margin (cm)", r["worst"], Fr(want)))
    exact.append(("shrinking worst after book 5 at book", Fr(rsh["rows"][4]["at"]), Fr(3)))
    exact.append(("shrinking falls never (0 = never)", Fr(rsh["fall_at"] or 0), Fr(0)))
    exact.append(("shrinking every margin positive (1 = yes)", Fr(int(all(x > 0 for r in rsh["rows"] for x in r["ms"]))), Fr(1)))
    exact.append(("shrinking top front end (cm)", rsh["top"], Fr("22.20")))
    exact.append(("shrinking top back end past the edge (cm)", rsh["back"], Fr("2.20")))
    exact.append(("equal top front end after 5 (cm)", req["top"], Fr("22.20")))
    exact.append(("limit five books (of a book)", lim[5], Fr(137, 120)))
    exact.append(("limit four books (of a book)", lim[4], Fr(25, 24)))
    checks.append(("limit five books (cm)", float(lim[5] * L), 22.833, 5e-4))
    checks.append(("limit four books (cm)", float(lim[4] * L), 20.833, 5e-4))
    checks.append(("four-book clearance (cm)", float(lim[4] * L - L), 0.8, 0.05))
    checks.append(("fall body centre past the edge (cm)", body.xc * 100, 1.10, 1e-9))
    checks.append(("fall body centre up (cm)", body.yc * 100, 6.0, 1e-9))
    checks.append(("table-frame pivot time, grip 0.3 (s)", tab[mu]["t_end"], 0.335, 6e-4))
    checks.append(("table-frame pivot angle, grip 0.3 (deg)", math.degrees(tab[mu]["th_end"]), 51.5, 0.06))
    checks.append(("table-frame spin, grip 0.3 (rad/s)", tab[mu]["w_end"], 7.56, 6e-3))
    checks.append(("table-frame pivot time, grip 0.5 (s)", tab[mu2]["t_end"], 0.348, 6e-4))
    checks.append(("table-frame pivot angle, grip 0.5 (deg)", math.degrees(tab[mu2]["th_end"]), 57.6, 0.06))
    out, fails = [], 0
    for name, got, want in exact:
        ok = got == want
        fails += not ok
        out.append(f"{name}: brief {want}, sim {got} exactly: {'ok' if ok else 'FAIL'}")
    for name, got, want, tol in checks:
        ok = abs(got - want) <= tol
        fails += not ok
        out.append(f"{name}: brief {want:g}, sim {got:.6g}, diff {got - want:+.1e}: {'ok' if ok else 'FAIL'}")
    print(f"checks against the brief ({len(exact) + len(checks)} checks, {len(exact)} exact in fractions, {fails} failed): "
          + "; ".join(out))
    assert fails == 0, "a check against the brief failed"
    # The schedule in video time.
    t0 = man["first_cycle_at"]
    k0 = math.ceil((0.0 - t0) / P - 1e-9) - 1
    k1 = math.floor((D - t0) / P - 1e-9)
    starts = [t0 + kk * P for kk in range(k0, k1 + 1)]
    ev["cycles"] = int(round(cycles))

    def lst(off_: float) -> str:
        return ", ".join(f"{st + off_:.2f}" for st in starts if 0.0 <= st + off_ < D)

    lands = man["land_s"]
    tip_at = lands[fa - 1]
    piv_v = S * fr["piv"]["t_end"]
    out_v = tip_at + S * t_out
    ev["tip_at"] = tip_at
    assert out_v <= 6.0 + 1e-9, "the equal stack is still in the band at 6 s of the cycle"
    assert lands[-1] < P - F and lands[0] - man["slide_s"] >= 0.0
    tau0 = (0.0 - t0) % P
    sliding0 = [j for j, x in enumerate(lands) if x - man["slide_s"] <= tau0 < x]
    first_note = ", ".join(
        [f"book {j + 1} {(tau0 - (lands[j] - man['slide_s'])) / man['slide_s'] * 100:.0f} percent through its slide"
         for j in sliding0]
        + ([f"the equal stack {tau0 - tip_at:.2f} s of video into its fall"] if tip_at <= tau0 < out_v else []))
    assert first_note, "the first frame has no motion"
    print(f"schedule (video time): cycles of {P:g} s start at " + ", ".join(f"{st:.2f}" for st in starts)
          + f" s (the first {-t0:.2f} s before the first frame); each book slides in over the {man['slide_s']:g} s before "
          f"it lands; books land {', '.join(f'{x:g}' for x in lands)} s into each cycle: "
          + "; ".join(f"book {j + 1} at {lst(x)} s" for j, x in enumerate(lands))
          + f"; the equal stack never gets book 5; it starts to tip as book {fa} lands at {lst(tip_at)} s (its event row "
          f"lights), the fall drawn at 1/{S:g} speed: it pivots {piv_v:.2f} s of video to "
          f"{math.degrees(fr['piv']['th_end']):.1f} deg, slides off by {lst(tip_at + S * fr['t_fly0'])} s and has left "
          f"the band at {lst(out_v)} s ({out_v:.2f} s into the cycle, by 6 s); the shrinking stack's book 5 lands and its "
          f"event row lights at {lst(lands[-1])} s; both held to {P - F:g} s, the reset crossfade over the last {F:g} s "
          f"of each cycle (from {lst(P - F)} s); on the first frame the cycle is {tau0:.2f} s in ({first_note}); title until "
          f"{man['title_until']:g} s; payoff card from {man['payoff_t']:g} s; the title fades back in over the last "
          f"{man['loop_fade']:g} s and the last frame repeats the first ({D:g} s holds exactly {cycles:.0f} cycles)")
    # Text widths.
    font = os.environ["SEED_ZERO_FONT"]
    f28, f34, f40, f56 = (ImageFont.truetype(font, n) for n in (28, 34, 40, 56))
    widths = {"overlay@34": (f34, man["overlay"])}
    for j, line in enumerate(man["title"].split("|")):
        widths[f"title line {j + 1}@56"] = (f56, line)
    widths["legend@40"] = (f40, legend_text())
    widths["clock@28"] = (f28, clock_text(man))
    for m in PANELS:
        widths[f"label {m}@40"] = (f40, label_text(man, m))
        widths[f"event {m}@28"] = (f28, event_text(ev, m))
    widths["book count@28"] = (f28, count_text(5))
    widths["balance behind@28"] = (f28, balance_text(Fr("-8.10")))
    widths["balance past@28"] = (f28, balance_text(Fr("1.10")))
    widths["top book@28"] = (f28, top_text(Fr("22.2")))
    for j, line in enumerate(payoff_lines(man, ev)):
        widths[f"payoff line {j + 1}@40"] = (f40, line)
    print("text widths (the on-screen strings verbatim): " + ", ".join(
        f"{kk} {f.getlength(s):.0f} px '{s}'" for kk, (f, s) in widths.items()))
    assert all(f.getlength(s) < 950 for f, s in widths.values()), "a text line is wider than 950 px"
    assert len(payoff_lines(man, ev)) <= 6, "the card has more than six lines"
    # Layout checks (band-local pixels).
    left84 = ROW_X0 + f28.getlength(count_text(5))
    right84 = ROW_X1 - f28.getlength(top_text(Fr("22.2")))
    left120 = ROW_X0 + max(f28.getlength(balance_text(Fr("-8.10"))), f28.getlength(balance_text(Fr("1.10"))))
    stack_top = top_px - nb * float(T) / 100.0 * ppm
    edge = float(man["edge_x_px"])
    xs_front = {m: [edge + float(e) / 100.0 * ppm for e in ends_of(steps[m])] for m in PANELS}
    x_max = max(max(v) for v in xs_front.values())
    x_min = min(x - float(L) / 100.0 * ppm for v in xs_front.values() for x in v)
    ev_w = {m: f28.getlength(event_text(ev, m)) for m in PANELS}
    dim_y = stack_top - DIM_DY
    print(f"row check: the label rows run 40 px under the band top; row 84 ends at x {left84:.0f} px on the left and "
          f"starts at x {right84:.0f} px on the right; row 120 ends at x {left120:.0f} px; the rows end {ROWS_BOTTOM} px "
          f"under the band top; the five-book stack's top is {stack_top:.0f} px under the band top, its overhang line at "
          f"{dim_y:.0f} px, the dashed edge line from the table top to {DASH_TOP} px; the books span x {x_min:.0f} to "
          f"{x_max:.0f} px; the table top {top_px:.0f} px under the band top with its edge at x {edge:.0f}, slab to "
          f"{top_px + SLAB_PX:.0f}, a leg at x {LEG_X} to {LEG_X + LEG_W}; the centre-of-mass triangle from "
          f"{top_px + 2:.0f} to {top_px + 2 + TRI_H:.0f} px; the event rows centred {EVENT_DY} px under the band top from "
          f"x {EVENT_X} to {EVENT_X + ev_w['equal']:.0f} (equal) and {EVENT_X + ev_w['shrinking']:.0f} (shrinking); the "
          f"falling books are drawn only past the edge under the table top; each band is {BAND_H} px tall (y "
          f"{BAND_Y['equal']} to {BAND_Y['equal'] + BAND_H} and {BAND_Y['shrinking']} to {BAND_Y['shrinking'] + BAND_H}); "
          f"the caption band starts at y {int(man['caption_y'] * H)}; the title rows end at y {TITLE_YS[-1] + 28}")
    assert right84 - left84 > 40, "the row 84 columns meet"
    assert stack_top > ROWS_BOTTOM + 10 and dim_y - 4 > ROWS_BOTTOM, "the stack meets the readout rows"
    assert x_max < W - 20 and x_min > 0, "a book leaves the frame"
    assert EVENT_DY - 16 > top_px + SLAB_PX and EVENT_DY + 16 < BAND_H, "the event row leaves the space under the slab"
    assert EVENT_X > LEG_X + LEG_W + 10, "the event row meets the leg"
    assert EVENT_X + ev_w["equal"] < edge - 10, "the equal event row reaches past the edge where the books fall"
    assert BAND_Y["shrinking"] + BAND_H <= int(man["caption_y"] * H), "the bottom band reaches the caption band"
    assert PAYOFF_Y - 20 > int(man["caption_y"] * H) + 90, "the card meets the caption band"
    assert PAYOFF_Y + 5 * PAYOFF_PITCH + 20 < H, "the card leaves the frame"
    return ev


def legend_text() -> str:
    return "same five books, same table edge"


def clock_text(man: dict) -> str:
    return f"one book a second, the fall at 1/{man['slow']:g} speed"


def label_text(man: dict, m: str) -> str:
    if m == "equal":
        return f"equal steps, {man['steps_cm']['equal'][0]} cm"
    s = man["steps_cm"]["shrinking"]
    return f"shrinking steps, {s[-1]} to {s[0]} cm"


def count_text(n: int) -> str:
    return f"book {n} of 5"


def balance_text(com: Fr) -> str:
    if com > 0:
        return f"balance {float(com):.2f} cm past the edge"
    return f"balance {float(-com):.2f} cm behind the edge"


def top_text(top: Fr) -> str:
    return f"top book {float(top):.1f} cm out"


def event_text(ev: dict, m: str) -> str:
    if m == "equal":
        return f"equal: falls at book {ev['rep']['equal']['fall_at']}"
    return f"shrinking: holds, {float(ev['rep']['shrinking']['back']):.1f} cm past the table"


def payoff_lines(man: dict, ev: dict) -> list[str]:
    lim5 = ev["lim"][5]
    text = man["payoff_text"].format(gap=float(ev["rep"]["shrinking"]["back"]), d_eq=float(ev["steps"]["equal"][0]),
                                     fall_at=ev["rep"]["equal"]["fall_at"], lim5=float(lim5 * ev["L"]),
                                     lim5_frac=f"{lim5.numerator}/{lim5.denominator}")
    return [s.strip() for s in text.split("|")]


# --- rendering ---------------------------------------------------------------
class Renderer:
    def __init__(self, man: dict, ev: dict):
        self.man, self.ev = man, ev
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_small = ImageFont.truetype(font, 28)
        self.ppm = float(man["px_per_m"])
        self.S = man["slow"]
        self.P = man["cycle_s"]
        self.P_f = int(round(man["cycle_s"] * self.fps))
        self.c0_f = int(round(man["first_cycle_at"] * self.fps))
        self.F = man["reset_fade"]
        self.edge = float(man["edge_x_px"])
        self.top = float(man["table_top_dy"])
        self.Lp = float(ev["L"]) / 100.0 * self.ppm
        self.Tp = float(ev["T"]) / 100.0 * self.ppm
        self.lands = man["land_s"]
        self.slide = man["slide_s"]
        self.fall_at = ev["rep"]["equal"]["fall_at"]
        self.fronts = {m: [self.edge + float(e) / 100.0 * self.ppm for e in ends_of(ev["steps"][m])] for m in PANELS}

    def phase(self, f: int) -> tuple[int, float]:
        k, tau_f = divmod(f - self.c0_f, self.P_f)
        return k, tau_f / self.fps

    @staticmethod
    def L_(x: float, y: float) -> tuple[float, float]:
        """Layer (2x) pixel of a band-local point, rounded to 1e-4 px so equal states draw equal pixels."""
        return round(x * SS, 4), round(y * SS, 4)

    @staticmethod
    def dashed(d: ImageDraw.ImageDraw, a: tuple, b: tuple, col, dash: float, gap: float, width: int) -> None:
        ax, ay = a
        bx, by = b
        length = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / length, (by - ay) / length
        s = 0.0
        while s < length:
            e = min(length, s + dash)
            d.line((ax + ux * s, ay + uy * s, ax + ux * e, ay + uy * e), fill=col, width=width)
            s = e + gap

    def draw_table(self, d: ImageDraw.ImageDraw) -> None:
        top, edge = self.top, self.edge
        s0, s1 = self.L_(-10, top), self.L_(edge, top + SLAB_PX)
        d.rectangle((s0[0], s0[1], s1[0], s1[1]), fill=DECK_A)
        t0, t1 = self.L_(0, top), self.L_(edge - 2, top)
        d.line((*t0, *t1), fill=DECK_B, width=3 * SS)
        e0, e1 = self.L_(edge - 1, top + 3), self.L_(edge - 1, top + SLAB_PX - 3)
        d.line((*e0, *e1), fill=RIM, width=2 * SS)
        l0, l1 = self.L_(LEG_X, top + SLAB_PX), self.L_(LEG_X + LEG_W, BAND_H + 2)
        d.rectangle((l0[0], l0[1], l1[0], l1[1]), fill=DECK_A)
        self.dashed(d, self.L_(edge, top - 4), self.L_(edge, DASH_TOP), blend(MUTED, 0.75), 8 * SS, 7 * SS, 2 * SS)

    def draw_book(self, d: ImageDraw.ImageDraw, k: int, pts: list[tuple[float, float]]) -> None:
        """Book k as a quad of band-local points (back-bottom, front-bottom, front-top, back-top)."""
        col = BOOKS[k]
        dark = tuple(int(c * 0.55) for c in col)
        poly = [self.L_(*p) for p in pts]
        d.polygon(poly, fill=col, outline=dark, width=2 * SS)
        # The spine line 14 px in from the back end.
        (bx0, by0), (fx0, fy0), (fx1, fy1), (bx1, by1) = pts
        lx, ly = (fx0 - bx0) / self.Lp, (fy0 - by0) / self.Lp
        a = (bx0 + lx * 14, by0 + ly * 14)
        b = (bx1 + lx * 14, by1 + ly * 14)
        d.line((*self.L_(*a), *self.L_(*b)), fill=dark, width=2 * SS)

    def upright(self, front: float, k: int) -> list[tuple[float, float]]:
        y0 = self.top - k * self.Tp
        return [(front - self.Lp, y0), (front, y0), (front, y0 - self.Tp), (front - self.Lp, y0 - self.Tp)]

    def placed(self, m: str, tau: float) -> int:
        n = sum(1 for x in self.lands if tau >= x - 1e-9)
        return min(n, self.fall_at) if m == "equal" else n

    def scene(self, m: str, tau: float) -> tuple[Image.Image, dict]:
        """The band layer of band m at tau seconds into a cycle (the empty table before the first slide)."""
        layer = Image.new("RGB", (W * SS, BAND_H * SS), BG)
        d = ImageDraw.Draw(layer)
        self.draw_table(d)
        ev = self.ev
        n = self.placed(m, tau)
        st = {"n": n, "sliding": None, "phase": STAND, "tau": tau}
        fronts = self.fronts[m]
        tipping = m == "equal" and n >= self.fall_at and tau >= self.lands[self.fall_at - 1]
        if tipping:
            rt = (tau - self.lands[self.fall_at - 1]) / self.S
            ph, C, th = fall_state(ev["fall"], self.man["g"], rt)
            st["phase"] = ph
            for k, box in enumerate(ev["body"].corners(C, th)):
                pts = [(self.edge + x * self.ppm, self.top - y * self.ppm) for (x, y) in box]
                pts = [pts[0], pts[1], pts[2], pts[3]]
                self.draw_book(d, k, pts)
        else:
            for k in range(n):
                self.draw_book(d, k, self.upright(fronts[k], k))
        # The book sliding in from the left along the top of the stack.
        if n < len(self.lands) and not (m == "equal" and n >= self.fall_at):
            t_land = self.lands[n]
            u = (tau - (t_land - self.slide)) / self.slide
            if 0.0 <= u < 1.0:
                e = 1.0 - (1.0 - u) ** 3
                x_start = -12.0                                    # the front end just off the left edge
                front = x_start + (fronts[n] - x_start) * e
                self.draw_book(d, n, self.upright(front, n))
                st["sliding"] = n + 1
        # The overhang line over the top book and the centre-of-mass triangle.
        if n > 0 and not tipping and st["sliding"] is None:
            ytop = self.top - n * self.Tp - DIM_DY
            x1 = fronts[n - 1]
            d.line((*self.L_(self.edge, ytop), *self.L_(x1, ytop)), fill=MUTED, width=2 * SS)
            for x in (self.edge, x1):
                d.line((*self.L_(x, ytop - 6), *self.L_(x, ytop + 6)), fill=MUTED, width=2 * SS)
            if m == "shrinking" and n == len(self.lands):
                # The gap between the table edge and the top book's back end, in gold.
                yb = self.top - (n - 0.5) * self.Tp
                xb = fronts[n - 1] - self.Lp
                d.line((*self.L_(self.edge + 2, yb), *self.L_(xb - 2, yb)), fill=GOLD, width=3 * SS)
                for x in (self.edge + 2, xb - 2):
                    d.line((*self.L_(x, yb - 9), *self.L_(x, yb + 9)), fill=GOLD, width=3 * SS)
        if n > 0:
            com = ev["rep"][m]["rows"][n - 1]["com"]
            cx = self.edge + float(com) / 100.0 * self.ppm
            y0 = self.top + 2
            tri = [self.L_(cx, y0), self.L_(cx - TRI_W / 2, y0 + TRI_H), self.L_(cx + TRI_W / 2, y0 + TRI_H)]
            d.polygon(tri, fill=GOLD)
        return layer, st

    def draw_panel(self, m: str, f: int) -> tuple[Image.Image, dict]:
        k, tau = self.phase(f)
        P, F = self.P, self.F
        layer, st = self.scene(m, tau)
        st["alpha"] = 1.0
        if tau >= P - F:
            # Crossfade to the next cycle's empty table (the fallen books left the band by 6 s, asserted).
            a = (tau - (P - F)) / F
            new, st_new = self.scene(m, tau - P)
            layer = Image.blend(layer, new, a)
            st["alpha"] = max(0.0, 1.0 - 2.0 * a)
            st_new["alpha"] = max(0.0, 2.0 * a - 1.0)
            if a >= 0.5:
                st = st_new
        return layer, st

    def draw_text(self, d: ImageDraw.ImageDraw, states: dict, hud_alpha: float) -> None:
        man, ev = self.man, self.ev
        for m, st in states.items():
            y0 = BAND_Y[m]
            a, n = st["alpha"], st["n"]
            d.text((ROW_X0, y0 + LABEL_DY), label_text(man, m), font=self.font, fill=COLOUR[m], anchor="lm")
            shown = st["sliding"] or n
            if shown:
                d.text((ROW_X0, y0 + SUB_DY), count_text(shown), font=self.font_small, fill=blend(TEXT, a), anchor="lm")
            if n:
                row = ev["rep"][m]["rows"][n - 1]
                com = row["com"]
                d.text((ROW_X0, y0 + FIX_DY), balance_text(com), font=self.font_small,
                       fill=blend(GOLD if com > 0 else TEXT, a), anchor="lm")
                d.text((ROW_X1, y0 + SUB_DY), top_text(row["top"]), font=self.font_small, fill=blend(MUTED, a), anchor="rm")
            lit = (m == "equal" and n >= self.fall_at) or (m == "shrinking" and n == len(self.lands))
            if lit:
                d.text((EVENT_X, y0 + EVENT_DY), event_text(ev, m), font=self.font_small, fill=blend(GOLD, a), anchor="lm")
        if hud_alpha > 0.02:
            d.text((W / 2, LEGEND_Y), legend_text(), font=self.font, fill=blend(TEXT, hud_alpha), anchor="mm")
            d.text((W / 2, CLOCK_Y), clock_text(man), font=self.font_small, fill=blend(MUTED, hud_alpha), anchor="mm")

    def live_frame(self, f: int, title_alpha: float | None = None, hud_alpha: float = 0.0) -> np.ndarray:
        man = self.man
        t = f / self.fps
        if title_alpha is None:
            if t < man["title_until"]:
                title_alpha = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
                hud_alpha = 0.0
            else:
                title_alpha = 0.0
                hud_alpha = min(1.0, (t - man["title_until"]) / 0.4)
        img = Image.new("RGB", (W, H), BG)
        states = {}
        for m in PANELS:
            layer, states[m] = self.draw_panel(m, f)
            img.paste(layer.reduce(SS), (0, BAND_Y[m]))
        d = ImageDraw.Draw(img)
        self.draw_text(d, states, hud_alpha)
        if title_alpha > 0.0:
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, TITLE_YS[j]), line, font=self.font_title, fill=blend(TEXT, title_alpha), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"]) * hud_alpha
            for j, line in enumerate(payoff_lines(man, self.ev)):
                d.text((W / 2, PAYOFF_Y + j * PAYOFF_PITCH), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.uint8)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f == total - 1:
            return self.live_frame(0)   # the scene is periodic: the last frame repeats the first
        if f >= total - fade_frames:
            # The geometry runs on; the legend, clock and card fade out over the first half of the
            # loop fade and the title fades in over the second half, so the two never overlap.
            a = (f - (total - fade_frames) + 1) / fade_frames
            return self.live_frame(f, title_alpha=max(0.0, 2.0 * a - 1.0), hud_alpha=max(0.0, 1.0 - 2.0 * a))
        return self.live_frame(f)

    def render(self, out_path: Path) -> None:
        global _RENDERER
        out_path.parent.mkdir(parents=True, exist_ok=True)
        total = int(round(self.man["scene_duration"] * self.fps))
        first = self.frame_at(0)
        last = self.frame_at(total - 1)
        diff = np.abs(first.astype(int) - last.astype(int))
        loop_px = int((diff.max(axis=2) > 24).sum())
        print(f"loop check: last frame differs from the first in {loop_px} px (max channel difference {int(diff.max())})")
        assert loop_px == 0
        wrap = self.live_frame(total, title_alpha=1.0, hud_alpha=0.0)   # the scene one period on, drawn live
        diff = np.abs(first.astype(int) - wrap.astype(int))
        print(f"periodicity check: the scene drawn live at {self.man['scene_duration']:g} s differs from 0 s in "
              f"{int((diff.max(axis=2) > 24).sum())} px (max channel difference {int(diff.max())})")
        prev = self.frame_at(total - 2)
        diff = np.abs(prev.astype(int) - last.astype(int))
        print(f"loop step: the frame before the last differs from the last in {int((diff.max(axis=2) > 24).sum())} px")
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{W}x{H}", "-r", str(self.fps), "-i", "-",
             "-c:v", "libx264", "-crf", "16", "-preset", "medium",
             "-pix_fmt", "yuv420p", str(out_path)],
            stdin=subprocess.PIPE,
        )
        assert proc.stdin is not None
        _RENDERER = self
        workers = min(12, os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("fork")) as pool:
            for f, frame in enumerate(pool.map(_frame_bytes, range(total), chunksize=8)):
                proc.stdin.write(frame)
                if f % 300 == 0:
                    print(f"frame {f}/{total}", file=sys.stderr)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")
        print(f"footage: {out_path} ({total / self.fps:.2f}s at {self.fps} fps)")


_RENDERER: Renderer | None = None


def _frame_bytes(f: int) -> bytes:
    assert _RENDERER is not None
    return _RENDERER.frame_at(f).tobytes()


def main() -> None:
    man = json.loads((ROOT / f"projects/{NAME}/manifest.json").read_text())
    ev = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, ev)
        (ROOT / f"media/{NAME}").mkdir(parents=True, exist_ok=True)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/{NAME}/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, ev).render(ROOT / f"media/{NAME}/footage.mp4")


if __name__ == "__main__":
    main()

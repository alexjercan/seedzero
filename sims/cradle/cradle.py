#!/usr/bin/env python3
"""Newton's cradle: lift two balls. How many fly out?

Five identical steel balls hang side by side on strings of length L from
pivots one ball diameter plus a hair (the manifest gap, 0.3 mm) apart. Each
ball is an exact pendulum in its own angle theta_i (no small-angle
approximation); neighbours push on each other with a Hertz contact force
F = k delta^1.5 along the line of centres while their centre distance is
under one diameter (delta is the overlap):

    m L theta_i'' = -m g sin theta_i + F_i . t_i,   t_i = (cos theta_i, sin theta_i)

Two cradles, same balls: the top one has ball 1 lifted so its centre is
10 cm above rest, the bottom one has balls 1 and 2 lifted together to the
same height; both are let go at the same moment. RK4 at a fixed base
step; while any pair is in contact the base step is cut into sub-steps,
and every contact onset and offset is bracketed with a geometric ramp of
tiny steps, because the Hertz force has a kink at zero overlap that would
otherwise cost energy accuracy. Deterministic, no seed.

The stiffness is softened from real steel so that a click lasts about
0.4 ms and the step resolves it (real steel squashes 41 microns and
clicks for 86 microseconds); the outcome does not depend on it (checked
at ten times the stiffness). The hair of a gap makes each click finish before
the next one starts, as in a real cradle; with no gap at all the whole
chain squeezes as one and the far ball takes the larger share (checked
and printed, not drawn).

Measured and printed: the incoming speed at the first click against
sqrt(2 g h), the first-click time, the contact durations, each ball's
outgoing speed and peak rise after the first click, how many balls leave
the far side (peak rise over the manifest threshold), the height one
ball at double speed would reach and the energy that needs, the swing
period and the click cadence, momentum and energy before and after the
first clicks and the relative energy drift over the run, checks at half
the step, at ten times the stiffness and with no gap, the state at the
end of the scene against the start, and the on-screen text widths.

usage: cradle.py [--measure-only] [--frames t1,t2,...]
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
W, H = 1080, 1920
N = 5

BG = (11, 14, 18)
TEAL = (92, 200, 165)
GOLD = (240, 176, 84)
CORAL = (232, 96, 88)
TEXT = (216, 222, 230)
MUTED = (138, 148, 163)
WIRE = (70, 80, 94)
WHITE = (236, 240, 244)
BEAM = (120, 130, 145)
STRING = (150, 158, 170)
STEEL = (178, 186, 198)
STEEL_EDGE = (92, 100, 112)
GOLD_EDGE = (120, 84, 30)
CORAL_EDGE = (128, 42, 38)

# Layout: overlay at y 96..130 (compose), title rows at y 190/252 for the
# first seconds, two panels stacked from y 336 (one ball lifted) and 886
# (two balls lifted), each with a label row, a pivot bar 100 px below the
# panel top, strings of L px and the balls at rest 505 px below the top,
# the cradle centred at x 500 so the far ball clears the ruler at x 990;
# captions at caption_y 0.75 (y 1440..1520), payoff card from y 1592.
GEOM_Y0, GEOM_Y1 = 336, 1436
PANEL_H = 550
PIVOT_DY = 100
PAYOFF_Y = 1592.0
RULER_X = 990
CRADLE_CX = 500
SS = 2
PANELS = [
    {"name": "one", "label": "one ball lifted", "lifted": 1, "colour": GOLD, "edge": GOLD_EDGE, "top": GEOM_Y0},
    {"name": "two", "label": "two balls lifted", "lifted": 2, "colour": CORAL, "edge": CORAL_EDGE, "top": GEOM_Y0 + PANEL_H},
]


def blend(col, a, base=BG):
    return tuple(int(round(c * a + b * (1 - a))) for c, b in zip(col, base))


def ball_mass(man: dict) -> float:
    r = man["ball_radius_m"]
    return 4.0 / 3.0 * math.pi * r ** 3 * man["steel_density_kg_m3"]


def hertz_real(man: dict) -> float:
    """Hertz stiffness of two real steel balls, F = k delta^1.5."""
    E, nu, r = man["young_modulus_pa"], man["poisson_ratio"], man["ball_radius_m"]
    e_star = E / (2.0 * (1.0 - nu * nu))
    return 4.0 / 3.0 * e_star * math.sqrt(r / 2.0)


def contact_closed_form(m: float, k: float, v: float) -> tuple[float, float]:
    """Max overlap and duration of a head-on Hertz collision of two equal balls at closing speed v."""
    d_max = (5.0 * m * v * v / (8.0 * k)) ** 0.4
    return d_max, 2.9432 * d_max / v


def pendulum_period(L: float, g: float, amp: float) -> float:
    """Exact period of a pendulum swinging to amplitude amp (rad), via the AGM."""
    a, b = 1.0, math.cos(amp / 2.0)
    while abs(a - b) > 1e-15:
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return 2.0 * math.pi * math.sqrt(L / g) / a


def cfg_for(man: dict, lifted: int, duration: float, dt: float | None = None, k: float | None = None,
            gap: float | None = None) -> dict:
    return {
        "g": man["g"], "L": man["string_length_m"], "r": man["ball_radius_m"], "m": ball_mass(man),
        "k": man["hertz_k"] if k is None else k, "gap": man["gap_m"] if gap is None else gap,
        "lift": man["lift_m"], "dt": man["dt"] if dt is None else dt, "sub": man["contact_substeps"],
        "store_every": man["store_every"], "lifted": lifted, "duration": duration,
    }


def simulate(cfg: dict) -> dict:
    """Integrate one cradle; return sampled angles and rates, contact intervals, turning points and click states."""
    g, L, r, m, k, gap = cfg["g"], cfg["L"], cfg["r"], cfg["m"], cfg["k"], cfg["gap"]
    dt, sub, lifted = cfg["dt"], cfg["sub"], cfg["lifted"]
    n_steps = int(round(cfg["duration"] / dt))
    store_every = cfg["store_every"]
    twor = 2.0 * r
    pitch = twor + gap
    gL = g / L
    kF = k / (m * L)
    th0 = -math.acos(1.0 - cfg["lift"] / L)
    th = [th0 if i < lifted else 0.0 for i in range(N)]
    om = [0.0] * N
    ramp = tuple(0.5 ** j for j in range(1, 11)) + (0.5 ** 10,)
    ramp_rev = ramp[::-1]

    def accel(th, om):
        s = [math.sin(a) for a in th]
        c = [math.cos(a) for a in th]
        acc = [-gL * si for si in s]
        dl = [-1.0] * (N - 1)
        for i in range(N - 1):
            if L * (s[i + 1] - s[i]) < -gap:
                dx = pitch + L * (s[i + 1] - s[i])
                dy = L * (c[i] - c[i + 1])
                d = math.hypot(dx, dy)
                delta = twor - d
                dl[i] = delta
                if delta > 0.0:
                    F = kF * delta ** 1.5
                    nx, ny = dx / d, dy / d
                    acc[i] -= F * (nx * c[i] + ny * s[i])
                    acc[i + 1] += F * (nx * c[i + 1] + ny * s[i + 1])
        return acc, dl

    def gaps(th):
        s = [math.sin(a) for a in th]
        c = [math.cos(a) for a in th]
        return [twor - math.hypot(pitch + L * (s[i + 1] - s[i]), L * (c[i] - c[i + 1])) for i in range(N - 1)]

    def rk4(th, om, k1, Hs):
        h2, h6 = Hs / 2.0, Hs / 6.0
        th2 = [a + h2 * w for a, w in zip(th, om)]
        om2 = [w + h2 * a for w, a in zip(om, k1)]
        k2, _ = accel(th2, om2)
        th3 = [a + h2 * w for a, w in zip(th, om2)]
        om3 = [w + h2 * a for w, a in zip(om, k2)]
        k3, _ = accel(th3, om3)
        th4 = [a + Hs * w for a, w in zip(th, om3)]
        om4 = [w + Hs * a for w, a in zip(om, k3)]
        k4, _ = accel(th4, om4)
        thn = [a + h6 * (w + 2 * w2 + 2 * w3 + w4) for a, w, w2, w3, w4 in zip(th, om, om2, om3, om4)]
        omn = [w + h6 * (a1 + 2 * a2 + 2 * a3 + a4) for w, a1, a2, a3, a4 in zip(om, k1, k2, k3, k4)]
        k1n, dln = accel(thn, omn)
        return thn, omn, k1n, dln

    def advance(th, om, k1, dl, Hs, depth):
        """RK4 over Hs; a contact onset or offset inside the step is bracketed with a ramp of tiny steps."""
        thn, omn, k1n, dln = rk4(th, om, k1, Hs)
        if depth >= 14:
            return thn, omn, k1n, dln
        cross = [i for i in range(N - 1) if (dl[i] > 0.0) != (dln[i] > 0.0)]
        if not cross:
            return thn, omn, k1n, dln
        g0, g1 = gaps(th), gaps(thn)
        f = min(g0[i] / (g0[i] - g1[i]) for i in cross)
        if not (1e-9 < f < 1.0 - 1e-9):
            return thn, omn, k1n, dln
        st = (th, om, k1, dl)
        for fr in ramp:
            st = advance(*st, f * Hs * fr, depth + 1)
        for fr in ramp_rev:
            st = advance(*st, (1.0 - f) * Hs * fr, depth + 1)
        return st

    def base_step(th, om, k1, dl):
        if max(dl) > 0.0:
            st = (th, om, k1, dl)
            for _ in range(sub):
                st = advance(*st, dt / sub, 0)
            return st
        thn, omn, k1n, dln = rk4(th, om, k1, dt)
        if any((dl[i] > 0.0) != (dln[i] > 0.0) for i in range(N - 1)):
            st = (th, om, k1, dl)
            for _ in range(sub):
                st = advance(*st, dt / sub, 0)
            return st
        return thn, omn, k1n, dln

    k1, dl = accel(th, om)
    contact = [False] * (N - 1)
    onset = [(0.0, 0.0)] * (N - 1)
    contacts: list[tuple[int, float, float, float]] = []
    events: list[tuple[float, str, int, list, list]] = []
    turns: list[tuple[float, int, float]] = []
    th_s, om_s = [list(th)], [list(om)]
    for step in range(n_steps):
        t = step * dt
        for i in range(N - 1):
            on = dl[i] > 0.0
            if on and not contact[i]:
                onset[i] = (t, dl[i])
                events.append((t, "on", i, list(th), list(om)))
            elif on:
                onset[i] = (onset[i][0], max(onset[i][1], dl[i]))
            elif contact[i]:
                contacts.append((i, onset[i][0], t, onset[i][1]))
                events.append((t, "off", i, list(th), list(om)))
            contact[i] = on
        thn, omn, k1, dl = base_step(th, om, k1, dl)
        for i in range(N):
            if om[i] * omn[i] < 0.0:
                f = om[i] / (om[i] - omn[i])
                turns.append((t + f * dt, i, th[i] + f * (thn[i] - th[i])))
        th, om = thn, omn
        if (step + 1) % store_every == 0:
            th_s.append(list(th))
            om_s.append(list(om))
    return {
        "dt": dt, "store_dt": dt * store_every, "th": np.array(th_s), "om": np.array(om_s),
        "contacts": contacts, "events": events, "turns": turns, "cfg": cfg,
    }


def momentum(cfg: dict, th, om) -> float:
    m, L = cfg["m"], cfg["L"]
    return float(sum(m * L * w * math.cos(a) for a, w in zip(th, om)))


def energy(cfg: dict, th, om) -> float:
    g, L, m, k, r, gap = cfg["g"], cfg["L"], cfg["m"], cfg["k"], cfg["r"], cfg["gap"]
    e = sum(0.5 * m * L * L * w * w + m * g * L * (1.0 - math.cos(a)) for a, w in zip(th, om))
    s = [math.sin(a) for a in th]
    c = [math.cos(a) for a in th]
    for i in range(N - 1):
        delta = 2.0 * r - math.hypot(2.0 * r + gap + L * (s[i + 1] - s[i]), L * (c[i] - c[i + 1]))
        if delta > 0.0:
            e += 0.4 * k * delta ** 2.5
    return float(e)


def energy_series(run: dict) -> np.ndarray:
    cfg = run["cfg"]
    g, L, m, k, r, gap = cfg["g"], cfg["L"], cfg["m"], cfg["k"], cfg["r"], cfg["gap"]
    th, om = run["th"], run["om"]
    e = (0.5 * m * L * L * om * om + m * g * L * (1.0 - np.cos(th))).sum(axis=1)
    s, c = np.sin(th), np.cos(th)
    for i in range(N - 1):
        delta = 2.0 * r - np.hypot(2.0 * r + gap + L * (s[:, i + 1] - s[:, i]), L * (c[:, i] - c[:, i + 1]))
        e += np.where(delta > 0.0, 0.4 * k * np.clip(delta, 0.0, None) ** 2.5, 0.0)
    return e


def analyse(run: dict, thr_cm: float) -> dict:
    """Cluster the contacts into clicks, keep the major ones, and list each ball's peaks between them."""
    cfg = run["cfg"]
    L = cfg["L"]
    episodes: list[dict] = []
    for pair, t0, t1, dmax in sorted(run["contacts"], key=lambda c: c[1]):
        if episodes and t0 <= episodes[-1]["t1"] + 0.01:
            ep = episodes[-1]
            ep["t1"] = max(ep["t1"], t1)
            ep["dmax"] = max(ep["dmax"], dmax)
            ep["pairs"].append((pair, t0, t1, dmax))
        else:
            episodes.append({"t0": t0, "t1": t1, "dmax": dmax, "pairs": [(pair, t0, t1, dmax)]})
    ref = episodes[0]["dmax"] if episodes else 0.0
    majors = [ep for ep in episodes if ep["dmax"] >= 0.3 * ref]
    on_states = {(t, i): (th, om) for t, kind, i, th, om in run["events"] if kind == "on"}
    off_states = {(t, i): (th, om) for t, kind, i, th, om in run["events"] if kind == "off"}
    for ep in majors:
        first = min(ep["pairs"], key=lambda p: p[1])
        last = max(ep["pairs"], key=lambda p: p[2])
        ep["before"] = on_states[(first[1], first[0])]
        ep["after"] = off_states[(last[2], last[0])]
        ep["P"] = (momentum(cfg, *ep["before"]), momentum(cfg, *ep["after"]))
        ep["E"] = (energy(cfg, *ep["before"]), energy(cfg, *ep["after"]))
        ep["v_out"] = [L * w for w in ep["after"][1]]
    # Peaks of every ball between consecutive major clicks (height in cm, signed by side).
    turns = sorted(run["turns"])
    for j, ep in enumerate(majors):
        lo = ep["t1"]
        hi = majors[j + 1]["t0"] if j + 1 < len(majors) else math.inf
        right = [0.0] * N
        left = [0.0] * N
        for t, i, a in turns:
            if lo <= t <= hi:
                hcm = 100.0 * L * (1.0 - math.cos(a))
                if a > 0:
                    right[i] = max(right[i], hcm)
                else:
                    left[i] = max(left[i], hcm)
        ep["right"] = right
        ep["left"] = left
        ep["out"] = [i for i in range(N) if right[i] > thr_cm]
        ep["back"] = [i for i in range(N) if left[i] > thr_cm]
    return {"episodes": episodes, "majors": majors}


def peak_times(run: dict, ball: int, side: int, min_cm: float) -> list[tuple[float, float]]:
    L = run["cfg"]["L"]
    out = []
    for t, i, a in sorted(run["turns"]):
        hcm = 100.0 * L * (1.0 - math.cos(a))
        if i == ball and hcm >= min_cm and (a > 0) == (side > 0):
            out.append((t, hcm))
    return out


def fmt_list(vals, nd: int = 2, unit: str = "") -> str:
    return ", ".join(f"{v:.{nd}f}{unit}" for v in vals)


def measure(man: dict) -> dict:
    g, L, r = man["g"], man["string_length_m"], man["ball_radius_m"]
    m, k, gap, h = ball_mass(man), man["hertz_k"], man["gap_m"], man["lift_m"]
    dt, sub = man["dt"], man["contact_substeps"]
    t_rel, dur = man["release_t"], man["scene_duration"]
    thr = man["out_threshold_cm"]
    sim_dur = dur - t_rel + 0.1
    v0 = math.sqrt(2.0 * g * h)
    th0 = math.degrees(math.acos(1.0 - h / L))
    k_real = hertz_real(man)
    d_soft, t_soft = contact_closed_form(m, k, v0)
    d_real, t_real = contact_closed_form(m, k_real, v0)
    print(f"setup: five steel balls of radius {r * 100:g} cm (density {man['steel_density_kg_m3']:g} kg/m^3, mass "
          f"{m * 1000:.1f} g each) on strings of {L:g} m from pivots {2 * r * 1000 + gap * 1000:g} mm apart, so the balls "
          f"hang {gap * 1000:g} mm apart at rest; exact pendulums with a Hertz contact F = k delta^1.5 between "
          f"neighbours, k = {k:.3g} N/m^1.5, softened from real steel (E = {man['young_modulus_pa'] / 1e9:g} GPa, nu = "
          f"{man['poisson_ratio']:g}: k = {k_real:.3g}, a factor {k_real / k:.0f}) so that a click lasts {t_soft * 1000:.2f} ms "
          f"with {d_soft * 1e6:.0f} microns of squash instead of {t_real * 1e6:.0f} microseconds and {d_real * 1e6:.0f} microns; "
          f"g = {g:g} m/s^2; top cradle: ball 1 lifted so its centre is {h * 100:g} cm above rest ({th0:.2f} degrees), bottom "
          f"cradle: balls 1 and 2 lifted together to the same height; both let go at {t_rel:g} s of the video; RK4 at a base "
          f"step of {dt:.0e} s ({t_soft / dt:.0f} steps per click) cut into {sub} sub-steps while any pair touches, with "
          f"a geometric ramp of tiny steps at every contact onset and offset; {sim_dur:g} s simulated for the {dur:g} s scene; "
          f"deterministic, no seed")
    T_small = 2.0 * math.pi * math.sqrt(L / g)
    T_amp = pendulum_period(L, g, math.radians(th0))
    print(f"closed forms: speed at the bottom sqrt(2 g h) = {v0:.4f} m/s; one ball at double speed would rise "
          f"4 h = {4 * h * 100:g} cm (above the pivots, the strings are {L * 100:g} cm) and carry twice the energy of two "
          f"balls at {v0:.2f} m/s (momentum the same); swing period {T_small:.4f} s at small angles and {T_amp:.4f} s at "
          f"{th0:.1f} degrees, so a click every {T_amp / 2:.4f} s; energy lifted: {m * g * h * 1000:.2f} mJ per ball")

    jobs = {
        "one": cfg_for(man, 1, sim_dur),
        "two": cfg_for(man, 2, sim_dur),
        "one_half": cfg_for(man, 1, man["check_duration"], dt=dt / 2),
        "two_half": cfg_for(man, 2, man["check_duration"], dt=dt / 2),
        "two_stiff": cfg_for(man, 2, man["short_check_duration"], dt=dt / 4, k=10.0 * k),
        "one_nogap": cfg_for(man, 1, man["short_check_duration"], gap=0.0),
        "two_nogap": cfg_for(man, 2, man["short_check_duration"], gap=0.0),
    }
    with ProcessPoolExecutor(max_workers=len(jobs)) as pool:
        futures = {name: pool.submit(simulate, cfg) for name, cfg in jobs.items()}
        runs = {name: fut.result() for name, fut in futures.items()}
    out = {"runs": runs, "t_rel": t_rel}
    for name in ("one", "two"):
        run = runs[name]
        an = analyse(run, thr)
        run["an"] = an
        majors = an["majors"]
        first = majors[0]
        lifted = jobs[name]["lifted"]
        v_in = L * first["before"][1][lifted - 1]
        pairs = sorted(first["pairs"], key=lambda p: p[1])
        print(f"{name} lifted, first click: contact begins at {t_rel + first['t0']:.4f} s of the video "
              f"({first['t0']:.4f} s after release), the incoming ball at {v_in:.4f} m/s against sqrt(2 g h) = "
              f"{v0:.4f}; contacts " + "; ".join(f"{p[0] + 1}-{p[0] + 2} {1000 * (p[2] - p[1]):.2f} ms" for p in pairs) +
              f"; the click is over at {t_rel + first['t1']:.4f} s ({1000 * (first['t1'] - first['t0']):.2f} ms); "
              f"outgoing speeds (m/s, + to the far side) balls 1..5: {fmt_list(first['v_out'], 4)}; peak rise after "
              f"the click (cm) balls 1..5: far side {fmt_list(first['right'], 3)}, near side {fmt_list(first['left'], 3)}; "
              f"balls out the far side (peak over {thr:g} cm): {len(first['out'])} ({', '.join(str(i + 1) for i in first['out'])}); "
              f"closed form v^2 / (2 g) for the far balls: " +
              ", ".join(f"ball {i + 1} {100 * first['v_out'][i] ** 2 / (2 * g):.3f} cm" for i in first["out"]))
        second = majors[1]
        print(f"{name} lifted, second click at {t_rel + second['t0']:.4f} s: back out the near side "
              f"{len(second['back'])} ball(s) ({', '.join(str(i + 1) for i in second['back'])}) to "
              f"{fmt_list([second['left'][i] for i in second['back']], 3)} cm; the far balls after this click rise at most "
              f"{max(second['right']):.3f} cm")
        lines = []
        for j, ep in enumerate(majors[:4]):
            P0, P1 = ep["P"]
            E0, E1 = ep["E"]
            lines.append(f"click {j + 1} at {t_rel + ep['t0']:.3f} s: momentum {P0:.6f} -> {P1:.6f} kg m/s "
                         f"({(P1 - P0) / abs(P0):+.1e}), energy {E0 * 1000:.6f} -> {E1 * 1000:.6f} mJ ({(E1 - E0) / E0:+.1e})")
        dP = max(abs((ep["P"][1] - ep["P"][0]) / ep["P"][0]) for ep in majors)
        dE = max(abs((ep["E"][1] - ep["E"][0]) / ep["E"][0]) for ep in majors)
        e = energy_series(run)
        drift = float(np.abs(e - e[0]).max() / e[0])
        print(f"{name} lifted, conservation: " + "; ".join(lines) + f"; over all {len(majors)} major clicks the momentum "
              f"changes by at most {dP:.1e} across a click and the energy by at most {dE:.1e}; relative energy drift "
              f"over the whole run {drift:.1e} (momentum is not conserved exactly: a click spans the gap crossings, and "
              f"while it lasts the strings of balls that sit a gap short of their rest points pull sideways)")
        cadence = np.diff([ep["t0"] for ep in majors])
        far = N - 1
        pk_far = peak_times(run, far, +1, thr)
        pk_near = peak_times(run, 0, -1, thr)
        period = np.diff([t for t, _ in pk_near])
        rest = [b for b in range(N) if b >= lifted and b not in first["out"]]
        th_rest = run["th"][:, rest]
        sway = float(np.degrees(np.abs(th_rest).max()))
        rise_rest = 100.0 * L * (1.0 - math.cos(math.radians(sway)))
        lo_far = min(pk_far, key=lambda p: p[1])
        hi_far = max(pk_far, key=lambda p: p[1])
        print(f"{name} lifted, rhythm: {len(majors)} major clicks in {sim_dur:g} s, one every {cadence.mean():.4f} s "
              f"(first three {fmt_list(cadence[:3], 4)}); ball 1 peaks on the near side every {period.mean():.4f} s "
              f"(closed form {T_amp:.4f}); ball {far + 1}'s far-side peak over the run ranges {lo_far[1]:.2f} cm (at "
              f"{t_rel + lo_far[0]:.1f} s of the video) to {hi_far[1]:.2f} cm (at {t_rel + hi_far[0]:.1f} s) and ball 1's "
              f"near-side peak {min(p for _, p in pk_near):.2f} to {max(p for _, p in pk_near):.2f} cm, a slow beat as the "
              f"balls that stay swing at their own small-angle period against the click cadence; the balls that stay ({', '.join(str(b + 1) for b in rest)}) sway at most "
              f"{sway:.2f} degrees ({rise_rest:.3f} cm of rise) over the run, kicked a gap's width at every click; minor "
              f"contacts (under 0.3 of the first click's squash): {len(an['episodes']) - len(majors)}")
        # End of the scene against the first frame.
        i_end = int(round((dur - t_rel) / run["store_dt"]))
        th_end = run["th"][i_end]
        om_end = run["om"][i_end]
        last_near = pk_near[-1]
        ppm = man["px_per_m"]
        dx = [ppm * L * (math.sin(th_end[i]) - math.sin(run["th"][0][i])) for i in range(N)]
        dy = [ppm * L * (math.cos(run["th"][0][i]) - math.cos(th_end[i])) for i in range(N)]
        print(f"{name} lifted, loop: ball 1's last near-side peak is {last_near[1]:.2f} cm at {t_rel + last_near[0]:.3f} s of "
              f"the video; at {dur:g} s the balls are at " +
              ", ".join(f"{math.degrees(a):+.1f} deg" for a in th_end) + " moving at " +
              ", ".join(f"{L * w:+.2f} m/s" for w in om_end) +
              f"; the lifted balls sit {max(abs(v) for v in dx[:lifted]):.0f} px sideways and "
              f"{max(abs(v) for v in dy[:lifted]):.0f} px vertically from their first-frame spots; the {man['loop_fade']:g} s "
              f"loop fade covers the difference")
        out[name + "_first"] = first
        out[name + "_peak"] = max(first["right"])
    # Checks.
    for name in ("one", "two"):
        full = runs[name]["an"]["majors"][0]
        half = analyse(runs[name + "_half"], thr)["majors"][0]
        print(f"check at half the step ({name} lifted, dt = {dt / 2:.1e} s): far-side peaks balls 1..5 "
              f"{fmt_list(half['right'], 4)} cm against {fmt_list(full['right'], 4)} at the full step; outgoing speeds "
              f"{fmt_list(half['v_out'], 5)} against {fmt_list(full['v_out'], 5)}")
    stiff = analyse(runs["two_stiff"], thr)["majors"][0]
    full = runs["two"]["an"]["majors"][0]
    d_stiff, t_stiff = contact_closed_form(m, 10.0 * k, v0)
    print(f"check at ten times the stiffness (two lifted, k = {10 * k:.3g}, a click of {t_stiff * 1000:.2f} ms): far-side "
          f"peaks balls 1..5 {fmt_list(stiff['right'], 4)} cm against {fmt_list(full['right'], 4)}; balls out "
          f"{len(stiff['out'])}")
    for name in ("one", "two"):
        ng = analyse(runs[name + "_nogap"], thr)["majors"][0]
        print(f"check with no gap at all ({name} lifted, balls touching exactly, not drawn): the whole chain squeezes as one "
              f"from {ng['t0']:.4f} to {ng['t1']:.4f} s after release; far-side peaks balls 1..5 {fmt_list(ng['right'], 3)} cm, "
              f"near-side {fmt_list(ng['left'], 3)}; balls out {len(ng['out'])}; energy {ng['E'][0] * 1000:.4f} -> "
              f"{ng['E'][1] * 1000:.4f} mJ, momentum {ng['P'][0]:.5f} -> {ng['P'][1]:.5f} kg m/s")
    return out


class Renderer:
    def __init__(self, man: dict, meas: dict):
        self.man, self.meas = man, meas
        self.fps = man["fps"]
        font = os.environ["SEED_ZERO_FONT"]
        self.font = ImageFont.truetype(font, 40)
        self.font_title = ImageFont.truetype(font, 56)
        self.font_read = ImageFont.truetype(font, 36)
        self.font_num = ImageFont.truetype(font, 48)
        self.font_small = ImageFont.truetype(font, 28)
        self.font_status = ImageFont.truetype(font, 32)
        self.first = None
        self.ppm = float(man["px_per_m"])
        self.L = man["string_length_m"] * self.ppm
        self.r = man["ball_radius_m"] * self.ppm
        self.pitch = (2.0 * man["ball_radius_m"] + man["gap_m"]) * self.ppm
        self.lift_px = man["lift_m"] * self.ppm
        self.t_rel = man["release_t"]
        self.reads = {p["name"]: self.readouts(meas["runs"][p["name"]]) for p in PANELS}
        widths = {"overlay@34": (ImageFont.truetype(font, 34), man["overlay"])}
        for j, line in enumerate(man["title"].split("|")):
            widths[f"title line {j + 1}@56"] = (self.font_title, line)
        for p in PANELS:
            widths[f"label {p['name']}@40"] = (self.font, p["label"])
        widths["sublabel@28"] = (self.font_small, f"lifted {man['lift_m'] * 100:g} cm, then let go")
        widths["readout label@28"] = (self.font_small, "balls out")
        widths["readout count@48"] = (self.font_num, "2")
        widths["readout peak@36"] = (self.font_read, "to 10 cm")
        widths["click@32"] = (self.font_status, "click")
        widths["ruler@28"] = (self.font_small, "10 cm")
        for j, line in enumerate(self.payoff_lines()):
            widths[f"payoff line {j + 1}@40"] = (self.font, line)
        print("text widths: " + ", ".join(f"{k} {f.getlength(s):.0f} px" for k, (f, s) in widths.items()))
        one, two = meas["one_first"], meas["two_first"]
        print(f"video: real time, {man['scene_duration']:g} s; balls held until {self.t_rel:g} s; first clicks at "
              f"{self.t_rel + one['t0']:.2f} s (one lifted) and {self.t_rel + two['t0']:.2f} s (two lifted), far-side peaks "
              f"at about {self.t_rel + one['t1'] + 0.29:.2f} s; payoff card at {man['payoff_t']:g} s; strings {self.L:.0f} px, "
              f"balls {2 * self.r:.1f} px across, {man['gap_m'] * self.ppm:.1f} px apart, {man['lift_m'] * 100:g} cm = "
              f"{self.lift_px:.0f} px")

    def payoff_lines(self) -> list[str]:
        text = self.man["payoff_text"].format(one=self.meas["one_peak"], two=self.meas["two_peak"])
        return [s.strip() for s in text.split("|")]

    def readouts(self, run: dict) -> dict:
        """Per sample: balls out and peak so far on the far side, reset at every major click that sends balls out."""
        man = self.man
        L = run["cfg"]["L"]
        thr = man["out_threshold_cm"]
        th = run["th"]
        n = th.shape[0]
        hcm = 100.0 * L * (1.0 - np.cos(th))
        right = np.where(th > 0.0, hcm, 0.0)
        majors = run["an"]["majors"]
        bounds = [0] + [min(n, int(math.ceil(ep["t1"] / run["store_dt"]))) for ep in majors] + [n]
        count = np.zeros(n, dtype=int)
        peak = np.zeros(n)
        marks = np.zeros((n, N))
        live = np.zeros(n, dtype=bool)
        last_c, last_p, last_m = 0, 0.0, np.zeros(N)
        for a, b in zip(bounds[:-1], bounds[1:]):
            if b <= a:
                continue
            rm = np.maximum.accumulate(right[a:b], axis=0)
            if a > 0 and rm[-1].max() > 0.5:
                count[a:b] = (rm > thr).sum(axis=1)
                peak[a:b] = rm.max(axis=1)
                marks[a:b] = rm
                live[a:b] = True
                last_c, last_p, last_m = int(count[b - 1]), float(peak[b - 1]), rm[-1].copy()
            else:
                count[a:b] = last_c
                peak[a:b] = last_p
                marks[a:b] = last_m
        clicks = [ep["t0"] for ep in majors]
        return {"count": count, "peak": peak, "marks": marks, "live": live, "clicks": clicks}

    def sample(self, run: dict, t: float) -> tuple[np.ndarray, int]:
        """Angles at video time t (linear between stored samples) and the nearest sample index."""
        tau = max(0.0, t - self.t_rel) / run["store_dt"]
        i0 = min(int(tau), run["th"].shape[0] - 1)
        i1 = min(i0 + 1, run["th"].shape[0] - 1)
        f = tau - i0
        return run["th"][i0] * (1.0 - f) + run["th"][i1] * f, min(int(round(tau)), run["th"].shape[0] - 1)

    def draw_cradle(self, d: ImageDraw.ImageDraw, p: dict, th: np.ndarray) -> None:
        """Geometry layer (supersampled): pivot bar, strings, balls, the 10 cm level and the ruler."""
        top = (p["top"] - GEOM_Y0) * SS
        y_piv = top + PIVOT_DY * SS
        L, r = self.L * SS, self.r * SS
        y_rest = y_piv + L
        xs = [CRADLE_CX * SS + (i - 2) * self.pitch * SS for i in range(N)]
        # 10 cm level line, dashed, and the ruler.
        y10 = y_rest - self.lift_px * SS
        x = 60 * SS
        while x < (RULER_X - 16) * SS:
            d.line((x, y10, min(x + 12 * SS, (RULER_X - 16) * SS), y10), fill=blend(TEXT, 0.22), width=SS)
            x += 24 * SS
        rx = RULER_X * SS
        d.line((rx, y_rest, rx, y10), fill=BEAM, width=2 * SS)
        for cm in (0, 5, 10):
            yy = y_rest - cm / 100.0 * self.ppm * SS
            d.line((rx - 14 * SS, yy, rx, yy), fill=BEAM, width=2 * SS)
        # Pivot bar.
        d.rectangle((xs[0] - 60 * SS, y_piv - 5 * SS, xs[-1] + 60 * SS, y_piv + 5 * SS), fill=BEAM)
        balls = []
        for i in range(N):
            bx = xs[i] + L * math.sin(th[i])
            by = y_piv + L * math.cos(th[i])
            balls.append((bx, by))
            d.line((xs[i], y_piv, bx, by), fill=STRING, width=2 * SS)
            d.ellipse((xs[i] - 5 * SS, y_piv - 5 * SS, xs[i] + 5 * SS, y_piv + 5 * SS), fill=WIRE)
        for i, (bx, by) in enumerate(balls):
            lifted = i < p["lifted"]
            fill = p["colour"] if lifted else STEEL
            edge = p["edge"] if lifted else STEEL_EDGE
            d.ellipse((bx - r, by - r, bx + r, by + r), fill=fill, outline=edge, width=SS)
            hr = r * 0.3
            d.ellipse((bx - r * 0.42 - hr, by - r * 0.42 - hr, bx - r * 0.42 + hr, by - r * 0.42 + hr), fill=WHITE)

    def draw_marks(self, d: ImageDraw.ImageDraw, p: dict, marks: np.ndarray, live: bool) -> None:
        top = p["top"]
        y_rest = top + PIVOT_DY + self.L
        col = p["colour"] if live else blend(p["colour"], 0.55)
        for i in range(N):
            if marks[i] > 0.05:
                yy = y_rest - marks[i] / 100.0 * self.ppm
                d.line((RULER_X - 40, yy, RULER_X + 6, yy), fill=col, width=4)

    def draw_scene(self, t: float) -> Image.Image:
        man = self.man
        img = Image.new("RGB", (W, H), BG)
        layer = Image.new("RGB", (W * SS, (GEOM_Y1 - GEOM_Y0) * SS), BG)
        ld = ImageDraw.Draw(layer)
        state = {}
        for p in PANELS:
            run = self.meas["runs"][p["name"]]
            th, idx = self.sample(run, t)
            state[p["name"]] = (th, idx)
            self.draw_cradle(ld, p, th)
        img.paste(layer.reduce(SS), (0, GEOM_Y0))
        d = ImageDraw.Draw(img)
        for p in PANELS:
            top = p["top"]
            col = p["colour"]
            th, idx = state[p["name"]]
            rd = self.reads[p["name"]]
            y_rest = top + PIVOT_DY + self.L
            d.text((40, top + 20), p["label"], font=self.font, fill=col, anchor="lm")
            d.text((40, top + 62), f"lifted {man['lift_m'] * 100:g} cm, then let go", font=self.font_small, fill=MUTED, anchor="lm")
            d.text((RULER_X, y_rest - self.lift_px - 10), f"{man['lift_m'] * 100:g} cm", font=self.font_small, fill=MUTED, anchor="mb")
            count, peak, live = int(rd["count"][idx]), float(rd["peak"][idx]), bool(rd["live"][idx])
            d.text((W - 40, top + 16), "balls out", font=self.font_small, fill=MUTED, anchor="rm")
            d.text((W - 40, top + 64), f"{count}", font=self.font_num, fill=col if count > 0 else TEXT, anchor="rm")
            if peak > 0.05:
                d.text((W - 40, top + 112), f"to {peak:.0f} cm", font=self.font_read,
                       fill=TEXT if live else MUTED, anchor="rm")
            tau = t - self.t_rel
            if any(0.0 <= tau - c < 0.25 for c in rd["clicks"]):
                d.text((W - 40, top + 156), "click", font=self.font_status, fill=col, anchor="rm")
            self.draw_marks(d, p, rd["marks"][idx], live)
        return img

    def live_frame(self, f: int) -> np.ndarray:
        man = self.man
        t = f / self.fps
        img = self.draw_scene(t)
        d = ImageDraw.Draw(img)
        if t < man["title_until"]:
            a = 1.0 if t < man["title_until"] - 0.4 else (man["title_until"] - t) / 0.4
            for j, line in enumerate(man["title"].split("|")):
                d.text((W / 2, 190 + j * 62), line, font=self.font_title, fill=blend(TEXT, a), anchor="mm")
        if t >= man["payoff_t"]:
            a = min(1.0, (t - man["payoff_t"]) / man["payoff_hold"])
            for j, line in enumerate(self.payoff_lines()):
                d.text((W / 2, PAYOFF_Y + j * 56), line, font=self.font, fill=blend(GOLD, a), anchor="mm")
        return np.asarray(img, dtype=np.float32)

    def frame_at(self, f: int) -> np.ndarray:
        man = self.man
        total = int(round(man["scene_duration"] * self.fps))
        live = self.live_frame(f)
        fade_frames = int(round(man["loop_fade"] * self.fps))
        if f >= total - fade_frames:
            if self.first is None:
                self.first = self.live_frame(0)
            a = (f - (total - fade_frames) + 1) / fade_frames
            live = live * (1 - a) + self.first * a
        return live.astype(np.uint8)

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
    man = json.loads((ROOT / "projects/cradle/manifest.json").read_text())
    meas = measure(man)
    if "--measure-only" in sys.argv:
        return
    if "--frames" in sys.argv:
        times = [float(v) for v in sys.argv[sys.argv.index("--frames") + 1].split(",")]
        r = Renderer(man, meas)
        for tv in times:
            Image.fromarray(r.frame_at(int(round(tv * man["fps"])))).save(ROOT / f"media/cradle/smoke-{tv}.png")
        print("smoke frames: " + ", ".join(f"{tv}" for tv in times))
        return
    Renderer(man, meas).render(ROOT / "media/cradle/footage.mp4")


if __name__ == "__main__":
    main()

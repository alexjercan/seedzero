import contextlib
import importlib.machinery
import importlib.util
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT = Path(__file__).with_name("captions.py")
LOADER = importlib.machinery.SourceFileLoader("captions", str(SCRIPT))
SPEC = importlib.util.spec_from_loader("captions", LOADER)
MODULE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(MODULE)

FONT = {"SEED_ZERO_FONT": "/fonts/test.ttf"}


def run_main(*args):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.dict(os.environ, FONT), mock.patch.object(sys, "argv", ["captions.py", *args]), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        MODULE.main()
    return out.getvalue(), err.getvalue()


def enables(filter_text):
    return [line.split("enable='")[1].rstrip("',\n") for line in filter_text.splitlines()[1:]]


class BoundariesTest(unittest.TestCase):
    def test_marks_after_quotes_and_brackets_count(self):
        words = 'Wall ahead. "Brake," or (swerve?) no: yes; end.'.split()
        self.assertEqual(MODULE.boundaries(words), [1, 2, 4, 5, 6])

    def test_last_word_is_not_a_boundary(self):
        self.assertEqual(MODULE.boundaries(["One", "two."]), [])


class SplitSilencesTest(unittest.TestCase):
    def test_leading_trailing_and_interior(self):
        start, end, interior = MODULE.split_silences(
            [0.0, 1.0, 4.9], [0.4, 1.3], 5.0)
        self.assertEqual((start, end), (0.4, 4.9))
        self.assertEqual(interior, [(1.0, 1.3)])

    def test_trailing_silence_that_ends_at_the_duration(self):
        start, end, interior = MODULE.split_silences([2.0, 4.8], [2.2, 5.0], 5.0)
        self.assertEqual((start, end), (0.0, 4.8))
        self.assertEqual(interior, [(2.0, 2.2)])


class AlignTest(unittest.TestCase):
    # 30 words at 0.25 s each; pauses after words 4, 14 and 24; one
    # spurious pause inside words 5..14; boundaries also after 9 and 19.
    BOUNDS = [4, 9, 14, 19, 24]
    PAUSES = [(1.25, 1.55), (2.30, 2.45), (4.20, 4.50), (7.00, 7.30)]

    def test_skips_a_spurious_pause_and_unused_boundaries(self):
        pairs = MODULE.align(self.BOUNDS, self.PAUSES, 30, 0.0, 8.55)
        self.assertEqual(pairs, [(0, 0), (2, 2), (3, 4)])

    def test_result_is_monotone(self):
        pairs = MODULE.align(self.BOUNDS, self.PAUSES, 30, 0.0, 8.55)
        for (i0, j0), (i1, j1) in zip(pairs, pairs[1:]):
            self.assertLess(i0, i1)
            self.assertLess(j0, j1)

    def test_more_pauses_than_boundaries(self):
        pauses = [(1.25, 1.5), (2.0, 2.2), (2.5, 2.7)]
        pairs = MODULE.align([4], pauses, 10, 0.0, 3.15)
        self.assertEqual(pairs, [(0, 0)])

    def test_nothing_to_match(self):
        self.assertEqual(MODULE.align([], [(1.0, 1.2)], 10, 0.0, 3.0), [])
        self.assertEqual(MODULE.align([4], [], 10, 0.0, 3.0), [])


class WordStartsTest(unittest.TestCase):
    def test_piecewise_linear_between_anchors(self):
        starts = MODULE.word_starts(10, [4], [(1.0, 1.5)], [(0, 0)], 0.0, 2.5)
        expected = [0.0, 0.2, 0.4, 0.6, 0.8, 1.5, 1.7, 1.9, 2.1, 2.3]
        for got, want in zip(starts, expected):
            self.assertAlmostEqual(got, want)

    def test_unmatched_pause_spreads_words_over_it(self):
        starts = MODULE.word_starts(4, [], [(1.0, 1.4)], [], 0.2, 3.0)
        for got, want in zip(starts, [0.2, 0.9, 1.6, 2.3]):
            self.assertAlmostEqual(got, want)


class MainTest(unittest.TestCase):
    NARRATION = "One two. Three four five. Six seven eight nine.\n"

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.narration = os.path.join(temporary.name, "narration.txt")
        with open(self.narration, "w") as handle:
            handle.write(self.NARRATION)
        self.args = (self.narration, "5.0", "0.6", "seed: 1, x", "0.75")

    def test_word_count_timing_without_voice(self):
        out, err = run_main(*self.args)
        self.assertEqual(err, "")
        self.assertEqual(enables(out), [
            "between(t,0.600,1.711)", "between(t,1.711,3.378)",
            "between(t,3.378,5.044)", "between(t,5.044,5.600)"])
        self.assertIn("text='seed\\: 1\\, x'", out.splitlines()[0])
        self.assertIn("y=h*0.750", out)

    def test_voice_aligns_chunks_to_pause_ends(self):
        # 0.4 s a word: speech 0.4..1.2, pause, 1.5..2.7, pause, 3.0..4.6
        silences = ([0.0, 1.2, 2.7, 4.6], [0.4, 1.5, 3.0])
        with mock.patch.object(MODULE, "detect_silences", return_value=silences) as detect:
            out, err = run_main("--voice", "v.wav", *self.args)
        detect.assert_called_once_with("v.wav")
        self.assertEqual(enables(out), [
            "between(t,1.000,2.100)", "between(t,2.100,3.600)",
            "between(t,3.600,4.800)", "between(t,4.800,5.600)"])
        self.assertEqual(err.count("\n"), 1)
        self.assertIn("2 pauses detected, 2 matched", err)
        self.assertIn("max chunk start shift 0.400 s", err)

    def test_voice_flag_with_equals_sign_after_positionals(self):
        # 0.45 s a word: speech 0..0.9, pause, 1.2..2.55, pause, 2.85..4.65
        silences = ([0.9, 2.55, 4.65], [1.2, 2.85])
        with mock.patch.object(MODULE, "detect_silences", return_value=silences):
            out, _ = run_main(*self.args, "--voice=v.wav")
        self.assertEqual(enables(out)[:2], ["between(t,0.600,1.800)", "between(t,1.800,3.450)"])

    def test_fallback_when_ffmpeg_fails(self):
        plain, _ = run_main(*self.args)
        with mock.patch.object(MODULE.subprocess, "run", side_effect=OSError):
            out, err = run_main("--voice", "missing.wav", *self.args)
        self.assertEqual(out, plain)
        self.assertEqual(err, "captions: word-count timing (ffmpeg silencedetect failed)\n")

    def test_fallback_without_interior_pause(self):
        plain, _ = run_main(*self.args)
        with mock.patch.object(MODULE, "detect_silences", return_value=([0.0, 4.9], [0.4])):
            out, err = run_main("--voice", "v.wav", *self.args)
        self.assertEqual(out, plain)
        self.assertEqual(err, "captions: word-count timing (no interior pause found)\n")

    def test_fallback_when_no_boundary_exists(self):
        with open(self.narration, "w") as handle:
            handle.write("One two three four five\n")
        plain, _ = run_main(*self.args)
        with mock.patch.object(MODULE, "detect_silences", return_value=([1.0], [1.3])):
            out, err = run_main("--voice", "v.wav", *self.args)
        self.assertEqual(out, plain)
        self.assertEqual(err, "captions: word-count timing (no pause matched a text boundary)\n")


if __name__ == "__main__":
    unittest.main()

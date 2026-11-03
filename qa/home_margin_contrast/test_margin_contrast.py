"""Offline-only guard for the proposed FV margin rotator contrast candidate.

No network requests, no WordPress writes. Never interpret these tests as hosted WCAG PASS.
"""
from __future__ import annotations

import pathlib
import re
import unittest

CSS = pathlib.Path(__file__).with_name("margin_strip_candidate.css")


def rgb(hex_string: str) -> tuple[float, float, float]:
    h = hex_string.removeprefix("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(c: tuple[float, float, float]) -> float:
    channels = []
    for n in c:
        s = n / 255.0
        channels.append(s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def ratio(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    x, y = sorted((luminance(a), luminance(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def blend(fg: tuple[float, float, float], bg: tuple[float, float, float], opacity: float) -> tuple[float, float, float]:
    return tuple(fg[i] * opacity + bg[i] * (1 - opacity) for i in range(3))


def keyframes(css: str) -> dict[float, tuple[float, str]]:
    m = re.search(r"@keyframes\s+fvMarginRevealAccessible\s*\{(?P<body>.*?)\n\}", css, re.S)
    if not m:
        return {}
    out: dict[float, tuple[float, str]] = {}
    for pct, body in re.findall(r"([\d.]+)%\s*\{([^{}]*)\}", m["body"]):
        alpha = re.search(r"\bopacity\s*:\s*([\d.]+)", body)
        visibility = re.search(r"\bvisibility\s*:\s*(hidden|visible)", body)
        if alpha and visibility:
            out[float(pct)] = (float(alpha.group(1)), visibility.group(1))
    return out


class MarginContrastContract(unittest.TestCase):
    def setUp(self) -> None:
        self.css = CSS.read_text()

    def test_candidate_is_scoped_to_rotator(self) -> None:
        self.assertIn(".fv-margin-strip--rotator .fv-margin-strip__item", self.css)
        self.assertNotIn(".fv-hf", self.css)

    def test_discrete_animation_avoids_fractional_opacity(self) -> None:
        self.assertRegex(self.css, r"360s\s+steps\(1,\s*end\)\s+infinite")
        stops = keyframes(self.css)
        self.assertEqual(len(stops), 5)
        self.assertEqual(sorted(stops), [0.0, 0.02, 1.36, 1.38, 100.0])
        for pct, (alpha, visibility) in stops.items():
            self.assertIn(alpha, (0.0, 1.0), str(pct))
            self.assertEqual(visibility, "visible" if alpha == 1 else "hidden")

    def test_cadence_has_no_long_crossfade(self) -> None:
        self.assertIn("var(--i) * 5s", self.css)
        self.assertEqual(360 / 5, 72)

    def test_visible_color_exceeds_4_5(self) -> None:
        foreground, background = rgb("#d8d2c7"), rgb("#0f100f")
        self.assertGreaterEqual(ratio(foreground, background), 4.5)

    def test_previous_partial_alpha_is_below_4_5(self) -> None:
        foreground, background = rgb("#d8d2c7"), rgb("#0f100f")
        for alpha in (0.42, 0.46):
            self.assertLess(ratio(blend(foreground, background, alpha), background), 4.5)

    def test_blur_is_not_applied_to_visible_text(self) -> None:
        self.assertRegex(self.css, r"filter\s*:\s*none")
        self.assertNotIn("blur(", self.css)

    def test_reduced_motion_does_not_animate(self) -> None:
        m = re.search(r"@media\s*\(prefers-reduced-motion:\s*reduce\)(.*)", self.css, re.S)
        self.assertIsNotNone(m)
        self.assertIn("animation: none", m.group(1))
        self.assertIn("nth-child(1)", m.group(1))

    def test_no_wordpress_or_network_calls(self) -> None:
        self.assertNotRegex(self.css, r"https?://|@import|url\s*\(")

    def test_opacity_regression_mutation_is_detected(self) -> None:
        changed = self.css.replace("opacity: 1; visibility: visible", "opacity: .46; visibility: visible", 1)
        stops = keyframes(changed)
        self.assertTrue(any(0 < a < 1 for a, _ in stops.values()))

    def test_animation_timing_regression_mutation_is_detected(self) -> None:
        bad = self.css.replace("steps(1, end)", "linear")
        self.assertNotRegex(bad, r"360s\s+steps\(1,\s*end\)\s+infinite")


if __name__ == "__main__":
    unittest.main()

"""BTC close 240 minutes ahead: mean-reverting median pull.

Scoring is mean absolute error, so the forecast should be the median
of the future price, not the last print. Across the practice window
(54 checkpoints cut from the kit's six cases) the last close drifts
back toward its 24-hour median over four hours: pulling the last
close 40% of the way toward the median of the last 1440 closes
scored MAE $401 vs $506 for persistence alone. The 0.6 weight left
on the last close bounds the damage when the final move is a genuine
trend rather than noise. Cases with fewer than 60 closes in the
window fall back to the last close unchanged.

Standard library only, offline, deterministic.
"""

import json
import os
import sys
from pathlib import Path

REVERSION = 0.4
LOOKBACK = 1440
MIN_VALID = 60
LOW = 0.00001
HIGH = 9999999.99999


def middle(values):
    ordered = sorted(values)
    n = len(ordered)
    half = n // 2
    if n % 2 == 1:
        return ordered[half]
    return (ordered[half - 1] + ordered[half]) / 2.0


def forecast(prices):
    latest = prices[-1]
    window = prices[-LOOKBACK:]
    if len(window) < MIN_VALID:
        return latest
    centre = middle(window)
    value = latest + REVERSION * (centre - latest)
    value = max(LOW, min(HIGH, value))
    return round(value, 5) + 0.0


def process(input_dir, output_dir):
    dest = Path(output_dir)
    dest.mkdir(parents=True, exist_ok=True)
    for src in sorted(Path(input_dir).glob("*.in")):
        case = json.loads(src.read_text())
        price = forecast(case["markets"][0]["prices"])
        result = {"forecasts": [{"case": case["case"], "price": price}]}
        (dest / (src.stem + ".out")).write_text(json.dumps(result) + "\n")


def main():
    process(
        os.environ.get("MAKEFUN_INPUT_DIR", "/input"),
        os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

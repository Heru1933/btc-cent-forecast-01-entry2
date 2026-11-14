"""BTC close, 240 minutes ahead.

The score is mean absolute error, so the forecast should be the median
of the future price, not the last print. Across the practice window
(54 checkpoints cut from the kit's six cases) the last close drifts
back toward its 24-hour median over four hours: pulling the last close
40% of the way toward the median of the last 1440 closes scored
MAE $401 against $506 for persistence alone. The 0.6 weight left on
the last close bounds the damage when the final move is a genuine
trend rather than noise. Cases with fewer than 60 closes in the
window fall back to the last close unchanged.

Standard library only, offline, deterministic.
"""

import json
import os
import sys
from pathlib import Path

PULL = 0.4
WINDOW = 1440
MIN_CLOSES = 60
LOW = 0.00001
HIGH = 9999999.99999


def median(values):
    # Even-length windows average the two middle closes; that keeps the
    # centre stable when the window straddles a sharp move.
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def forecast(prices):
    last = prices[-1]
    window = prices[-WINDOW:]
    if len(window) < MIN_CLOSES:
        # Too little history to trust a median: stay on the last close.
        return last
    guess = last + PULL * (median(window) - last)
    guess = max(LOW, min(HIGH, guess))
    return round(guess, 5)


def solve(input_dir, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for path in sorted(Path(input_dir).glob("*.in")):
        case = json.loads(path.read_text())
        price = forecast(case["markets"][0]["prices"])
        result = {"forecasts": [{"case": case["case"], "price": price}]}
        (out / (path.stem + ".out")).write_text(json.dumps(result) + "\n")


def main():
    solve(
        os.environ.get("MAKEFUN_INPUT_DIR", "/input"),
        os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

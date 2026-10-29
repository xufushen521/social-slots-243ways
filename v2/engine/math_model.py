from __future__ import annotations

from collections import Counter, defaultdict
from math import prod
from typing import Any


def visible_windows(preset: dict[str, Any]) -> list[list[list[str]]]:
    strips = preset["reels"]["strips"]
    rows = preset["grid"]["rows"]
    return [
        [[strip[(stop + row) % len(strip)] for row in range(rows)] for stop in range(len(strip))]
        for strip in strips
    ]


def symbol_count_distribution(
    preset: dict[str, Any],
    symbol: str,
    reel_index: int,
) -> dict[int, int]:
    windows = visible_windows(preset)[reel_index]
    distribution: Counter[int] = Counter()
    for window in windows:
        distribution[window.count(symbol)] += 1
    return dict(sorted(distribution.items()))


def mean_symbol_count(preset: dict[str, Any], symbol: str, reel_index: int) -> float:
    distribution = symbol_count_distribution(preset, symbol, reel_index)
    total = sum(distribution.values())
    return sum(count * frequency for count, frequency in distribution.items()) / total


def zero_probability(preset: dict[str, Any], symbol: str, reel_index: int) -> float:
    distribution = symbol_count_distribution(preset, symbol, reel_index)
    total = sum(distribution.values())
    return distribution.get(0, 0) / total


def ways_breakdown(preset: dict[str, Any], bet: float = 1.0) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for symbol, info in preset["symbols"].items():
        if info.get("type") != "regular":
            continue
        means = [mean_symbol_count(preset, symbol, reel) for reel in range(5)]
        zeros = [zero_probability(preset, symbol, reel) for reel in range(5)]
        pays = info["pays"]
        ways_3 = prod(means[:3]) * zeros[3]
        ways_4 = prod(means[:4]) * zeros[4]
        ways_5 = prod(means[:5])
        rtp_3 = pays["3"] * ways_3 * bet
        rtp_4 = pays["4"] * ways_4 * bet
        rtp_5 = pays["5"] * ways_5 * bet
        rows.append(
            {
                "symbol": symbol,
                "rtp_3": rtp_3,
                "rtp_4": rtp_4,
                "rtp_5": rtp_5,
                "rtp_total": rtp_3 + rtp_4 + rtp_5,
            }
        )
    return rows


def exact_ways_rtp(preset: dict[str, Any], bet: float = 1.0) -> float:
    return sum(item["rtp_total"] for item in ways_breakdown(preset, bet))


def trigger_probability(
    preset: dict[str, Any],
    symbol: str,
    min_count: int = 3,
) -> float:
    combined: dict[int, float] = {0: 1.0}
    for reel_index in range(5):
        distribution = symbol_count_distribution(preset, symbol, reel_index)
        total = sum(distribution.values())
        probabilities = {count: freq / total for count, freq in distribution.items()}
        nxt: defaultdict[int, float] = defaultdict(float)
        for current, p_current in combined.items():
            for count, p_count in probabilities.items():
                nxt[current + count] += p_current * p_count
        combined = dict(nxt)
    return sum(p for count, p in combined.items() if count >= min_count)


def base_metrics(preset: dict[str, Any], bet: float = 1.0) -> dict[str, Any]:
    ways_rtp = exact_ways_rtp(preset, bet)
    trigger_probabilities = {}
    scatter = preset.get("scatter", {})
    for key in ("respins", "free_spins"):
        block = scatter.get(key)
        if block:
            trigger_probabilities[key] = trigger_probability(
                preset, block["symbol"], block["min_count"]
            )
    return {
        "ways_rtp": ways_rtp,
        "base_rtp": ways_rtp,
        "trigger_probabilities": trigger_probabilities,
    }

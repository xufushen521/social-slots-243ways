from __future__ import annotations

import math
import random
from typing import Any

from .feature import merge_sticky, scatter_positions
from .reels import draw_grid
from .ways import count_symbol, evaluate_ways


def simulate_free_spins(
    preset: dict[str, Any],
    bet: float,
    rng: random.Random,
) -> float:
    block = preset["scatter"]["free_spins"]
    total = 0.0
    for _ in range(block["spins"]):
        grid = draw_grid(preset, rng)
        total += sum(item["win"] for item in evaluate_ways(grid, preset, bet))
    return min(total * block["multiplier"], preset.get("max_win", 5000) * bet)


def simulate_respins(
    preset: dict[str, Any],
    bet: float,
    rng: random.Random,
    trigger_grid: list[list[str]],
) -> float:
    block = preset["scatter"]["respins"]
    symbol = block["symbol"]
    sticky = scatter_positions(trigger_grid, symbol)
    left = block["awards"]["3"]
    total_awarded = left
    total = 0.0
    while left > 0:
        grid = draw_grid(preset, rng, sticky)
        total += sum(item["win"] for item in evaluate_ways(grid, preset, bet))
        sticky, new_count = merge_sticky(sticky, grid, symbol)
        if new_count:
            room = block["max_respins"] - total_awarded
            add = min(block["retrigger_add"], room)
            total_awarded += add
            left += add
        left -= 1
    return min(total, preset.get("max_win", 5000) * bet)


def simulate_preset(
    preset: dict[str, Any],
    spins: int = 1_000_000,
    bet: float = 1.0,
    seed: int = 20261023,
) -> dict[str, Any]:
    rng = random.Random(seed)
    max_win = preset.get("max_win", 5000)
    total_win = 0.0
    base_win = 0.0
    feature_win = 0.0
    sum_squares = 0.0
    hits = 0
    actual_max = 0.0
    respin_triggers = 0
    free_spin_triggers = 0
    feature_buy_total = 0.0
    feature_buy_sessions = 0

    scatter = preset.get("scatter", {})
    respins = scatter.get("respins")
    free_spins = scatter.get("free_spins")

    for _ in range(spins):
        grid = draw_grid(preset, rng)
        spin_win = sum(item["win"] for item in evaluate_ways(grid, preset, bet))
        base_win += spin_win

        sc1 = count_symbol(grid, respins["symbol"]) if respins else 0
        sc2 = count_symbol(grid, free_spins["symbol"]) if free_spins else 0

        if free_spins and sc2 >= free_spins["min_count"]:
            bonus = simulate_free_spins(preset, bet, rng)
            feature_win += bonus
            spin_win += bonus
            free_spin_triggers += 1
        elif respins and sc1 >= respins["min_count"]:
            bonus = simulate_respins(preset, bet, rng, grid)
            feature_win += bonus
            spin_win += bonus
            respin_triggers += 1

        spin_win = min(spin_win, max_win * bet)
        total_win += spin_win
        sum_squares += spin_win * spin_win
        hits += spin_win > 0
        actual_max = max(actual_max, spin_win)

    buy = preset.get("feature_buy")
    if buy and free_spins:
        buy_sessions = max(10_000, min(100_000, spins // 10))
        for _ in range(buy_sessions):
            feature_buy_total += simulate_free_spins(preset, bet, rng)
            feature_buy_sessions += 1

    mean = total_win / spins
    variance = max(0.0, sum_squares / spins - mean * mean)
    avg_buy_win = feature_buy_total / feature_buy_sessions if feature_buy_sessions else 0.0
    return {
        "spins": spins,
        "total_rtp": mean,
        "base_rtp": base_win / spins,
        "feature_contribution": feature_win / spins,
        "hit_rate": hits / spins,
        "sd": math.sqrt(variance),
        "max_win": actual_max,
        "respin_trigger_rate": respin_triggers / spins,
        "free_spin_trigger_rate": free_spin_triggers / spins,
        "avg_free_spin_win": avg_buy_win,
        "feature_buy_rtp": (
            avg_buy_win / buy["cost_multiplier"] if buy and buy_sessions else 0.0
        ),
    }

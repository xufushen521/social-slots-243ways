from __future__ import annotations

from math import prod
from typing import Any


def count_symbol(grid: list[list[str]], symbol: str) -> int:
    return sum(cell == symbol for reel in grid for cell in reel)


def evaluate_ways(
    grid: list[list[str]],
    preset: dict[str, Any],
    bet: float,
) -> list[dict[str, Any]]:
    min_match = preset["grid"]["min_match"]
    wins: list[dict[str, Any]] = []
    for symbol, info in preset["symbols"].items():
        if info.get("type") != "regular":
            continue
        counts = [sum(cell == symbol for cell in reel) for reel in grid]
        match = 0
        for count in counts:
            if count == 0:
                break
            match += 1
        if match < min_match:
            continue
        match = min(match, len(counts))
        ways = prod(counts[:match])
        pay = info["pays"][str(match)]
        wins.append(
            {
                "symbol": symbol,
                "match": match,
                "ways": ways,
                "pay": pay,
                "win": pay * ways * bet,
            }
        )
    return sorted(wins, key=lambda item: item["win"], reverse=True)

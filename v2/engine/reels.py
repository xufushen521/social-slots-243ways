from __future__ import annotations

import random
from typing import Any


def draw_grid(
    preset: dict[str, Any],
    rng: random.Random | None = None,
    sticky: dict[tuple[int, int], str] | None = None,
) -> list[list[str]]:
    rng = rng or random.Random()
    strips = preset["reels"]["strips"]
    rows = preset["grid"]["rows"]
    grid: list[list[str]] = []
    for strip in strips:
        stop = rng.randrange(len(strip))
        grid.append([strip[(stop + row) % len(strip)] for row in range(rows)])
    if sticky:
        for (reel_index, row_index), symbol in sticky.items():
            if 0 <= reel_index < len(grid) and 0 <= row_index < len(grid[reel_index]):
                grid[reel_index][row_index] = symbol
    return grid

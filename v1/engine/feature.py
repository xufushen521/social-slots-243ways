from __future__ import annotations


def scatter_positions(grid: list[list[str]], symbol: str) -> dict[tuple[int, int], str]:
    return {
        (reel_index, row_index): symbol
        for reel_index, reel in enumerate(grid)
        for row_index, cell in enumerate(reel)
        if cell == symbol
    }


def merge_sticky(
    sticky: dict[tuple[int, int], str],
    grid: list[list[str]],
    symbol: str,
) -> tuple[dict[tuple[int, int], str], int]:
    merged = dict(sticky)
    new_count = 0
    for position, cell_symbol in scatter_positions(grid, symbol).items():
        if position not in merged:
            merged[position] = cell_symbol
            new_count += 1
    return merged, new_count

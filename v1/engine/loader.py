from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGULAR_SYMBOLS = ("K", "Q", "J", "10", "9", "8", "7")
PAY_KEYS = ("3", "4", "5")


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    validate_config(config)
    return config


def list_presets(config: dict[str, Any]) -> list[str]:
    return list(config["presets"].keys())


def validate_config(config: dict[str, Any]) -> None:
    presets = config.get("presets")
    _require(isinstance(presets, dict) and presets, "presets must be non-empty")
    _require(config.get("max_win", 0) > 0, "max_win must be positive")
    _require(config.get("default_preset") in presets, "default_preset is invalid")
    for name, preset in presets.items():
        validate_preset(name, preset)


def validate_preset(name: str, preset: dict[str, Any]) -> None:
    grid = preset.get("grid", {})
    _require(grid.get("reels") == 5, f"{name}: reels must be 5")
    _require(grid.get("rows") == 3, f"{name}: rows must be 3")
    _require(grid.get("ways") == 243, f"{name}: ways must be 243")
    _require(grid.get("pay_direction") == "left_to_right", f"{name}: pay direction")
    _require(grid.get("min_match") == 3, f"{name}: min_match must be 3")

    symbols = preset.get("symbols", {})
    for symbol in REGULAR_SYMBOLS:
        _require(symbol in symbols, f"{name}: missing {symbol}")
        _require(symbols[symbol].get("type") == "regular", f"{name}:{symbol} regular")
        _require(all(key in symbols[symbol].get("pays", {}) for key in PAY_KEYS), f"{name}:{symbol} pays")

    strips = preset.get("reels", {}).get("strips", [])
    _require(len(strips) == 5, f"{name}: need 5 strips")
    for index, strip in enumerate(strips, start=1):
        _require(len(strip) >= 3, f"{name}: reel {index} too short")
        unknown = sorted(set(strip) - set(symbols))
        _require(not unknown, f"{name}: reel {index} unknown {unknown}")

    scatter = preset.get("scatter")
    if scatter:
        respins = scatter.get("respins")
        if respins:
            _require(respins.get("symbol") in symbols, f"{name}: SC1 missing")
            _require(respins.get("min_count") == 3, f"{name}: SC1 threshold")
            _require(respins.get("max_respins", 0) > 0, f"{name}: respin max")
        free_spins = scatter.get("free_spins")
        if free_spins:
            _require(free_spins.get("symbol") in symbols, f"{name}: SC2 missing")
            _require(free_spins.get("min_count") == 3, f"{name}: SC2 threshold")
            _require(free_spins.get("spins", 0) > 0, f"{name}: FS spins")
            _require(free_spins.get("multiplier", 0) > 0, f"{name}: FS multiplier")

    feature_buy = preset.get("feature_buy")
    if feature_buy:
        _require(feature_buy.get("cost_multiplier", 0) > 0, f"{name}: buy cost")

    bet = preset.get("bet", {})
    _require(bet.get("levels"), f"{name}: bet levels")
    _require(bet.get("default") in bet["levels"], f"{name}: default bet")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)

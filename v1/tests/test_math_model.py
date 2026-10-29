from copy import deepcopy
from pathlib import Path
import itertools
import unittest

from engine.loader import load_config
from engine.math_model import base_metrics
from engine.ways import evaluate_ways


class MathModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = load_config(Path(__file__).resolve().parents[1] / "config.json")
        cls.preset = config["presets"][config["default_preset"]]

    def test_exact_ways_matches_bruteforce(self) -> None:
        toy = deepcopy(self.preset)
        toy["reels"]["strips"] = [
            ["K", "Q", "J", "10", "K"],
            ["K", "Q", "10", "9", "Q"],
            ["J", "10", "9", "8", "K"],
            ["Q", "9", "8", "7", "Q"],
            ["J", "8", "7", "K", "J"],
        ]
        exact = base_metrics(toy)["ways_rtp"]
        total = 0.0
        count = 0
        for stops in itertools.product(range(5), repeat=5):
            grid = [
                [strip[(stop + row) % len(strip)] for row in range(3)]
                for strip, stop in zip(toy["reels"]["strips"], stops)
            ]
            total += sum(item["win"] for item in evaluate_ways(grid, toy, 1.0))
            count += 1
        self.assertAlmostEqual(exact, total / count)


if __name__ == "__main__":
    unittest.main()

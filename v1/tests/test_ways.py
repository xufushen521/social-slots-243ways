from pathlib import Path
import unittest

from engine.loader import load_config
from engine.ways import evaluate_ways


class WaysTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = load_config(Path(__file__).resolve().parents[1] / "config.json")
        cls.preset = config["presets"][config["default_preset"]]

    def test_all_k_five_of_a_kind(self) -> None:
        grid = [["K", "K", "K"] for _ in range(5)]
        wins = evaluate_ways(grid, self.preset, 1.0)
        k_win = next(item for item in wins if item["symbol"] == "K")
        self.assertEqual(k_win["match"], 5)
        self.assertEqual(k_win["ways"], 243)
        self.assertAlmostEqual(
            k_win["win"],
            self.preset["symbols"]["K"]["pays"]["5"] * 243,
        )


if __name__ == "__main__":
    unittest.main()

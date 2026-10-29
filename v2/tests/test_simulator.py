from pathlib import Path
import unittest

from engine.loader import load_config
from engine.math_model import base_metrics
from engine.simulator import simulate_preset


class SimulatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        config = load_config(Path(__file__).resolve().parents[1] / "config.json")
        cls.config = config
        cls.preset = config["presets"][config["default_preset"]]

    def test_base_matches_exact(self) -> None:
        exact = base_metrics(self.preset)["ways_rtp"]
        result = simulate_preset(self.preset, spins=20_000, seed=7)
        self.assertAlmostEqual(result["base_rtp"], exact, delta=0.05)

    def test_features_and_buy(self) -> None:
        result = simulate_preset(self.preset, spins=10_000, seed=8)
        if "scatter" in self.preset:
            self.assertGreaterEqual(result["feature_contribution"], 0)
        if "feature_buy" in self.preset:
            self.assertGreater(result["feature_buy_rtp"], 0)
            self.assertLess(result["feature_buy_rtp"], 1.0)


if __name__ == "__main__":
    unittest.main()

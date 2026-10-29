from pathlib import Path
import unittest

from engine.loader import REGULAR_SYMBOLS, load_config


class ConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_config(Path(__file__).resolve().parents[1] / "config.json")
        cls.preset = cls.config["presets"][cls.config["default_preset"]]

    def test_grid_and_max_win(self) -> None:
        self.assertEqual(self.preset["grid"]["reels"], 5)
        self.assertEqual(self.preset["grid"]["rows"], 3)
        self.assertEqual(self.preset["grid"]["ways"], 243)
        self.assertGreater(self.config["max_win"], 0)

    def test_seven_regular_symbols(self) -> None:
        regular = [
            symbol
            for symbol, info in self.preset["symbols"].items()
            if info["type"] == "regular"
        ]
        self.assertEqual(set(regular), set(REGULAR_SYMBOLS))


if __name__ == "__main__":
    unittest.main()

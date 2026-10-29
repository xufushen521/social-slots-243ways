from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.loader import load_config
from engine.math_model import base_metrics


def main() -> None:
    config = load_config(Path(__file__).resolve().parents[1] / "config.json")
    for name, preset in config["presets"].items():
        metrics = base_metrics(preset)
        print(name, f"ways={metrics['ways_rtp']:.4%}")
        for key, value in metrics["trigger_probabilities"].items():
            print(f"  {key} trigger={value:.4%}")


if __name__ == "__main__":
    main()

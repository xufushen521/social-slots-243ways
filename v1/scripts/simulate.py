from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.loader import load_config
from engine.math_model import base_metrics
from engine.simulator import simulate_preset


def main() -> None:
    spins = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    config = load_config(Path(__file__).resolve().parents[1] / "config.json")
    preset = config["presets"][config["default_preset"]]
    exact = base_metrics(preset)
    result = simulate_preset(preset, spins=spins)
    print(f"spins={result['spins']:,}")
    print(f"exact ways RTP={exact['ways_rtp']:.4%}")
    print(f"sim base RTP={result['base_rtp']:.4%}")
    print(f"feature contribution={result['feature_contribution']:.4%}")
    print(f"total RTP={result['total_rtp']:.4%}")
    print(f"hit rate={result['hit_rate']:.4%}")
    print(f"SD={result['sd']:.4f}")
    print(f"max win={result['max_win']:.2f}x")
    print(f"SC1 trigger={result['respin_trigger_rate']:.4%}")
    print(f"SC2 trigger={result['free_spin_trigger_rate']:.4%}")
    print(f"avg FS win={result['avg_free_spin_win']:.4f}x")
    print(f"Feature Buy RTP={result['feature_buy_rtp']:.4%}")


if __name__ == "__main__":
    main()

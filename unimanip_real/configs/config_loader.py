import yaml
from pathlib import Path
from typing import Any, Dict

def load_config(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r") as f:
        cfg = yaml.safe_load(f)
    return cfg


def load_reset_joints_config(path: str) -> Dict[str, float]:
    """
    Load a YAML file that defines:
        reset_joints:
          joint_name_1: angle1
          joint_name_2: angle2
          ...

    Returns:
        dict {joint_name: float_angle}
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "reset_joints" not in data:
        raise ValueError(f"YAML must contain a top-level 'reset_joints' dict, got: {data}")

    reset_joints_raw = data["reset_joints"]
    if not isinstance(reset_joints_raw, dict):
        raise ValueError(f"'reset_joints' must be a dict, got: {type(reset_joints_raw)}")

    reset_joints: Dict[str, float] = {}
    for joint_name, angle in reset_joints_raw.items():
        try:
            reset_joints[str(joint_name)] = float(angle)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid angle for joint '{joint_name}': {angle}")

    print(f"[ConfigLoader] Loaded {len(reset_joints)} reset joints from {config_path}")
    return reset_joints
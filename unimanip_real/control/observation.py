from typing import Dict, Any
from ..core.types import RawObservation

def build_model_input(obs: RawObservation) -> Dict[str, Any]:
    model_input = {
        # "joint_angles": obs.right_arm_q.tolist() + obs.body_q.tolist(),
        # "ee_pose_right": obs.ee_pose_right.tolist(),
    }
    # if obs.head_top_depth is not None:
    #     model_input["head_top_depth"] = obs.head_top_depth.tolist()
    # if obs.right_wrist_depth is not None:
    #     model_input["right_wrist_depth"] = obs.right_wrist_depth.tolist()
    return model_input
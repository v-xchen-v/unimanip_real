from typing import Dict, Any

def action_to_joint_targets(
    action: Dict[str, Any],
    current_q: Any,
    config: Dict[str, Any],
) -> Any:
    """
    Postprocess the model action output to get joint target positions.
    This function assumes the action contains only the right arm joint targets.
    It concatenates the body joints (kept at current positions) with the right arm joints from action.
    """
    import numpy as np

    num_body_joints = config["robot"].get("num_body_joints", 2)
    right_arm_action = np.zeros(7)  # default to zeros
    # right_arm_action = np.array(action["right_arm_joints"])  # assuming action provides this key

    # Get current body joint positions
    current_body_joints = current_q[:num_body_joints]

    # Concatenate body joints with right arm joints
    q_target = np.concatenate([current_body_joints, right_arm_action], axis=0)

    return q_target
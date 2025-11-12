from typing import Dict, Any, Optional
import numpy as np
from robot_kinematics.core.robot_kinematics import RobotKinematics
from robot_kinematics.core.types import Pose
from ..constrants import get_reset_joint_cfg

# Option 1: Module-level singleton with lazy initialization
_fk_kinematics_instance = None
_ik_kinematics_instance = None

def get_fk_kinematics_instance(
    urdf_path: str = "/home/xichen/Documents/repos/unimanip_real/assets/g1/G1_120s/urdf/G1_120s.urdf",
    base_link: str = "base_link",
    ee_link: str = "gripper_r_center_link",
) -> RobotKinematics:
    """Get or create the kinematics instance (singleton pattern)."""
    global _fk_kinematics_instance
    if _fk_kinematics_instance is None:
        # Initialize your instance here (e.g., RobotKinematics)
        # _kinematics_instance = RobotKinematics(config)
        _fk_kinematics_instance = RobotKinematics(
            urdf_path=urdf_path,
            base_link=base_link,
            ee_link=ee_link,
            backend="urdfpy"
        )
    return _fk_kinematics_instance

def get_ik_kinematics_instance(
    urdf_path: str = "/home/xichen/Documents/repos/unimanip_real/assets/g1/G1_120s/urdf/G1_120s.urdf",
    base_link: str = "base_link",
    ee_link: str = "gripper_r_center_link",
) -> RobotKinematics:
    """Get or create the kinematics instance (singleton pattern)."""
    global _ik_kinematics_instance
    if _ik_kinematics_instance is None:
        # Initialize your instance here (e.g., RobotKinematics)
        # _kinematics_instance = RobotKinematics(config)
        active_joints = [
            "idx61_arm_r_joint1",
            "idx62_arm_r_joint2",
            "idx63_arm_r_joint3",
            "idx64_arm_r_joint4",
            "idx65_arm_r_joint5",
            "idx66_arm_r_joint6",
            "idx67_arm_r_joint7",
        ]
            
        reset_q_cfg = get_reset_joint_cfg("open_laptop")
        _ik_kinematics_instance = RobotKinematics(
            urdf_path=urdf_path,
            base_link=base_link,
            ee_link=ee_link,
            backend="pinocchio",
            active_joints=active_joints,
            inactive_joints_seed={
                "idx01_body_joint1": reset_q_cfg["idx01_body_joint1"],
                "idx02_body_joint2": reset_q_cfg["idx02_body_joint2"],
            }
    )
    return _ik_kinematics_instance

# Option 2: Class-based approach (if you need multiple instances or state management)
# class ActionPostprocessor:
#     def __init__(self, config: Dict[str, Any]):
#         self.config = config
#         self.kinematics = RobotKinematics(config)  # Created once
#     
#     def current_q_to_ee_pose(self, current_q: Dict[str, float]) -> np.ndarray:
#         # Use self.kinematics
#         return self.kinematics.forward_kinematics(current_q)
#     
#     def action_to_joint_targets(self, action: np.ndarray, current_q: Dict[str, float]) -> Dict[str, float]:
#         # Use self.kinematics
#         pass


# Option 3: Pass instance as parameter (most explicit, best for testing)
# def _current_q_to_ee_pose(
#     current_q: Dict[str, float],
#     kinematics_instance,
# ) -> np.ndarray:
#     return kinematics_instance.forward_kinematics(current_q)


def _current_q_to_ee_pose(
    current_q: Dict[str, float],
    config: Dict[str, Any],
) -> np.ndarray:
    """
    Convert current joint positions to end-effector pose.
    This is a placeholder function and should be implemented based on the robot kinematics.
    """
    # Use the singleton instance
    fk_kinematics = get_fk_kinematics_instance()
    
    chain_joint_names = fk_kinematics.joint_names
    current_q_in_chain = {k: v for k, v in current_q.items() if k in chain_joint_names}
    current_pose = fk_kinematics.fk(current_q_in_chain)
    ee_pose = current_pose.as_flat_array()
    
    # Placeholder implementation
    # ee_pose = np.zeros(7)  # [x, y, z, qw, qx, qy, qz]
    return ee_pose

def apply_action_to_current_pose(
    action: np.ndarray,
    current_pose: np.ndarray,
) -> np.ndarray:
    """
    Apply the action to the current end-effector pose.
    This is a placeholder function and should be implemented based on the robot kinematics.
    
    Return the new end-effector pose after applying the action.
    """
    
    
    # Placeholder implementation: simply return the action as the new pose
    new_pose = current_pose
    return new_pose

def get_new_joint_targets_from_ee_pose(
    new_pose_arr: np.ndarray,
    current_q: Dict[str, float],
    config: Dict[str, Any],
) -> Dict[str, float]:
    """
    Given a desired end-effector pose, compute the corresponding joint targets using IK.
    This is a placeholder function and should be implemented based on the robot kinematics.
    """
    # Use the singleton instance
    ik_kinematics = get_ik_kinematics_instance()
    
    # Convert new_pose_arr to Pose object if needed
    target_pose = Pose(
        xyz=new_pose_arr[:3],
        quat_wxyz=new_pose_arr[3:7]
    ) 
    
    active_joints = [
        "idx61_arm_r_joint1",
        "idx62_arm_r_joint2",
        "idx63_arm_r_joint3",
        "idx64_arm_r_joint4",
        "idx65_arm_r_joint5",
        "idx66_arm_r_joint6",
        "idx67_arm_r_joint7",
    ]
    current_q_active = {k: v for k, v in current_q.items() if k in active_joints}
    active_q_arr = np.array([current_q_active[joint] for joint in active_joints])
    
    ik_result = ik_kinematics.ik(target_pose=target_pose,
                     seed_q=active_q_arr)
    
    new_q_arr = ik_result.q
    new_q_dict = {joint: new_q_arr[i] for i, joint in enumerate(active_joints)}
    
    delta_q_dict = {joint: new_q_dict[joint] - current_q_active[joint] for joint in active_joints}
    # print delta q for debugging
    print("Delta q from IK:")
    print(delta_q_dict)
    
    joint_targets = new_q_dict
    
    # Placeholder implementation
    joint_targets = {}  # e.g., {"joint1": 0.0, "joint2": 1.0, ...}
    return joint_targets

def action_to_joint_targets(
    action: np.ndarray,
    current_q: Dict[str, float],
    config: Dict[str, Any],
) -> Dict[str, float]:
    """
    Postprocess the model action output to get joint target positions.
    This function assumes the action contains only the right arm joint targets.
    It concatenates the body joints (kept at current positions) with the right arm joints from action.
    """
    pose_arr = _current_q_to_ee_pose(current_q, config)
    new_pose_arr = apply_action_to_current_pose(action, pose_arr)
    q_targets = get_new_joint_targets_from_ee_pose(new_pose_arr, current_q, config)
    return q_targets

    # import numpy as np

    # num_body_joints = config["robot"].get("num_body_joints", 2)
    # right_arm_action = np.zeros(7)  # default to zeros
    # # right_arm_action = np.array(action["right_arm_joints"])  # assuming action provides this key

    # # Get current body joint positions
    # current_body_joints = current_q[:num_body_joints]

    # # Concatenate body joints with right arm joints
    # q_target = np.concatenate([current_body_joints, right_arm_action], axis=0)

    # return q_target
    return None # Placeholder implementation


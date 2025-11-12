KIN_DIR = "/home/xichen/Documents/repos/unimanip_real/robot-kinematics-xc"
import sys
if KIN_DIR not in sys.path:
    sys.path.append(KIN_DIR)

from typing import Dict, Any, Optional
import numpy as np
from robot_kinematics.core.robot_kinematics import RobotKinematics
from robot_kinematics.core.types import Pose
from ..constrants import get_reset_joint_cfg

"""
action: delta_position(3d) + delta_euler_angle(3d) + gripper_joint_angle(1d)
action_range: [-1, 1]
delta_position_scale: 0.025
delta_euler_angle_scale: 0.025
"""


def compose_quat(base_q, delta_q, *, delta_in_local=True, normalize=True, eps=1e-12):
    """
    Compose a base orientation with a delta rotation.

    Args:
        base_q:  (..., 4) base quaternion [w,x,y,z]
        delta_q: (..., 4) delta quaternion [w,x,y,z]
        delta_in_local: if True, final = base ⊗ delta (delta in body/local frame).
                        if False, final = delta ⊗ base (delta in world frame).
        normalize: if True, renormalize result for numerical stability.
        eps: small number to avoid division by zero.

    Returns:
        (..., 4) final quaternion [w,x,y,z]
    """
    base_q = np.asarray(base_q)
    delta_q = np.asarray(delta_q)

    if delta_in_local:
        q = quaternion_multiply(base_q, delta_q)
    else:
        q = quaternion_multiply(delta_q, base_q)

    if normalize:
        norm = np.linalg.norm(q, axis=-1, keepdims=True)
        q = q / np.clip(norm, eps, None)
    return q

# def quaternion_to_euler_angle(quaternions):
#     """
#     Convert a batch of quaternions to Euler angles.
 
#     Args:
#         quaternions (torch.Tensor): Tensor of shape (batch_size, 4) in (w, x, y, z) format.
#     Returns:
#         euler_angles (torch.Tensor): Tensor of shape (batch_size, 3), representing Euler angles (roll, pitch, yaw) in radians.
#     """
#     import torch
#     # Extract components
#     w, x, y, z = quaternions[:, 0], quaternions[:, 1], quaternions[:, 2], quaternions[:, 3]
 
#     # Compute Euler angles
#     # Roll (X-axis rotation)
#     roll = torch.atan2(2 * (w * x + y * z), 1 - 2 * (x**2 + y**2))
#     # Pitch (Y-axis rotation) - Clamp to avoid NaNs
#     sinp = 2 * (w * y - z * x)
#     pitch = torch.asin(sinp.clamp(-1.0, 1.0))
#     # Yaw (Z-axis rotation)
#     yaw = torch.atan2(2 * (w * z + x * y), 1 - 2 * (y**2 + z**2))
 
#     return torch.stack((roll, pitch, yaw), dim=-1)  # Shape (batch_size, 3)

def euler_to_quaternion(roll, pitch, yaw):
    """
    Convert Euler angles (roll, pitch, yaw) to a quaternion (w, x, y, z).

    Args:
        roll (float): Rotation around the X-axis, in radians.
        pitch (float): Rotation around the Y-axis, in radians.
        yaw (float): Rotation around the Z-axis, in radians.

    Returns:
        np.ndarray: Quaternion [w, x, y, z].
    """
    cr = np.cos(roll / 2)
    sr = np.sin(roll / 2)
    cp = np.cos(pitch / 2)
    sp = np.sin(pitch / 2)
    cy = np.cos(yaw / 2)
    sy = np.sin(yaw / 2)

    # Compute quaternion (w, x, y, z)
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return np.array([w, x, y, z])

def quaternion_to_euler_angle(quaternion):
    """
    Convert a single quaternion (w, x, y, z) to Euler angles (roll, pitch, yaw) in radians.
    
    Args:
        quaternion (array-like): Quaternion [w, x, y, z].
    Returns:
        np.ndarray: Euler angles [roll, pitch, yaw] in radians.
    """
    w, x, y, z = quaternion

    # Roll (x-axis rotation)
    roll = np.arctan2(2 * (w * x + y * z), 1 - 2 * (x**2 + y**2))

    # Pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    sinp = np.clip(sinp, -1.0, 1.0)  # numerical stability
    pitch = np.arcsin(sinp)

    # Yaw (z-axis rotation)
    yaw = np.arctan2(2 * (w * z + x * y), 1 - 2 * (y**2 + z**2))

    return np.array([roll, pitch, yaw])

def quaternion_multiply(q1, q2):
    """
    Perform quaternion multiplication for a batch of quaternions for vector components.
    Args:
        q1: Array of shape (batch_size, 4) representing the first quaternion batch.
        q2: Array of shape (batch_size, 4) representing the second quaternion batch.
    Returns:
        Array of shape (batch_size, 4) representing the resulting quaternion batch.
    """
    # Separate scalar (w) and vector (x, y, z) parts
    w1, v1 = q1[..., 0], q1[..., 1:]
    w2, v2 = q2[..., 0], q2[..., 1:]
    # Compute the scalar (w) part
    w_r = w1 * w2 - np.sum(v1 * v2, axis=-1)
    # Compute the vector (x, y, z) part
    v_r = np.expand_dims(w1, -1) * v2 + np.expand_dims(w2, -1) * v1 + np.cross(v1, v2, axis=-1)
    # Combine scalar and vector parts
    return np.concatenate((np.expand_dims(w_r, -1), v_r), axis=-1)


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
    actions: np.ndarray,
    current_pose: np.ndarray,
) -> np.ndarray:
    """
    Apply the action to the current end-effector pose.
    This is a placeholder function and should be implemented based on the robot kinematics.
    
    Return the new end-effector pose after applying the action.
    """
    action = actions # only use the first step
    action_delta_xyz = action[:3]
    action_delta_euler = action[3:6]  # Assuming action contains quaternion delta
    action_delta_quat = euler_to_quaternion(
        roll=action_delta_euler[0],
        pitch=action_delta_euler[1],
        yaw=action_delta_euler[2],
    )
    action_gripper = action[6]
    
    xyz_scale = 0.025
    euler_scale = 0.025
    new_xyz = current_pose[:3] + (np.array(action_delta_xyz) * xyz_scale).tolist()
    new_quat = compose_quat(current_pose[3:7], action_delta_quat)
    new_pose = np.concatenate([new_xyz, new_quat], axis=0)
    
    # Placeholder implementation: simply return the action as the new pose
    # new_pose = current_pose
    return new_pose, action_gripper

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
    # pretty print the delta q dict with degree
    delta_q_dict_deg = {joint: np.degrees(delta_q_dict[joint]) for joint in delta_q_dict}
    print(delta_q_dict_deg)
    
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
    new_pose_arr, new_r_gripper_value = apply_action_to_current_pose(action, pose_arr)
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


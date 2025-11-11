# unmanip_real/robot/sdk_robot.py

from __future__ import annotations
from typing import Dict, Any, List
import numpy as np

from ..control.observation import RawObservation
# adjust import path to where you put RobotSDKWrapper file
from ..robot.robot_sdk_wrapper import create_robot_sdk, RobotSDKWrapper, RobotState  # <-- rename file as needed


class SDKRobot:
    """
    Adapter that uses RobotSDKWrapper (A2D / Example / DryRun) to produce RawObservation
    for unmanip_real.
    """

    def __init__(self, config: Dict[str, Any], task_config: Dict[str, Any] = None) -> None:
        self.config = config
        robot_cfg = config.get("robot", {})
        
        # reset joints, ... in task config
        self.task_config = task_config if task_config is not None else {}
        
        sdk_type = robot_cfg.get("sdk_type", "example")
        sdk_config = {
            "num_joints": robot_cfg.get("num_joints", 14),
            # pass through any SDK-specific keys if needed
            "image_width": robot_cfg.get("image_width", 640),
            "image_height": robot_cfg.get("image_height", 480),
            "initialization_delay": robot_cfg.get("initialization_delay", 5.0),
        }

        self.sdk: RobotSDKWrapper = create_robot_sdk(sdk_type, sdk_config)

        jm = robot_cfg["joint_mapping"]
        self.right_arm_indices: List[int] = jm["right_arm_indices"]
        self.body_indices: List[int] = jm["body_indices"]
        self.right_arm_joint_names: List[str] = jm["right_arm_joint_names"]
        self.body_joint_names: List[str] = jm["body_joint_names"]

        sensors = robot_cfg.get("sensors", {})
        self.head_depth_available = sensors.get("head_depth_available", False)
        self.right_arm_depth_available = sensors.get("right_arm_depth_available", False)

    # ------------ lifecycle ------------

    def connect(self) -> bool:
        return self.sdk.connect()

    def disconnect(self) -> None:
        self.sdk.disconnect()

    def home(self) -> bool:
        """Use SDK's home_robot as reset."""
        if hasattr(self.sdk, "home_robot"):
            return self.sdk.home_robot()
        print("[SDKRobot] home_robot not implemented in SDK, no-op reset.")
        return True
    
    def reset(self) -> bool:
        # get reset joints from task_config
        if not "reset_joints" in self.task_config:
            print("[SDKRobot] No reset_joints found in task_config")
            raise ValueError("reset_joints not found in task_config")
        
        reset_joints_cfg = self.task_config["reset_joints"]
        print(f"[SDKRobot] Reset joints config: {reset_joints_cfg}")
        
        state = self.sdk.get_current_state()
        full = state.joint_angles.copy()
        for joint_name, angle in reset_joints_cfg.items():
            if joint_name in self.body_joint_names:
                idx = self.body_joint_names.index(joint_name)
                full[self.body_indices[idx]] = angle
            elif joint_name in self.right_arm_joint_names:
                idx = self.right_arm_joint_names.index(joint_name)
                full[self.right_arm_indices[idx]] = angle
            else:
                print(f"[SDKRobot] Warning: joint name {joint_name} not found in body or right arm joints.")
                
        return self.sdk.move_to_joint_angles(full, duration=2.0)

    # ------------ core helpers ------------

    def _state_to_ee_pose_right(self, state: RobotState) -> np.ndarray:
        """
        Convert RobotState end_position + end_orientation(w,x,y,z)
        -> [x, y, z, qx, qy, qz, qw].
        """
        pos = np.asarray(state.end_position, dtype=np.float32)
        quat_wxyz = np.asarray(state.end_orientation, dtype=np.float32)  # [w,x,y,z]
        qx, qy, qz, qw = quat_wxyz[1], quat_wxyz[2], quat_wxyz[3], quat_wxyz[0]
        return np.concatenate([pos, np.array([qx, qy, qz, qw], dtype=np.float32)])

    def _split_joints(self, joint_angles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Split full joint vector into (body_q, right_arm_q) using config indices.
        """
        joint_angles = np.asarray(joint_angles, dtype=np.float32)
        body_q = joint_angles[self.body_indices]
        right_arm_q = joint_angles[self.right_arm_indices]
        return body_q, right_arm_q

    # ------------ observation ------------

    def get_raw_observation(self) -> RawObservation:
        """
        Read RobotState + camera(s) from SDK and produce RawObservation.
        For now, SDK only exposes a single RGB camera and no depth, so:
          - reuse the same RGB frame for head_top/right/right_arm
          - generate zeros for depth where not available
        """
        state: RobotState = self.sdk.get_current_state()
        full_joints = state.joint_angles
        body_q, right_arm_q = self._split_joints(full_joints)

        # End-effector pose for right arm
        ee_pose_right = self._state_to_ee_pose_right(state)

        # RGB image from SDK (single camera)
        rgb = self.sdk.capture_image()
        H, W = rgb.shape[:2]

        # Depth stubs
        head_depth = None
        right_arm_depth = None
        if self.head_depth_available:
            head_depth = np.ones((H, W), dtype=np.float32)  # dummy "valid" depth
        if self.right_arm_depth_available:
            right_arm_depth = np.ones((H, W), dtype=np.float32)
        else:
            # You said: right wrist depth cannot be grabbed -> use all zeros
            right_arm_depth = np.zeros((H, W), dtype=np.float32)

        return RawObservation(
            head_top_rgb=rgb,
            head_right_rgb=rgb,
            right_arm_rgb=rgb,
            head_depth=head_depth,
            right_arm_depth=right_arm_depth,
            ee_pose_right=ee_pose_right,
            right_arm_q=right_arm_q,
            body_q=body_q,
            right_arm_joint_names=self.right_arm_joint_names,
            body_joint_names=self.body_joint_names,
        )

    # ------------ control ------------

    def move_body_and_right_arm(self, body_q: np.ndarray, right_arm_q: np.ndarray, duration: float = 1.0) -> bool:
        """
        Map (body_q, right_arm_q) back into full joint vector and send to SDK.
        Assumes other joints keep their current values.
        """
        state = self.sdk.get_current_state()
        full = state.joint_angles.copy()

        body_q = np.asarray(body_q, dtype=np.float32)
        right_arm_q = np.asarray(right_arm_q, dtype=np.float32)

        if len(body_q) != len(self.body_indices):
            raise ValueError(f"body_q length {len(body_q)} != body_indices {len(self.body_indices)}")
        if len(right_arm_q) != len(self.right_arm_indices):
            raise ValueError(f"right_arm_q length {len(right_arm_q)} != right_arm_indices {len(self.right_arm_indices)}")

        full[self.body_indices] = body_q
        full[self.right_arm_indices] = right_arm_q

        return self.sdk.move_to_joint_angles(full, duration=duration)

    def move_full_concatenated_joints(self, q_concat: np.ndarray, duration: float = 1.0) -> bool:
        """
        Convenience: q_concat = [body_q(2), right_arm_q(7)] in that order.
        """
        q_concat = np.asarray(q_concat, dtype=np.float32)
        n_body = len(self.body_indices)
        n_arm = len(self.right_arm_indices)
        if len(q_concat) != n_body + n_arm:
            raise ValueError(f"Expected {n_body + n_arm} angles (body+right_arm), got {len(q_concat)}")

        body_q = q_concat[:n_body]
        right_arm_q = q_concat[n_body:]
        return self.move_body_and_right_arm(body_q, right_arm_q, duration=duration)

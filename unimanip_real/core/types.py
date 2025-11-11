from dataclasses import dataclass
import numpy as np
from typing import Optional

@dataclass
class RawObservation:
    """
    Raw (unprocessed) observation from the robot and sensors.
    This contains raw camera frames, depth maps, and joint states
    directly as returned from the robot SDK or simulation.
    """
    # RGB cameras
    head_top_rgb: Optional[np.ndarray] = None  # Shape: (H, W, 3), dtype: uint8
    right_wrist_rgb: Optional[np.ndarray] = None  # Shape: (H, W, 3), dtype: uint8
    
    # Depth cameras
    head_top_depth: Optional[np.ndarray] = None  # Shape: (H, W), dtype: float32 or (H, W, 3), not sure for now
    right_wrist_depth: Optional[np.ndarray] = None  # Shape: (H, W), dtype: float32 or (H, W, 3), not sure for now
    
    # Robot state (from base_link to right end-effector, include 7-DoF right arm and 2-DoF body)
    right_arm_q: Optional[np.ndarray] = None  # Shape: (7,), dtype: float32
    body_q: Optional[np.ndarray] = None  # Shape: (2,), dtype: float32
    
    # Joint order metadata
    right_arm_joint_names: Optional[list[str]] = None  # List of 7 joint in order
    body_joint_names: Optional[list[str]] = None  # List of 2 joint in order
    
    @property
    def full_joint_vector(self) -> Optional[np.ndarray]:
        """Concatenated full joint configuration vector (right arm + body)."""
        if self.right_arm_q is not None and self.body_q is not None:
            return np.concatenate([self.right_arm_q, self.body_q], axis=0)
        return None
    
    @property
    def full_joint_names(self) -> Optional[list[str]]:
        """Concatenated full joint names (right arm + body)."""
        if self.right_arm_joint_names is not None and self.body_joint_names is not None:
            return self.right_arm_joint_names + self.body_joint_names
        return None
    
    
def reorder_joints(raw_obs: RawObservation, desired_order: list[str]) -> np.ndarray:
    name_to_val = dict(zip(raw_obs.full_joint_names, raw_obs.full_joint_vector))
    return np.array([name_to_val[name] for name in desired_order], dtype=float)


@dataclass
class RobotState:
    """Current state of the robot."""
    joint_angles: np.ndarray      # (num_joints,) 
    head_angles: np.ndarray       # (2,) - pan, tilt
    waist_angles: np.ndarray      # (2,) - waist pan, tilt
    end_position: np.ndarray      # (3,) - x, y, z
    end_orientation: np.ndarray   # (4,) - quaternion w, x, y, z
    timestamp: float

    
    
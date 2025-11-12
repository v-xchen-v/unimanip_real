from .base_robot import BaseRobotSDK
import time
from typing import Dict, Any
import numpy as np
from dataclasses import dataclass

@dataclass
class A2DRobotState:
    """Current state of the robot."""
    joint_angles: np.ndarray      # (num_joints,) 
    head_angles: np.ndarray       # (2,) - pan, tilt
    # end_position: np.ndarray      # (3,) - x, y, z
    # end_orientation: np.ndarray   # (4,) - quaternion w, x, y, z
    waist_angles: np.ndarray      # (2,) - waist pan, tilt
    # timestamp: float


class A2DRobotSDK(BaseRobotSDK):
    """
    A2D Robot SDK implementation using the a2d_sdk.robot.RobotDds API.
    
    This implementation uses the actual A2D robot SDK for controlling the humanoid robot.
    """
    def __init__(self):
        super().__init__()
        try:
            # Initialize A2D SDK robot here
            from a2d_sdk.robot import RobotDds
            self.robot_api = RobotDds()
            print(f"A2D Robot SDK initialized, waiting {self.initialization_delay}s for robot initialization...")
        except ImportError:
            print("Warning: a2d_sdk not found. Please install the A2D SDK or use simulation mode.")
            self.robot_api = None
            
        self.right_arm_joint_names = [
            "idx61_arm_r_joint1",
            "idx62_arm_r_joint2",
            "idx63_arm_r_joint3",
            "idx64_arm_r_joint4",
            "idx65_arm_r_joint5",
            "idx66_arm_r_joint6",
            "idx67_arm_r_joint7",
        ]
        
        self.arm_joint_names = [
            "idx21_arm_l_joint1",
            "idx22_arm_l_joint2",
            "idx23_arm_l_joint3",
            "idx24_arm_l_joint4",
            "idx25_arm_l_joint5",
            "idx26_arm_l_joint6",
            "idx27_arm_l_joint7",
            "idx61_arm_r_joint1",
            "idx62_arm_r_joint2",
            "idx63_arm_r_joint3",
            "idx64_arm_r_joint4",
            "idx65_arm_r_joint5",
            "idx66_arm_r_joint6",
            "idx67_arm_r_joint7",
        ]
        
        self.waist_joint_names = [
            "idx01_body_joint1",  # waist pan
            "idx02_body_joint2",  # waist height
        ]
        
        self.head_joint_names = [
            "idx11_head_joint1",  # head yaw
            "idx12_head_joint2",  # head pitch
        ]

        self.activate_joint_names = self.right_arm_joint_names
        self.chain_joint_names = self.body_joint_names + self.right_arm_joint_names
    
            
    def connect(self):
        """Connect to A2D robot."""
        if self.robot_api is None:
            print("A2D SDK not available")
            return False
            
        try:
            # Wait for robot initialization
            time.sleep(self.initialization_delay)
            print("Connected to A2D robot")
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to A2D robot: {e}")
            return False
        
    def disconnect(self):
        pass
    
    def move_joints(self, joint_positions: Dict[str, float]) -> bool:
        pass
    
    def get_current_joints(self) -> Dict[str, float]:
        """Get current state from A2D robot."""
        if self.robot_api is None:
            print("Robot API not available, returning dummy data")
            return super().get_current_state()
            
        try:
            current_time = time.time()
            
            # Get arm joint states (14 joints - left 7 + right 7)
            arm_joints, _ = self.robot_api.arm_joint_states()
            joint_angles = np.array(arm_joints, dtype=np.float32)
            
            # Get head joint states [yaw, pitch]
            head_joints, _ = self.robot_api.head_joint_states()
            head_angles = np.array(head_joints, dtype=np.float32)
            
            # Get waist joint states [pitch, height] - convert height from cm to m
            waist_joints, _ = self.robot_api.waist_joint_states()
            waist_angles = np.array([waist_joints[0], waist_joints[1] / 100.0], dtype=np.float32)
            
            # Get gripper states for end effector info
            gripper_states, _ = self.robot_api.gripper_states()
            
            
            robot_state = A2DRobotState(
                joint_angles=joint_angles,
                head_angles=head_angles,
                # end_position=end_position,
                # end_orientation=end_orientation,
                waist_angles=waist_angles,
                # timestamp=current_time
            )
            
            arm_joints_cfg = {
                name: float(angle) for name, angle in zip(self.arm_joint_names, robot_state.joint_angles)
            }
            head_joints_cfg = {
                name: float(angle) for name, angle in zip(self.head_joint_names, robot_state.head_angles)
            }
            waist_joints_cfg = {
                name: float(angle) for name, angle in zip(self.waist_joint_names, robot_state.waist_angles)
            }
            
            joint_cfg = {
                **arm_joints_cfg,
                **head_joints_cfg,
                **waist_joints_cfg
            }
            return joint_cfg
            
        except Exception as e:
            print(f"Failed to get robot state: {e}")
            # Return dummy data as fallback
            # return super().get_current_state()
            return None
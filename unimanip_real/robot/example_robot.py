from robot_kinematics.urdf.inspector import FullURDFInspector
from .base_robot import BaseRobotSDK
from typing import Dict, Any
from ..core.types import RawObservation 
import numpy as np
import cv2

class ExampleRobotSDK(BaseRobotSDK):
    """
    Enhanced example implementation for testing and reference.
    
    This provides a more complete simulation that mimics the A2D robot behavior
    without requiring the actual hardware or SDK
    """
    
    def __init__(
        self, 
        config: Dict[str, Any],
        urdf_path: str
    ) -> None:
        super().__init__(config)
        print("[ExampleRobotSDK] Initialized with config:", config)
        self.urdf_path = urdf_path
        
    def connect(self) -> None:
        print("[ExampleRobotSDK] Connecting to Example Robot SDK...")
        # Simulate connection delay
        import time
        time.sleep(1)
        
        # Use urdf inspector for simulation
        self.urdf_inspector = FullURDFInspector(
            urdf_path=self.urdf_path
        )
        # zero pose visualization
        # self.urdf_inspector.show_robot(joint_cfg={})
        
        print("[ExampleRobotSDK] Connected.")
        
    def disconnect(self) -> None:
        print("[ExampleRobotSDK] Disconnecting from Example Robot SDK...")
        # Simulate disconnection delay
        import time
        time.sleep(1)
        print("[ExampleRobotSDK] Disconnected.")
        
        
    def reset(self, reset_joint_cfg: Dict[str, float]) -> None:
        print("[ExampleRobotSDK] Resetting robot with joint configuration:", reset_joint_cfg)
        # Simulate reset delay
        import time
        time.sleep(1)
        
        # show the reset pose by fk with visual
        # self.urdf_inspector.show_robot(reset_joint_cfg)
        
        print("[ExampleRobotSDK] Robot reset complete.")
        
    def get_raw_observation(self) -> RawObservation:
        print("[ExampleRobotSDK] Getting observation from Example Robot SDK...")
        # Simulate observation retrieval delay
        import time
        time.sleep(0.5)
        
        head_top_rgb = self._get_head_rgb_image()
        right_wrist_rgb = self._get_head_rgb_image()  # For simplicity, use the same function
        head_depth = np.zeros((1280, 800, 3), dtype=np.float32)  # Placeholder depth image
        right_wrist_depth = np.zeros((1280, 800, 3), dtype=np.float32)  # Placeholder depth image
        
        rawobs = RawObservation(
            head_top_rgb=head_top_rgb,
            right_wrist_rgb=right_wrist_rgb,
            head_top_depth=head_depth,
            right_wrist_depth=right_wrist_depth,
        )
        
        # observation = {
        #     # "joint_positions": [0.0] * self.urdf_inspector.n_dofs,
        #     # "joint_velocities": [0.0] * self.urdf_inspector.n_dofs,
        #     # "end_effector_pose": self.urdf_inspector.fk([0.0] * self.urdf_inspector.n_dofs)
        # }
        
        # print("[ExampleRobotSDK] Observation retrieved:", observation)
        return rawobs
    
    def _get_head_rgb_image(self) -> np.ndarray:
        # Create more realistic simulation image
        height, width = 1280, 800

        # Create a gradient background
        image = np.zeros((height, width, 3), dtype=np.uint8)

        # Add color gradients
        for y in range(height):
            for x in range(width):
                image[y, x, 0] = int(255 * x / width)  # Red gradient
                image[y, x, 1] = int(255 * y / height)  # Green gradient
                image[y, x, 2] = int(128 + 127 * np.sin(x * 0.01) * np.sin(y * 0.01))  # Blue pattern

        # Add some geometric shapes to simulate objects
        cv2.circle(image, (160, 120), 50, (255, 255, 255), 2)
        cv2.rectangle(image, (300, 200), (400, 300), (0, 255, 255), 2)
        cv2.line(image, (0, 240), (640, 240), (255, 0, 255), 1)  # Horizon line
        return image
        
    
    def move_joints(self, joint_cfg: Dict[str, float]) -> None:
        print("[ExampleRobotSDK] Moving joints to positions:", joint_cfg)
        # Simulate movement delay
        import time
        time.sleep(1)
        
        # Show the new pose by fk with visual
        # self.urdf_inspector.show_robot(joint_cfg)
        
        print("[ExampleRobotSDK] Joints moved successfully.")
    
    
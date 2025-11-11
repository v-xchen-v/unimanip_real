# unimanip_real/robot/fake_robot.py

from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
import time

from ..core.types import RawObservation
from ..configs.config_loader import load_reset_joints_config


class FakeRobot:
    """
    A fake robot implementation for testing and simulation.
    This robot generates synthetic data and simulates robot movements
    without requiring actual hardware.
    """

    def __init__(self, robot_config: Dict[str, Any], task_config: Dict[str, Any] = None) -> None:
        self.config = robot_config
        robot_cfg = robot_config.get("robot", {})
        
        # reset joints, ... in task config
        self.task_config = task_config if task_config is not None else {}
        
        # Robot configuration
        self.num_joints = robot_cfg.get("num_joints", 14)
        self.image_width = robot_cfg.get("image_width", 640)
        self.image_height = robot_cfg.get("image_height", 480)
        
        # Joint mapping configuration
        jm = robot_cfg.get("joint_mapping", {})
        self.right_arm_indices: List[int] = jm.get("right_arm_indices", [0, 1, 2, 3, 4, 5, 6])
        self.body_indices: List[int] = jm.get("body_indices", [7, 8])
        self.right_arm_joint_names: List[str] = jm.get("right_arm_joint_names", 
            [f"right_arm_joint_{i}" for i in range(7)])
        self.body_joint_names: List[str] = jm.get("body_joint_names", 
            ["body_joint_0", "body_joint_1"])
        
        # Sensor configuration
        sensors = robot_cfg.get("sensors", {})
        self.head_depth_available = sensors.get("head_depth_available", False)
        self.right_arm_depth_available = sensors.get("right_arm_depth_available", False)
        
        # Internal state
        self.is_connected = False
        self.current_joint_angles = np.zeros(self.num_joints, dtype=np.float32)
        self.target_joint_angles = np.zeros(self.num_joints, dtype=np.float32)
        self.current_ee_pose = np.array([0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 1.0], dtype=np.float32)  # [x,y,z,qx,qy,qz,qw]
        
        # Movement simulation
        self.move_start_time = None
        self.move_duration = 0.0
        self.move_start_angles = None
        
        print(f"[FakeRobot] Initialized with {self.num_joints} joints")

    # ------------ lifecycle ------------

    def connect(self) -> bool:
        """Simulate connection to robot."""
        print("[FakeRobot] Connecting...")
        time.sleep(0.1)  # Simulate connection delay
        self.is_connected = True
        print("[FakeRobot] Connected successfully")
        return True

    def disconnect(self) -> None:
        """Simulate disconnection from robot."""
        print("[FakeRobot] Disconnecting...")
        self.is_connected = False
        print("[FakeRobot] Disconnected")

    def reset(self) -> bool:
        """Reset robot to home position."""
        print("[FakeRobot] Resetting to home position...")
        # read reset_joints from task_config
        if not "reset_joints" in self.task_config:
            print("[FakeRobot] No reset_joints found in task_config")
            raise ValueError("reset_joints not found in task_config")
        
        reset_joints_cfg = self.task_config["reset_joints"]
        print(f"[FakeRobot] Reset joints config: {reset_joints_cfg}")
            
        self.current_joint_angles = np.zeros(self.num_joints, dtype=np.float32)
        self.target_joint_angles = np.zeros(self.num_joints, dtype=np.float32)
        self.current_ee_pose = np.array([0.5, 0.0, 0.5, 0.0, 0.0, 0.0, 1.0], dtype=np.float32)
        self.move_start_time = None
        print("[FakeRobot] Reset complete")
        return True

    # ------------ core helpers ------------

    def _update_joint_simulation(self):
        """Update simulated joint positions based on ongoing movements."""
        if self.move_start_time is not None:
            elapsed = time.time() - self.move_start_time
            progress = min(elapsed / self.move_duration, 1.0)
            
            # Linear interpolation between start and target positions
            self.current_joint_angles = (
                self.move_start_angles + 
                progress * (self.target_joint_angles - self.move_start_angles)
            )
            
            if progress >= 1.0:
                self.move_start_time = None
                self.current_joint_angles = self.target_joint_angles.copy()
                print("[FakeRobot] Movement completed")

    def _simulate_forward_kinematics(self) -> np.ndarray:
        """Simulate forward kinematics to compute end-effector pose."""
        # Simple simulation: use joint angles to compute a reasonable EE pose
        arm_angles = self.current_joint_angles[self.right_arm_indices]
        
        # Very simplified FK - just for demonstration
        x = 0.3 + 0.1 * np.sin(arm_angles[0]) + 0.1 * np.cos(arm_angles[1])
        y = 0.1 * np.cos(arm_angles[0]) + 0.1 * np.sin(arm_angles[2])
        z = 0.4 + 0.1 * np.sin(arm_angles[1]) + 0.1 * np.cos(arm_angles[3])
        
        # Simple orientation based on wrist joints
        qx = 0.1 * np.sin(arm_angles[4])
        qy = 0.1 * np.cos(arm_angles[5])
        qz = 0.1 * np.sin(arm_angles[6])
        qw = np.sqrt(max(0, 1 - qx*qx - qy*qy - qz*qz))
        
        return np.array([x, y, z, qx, qy, qz, qw], dtype=np.float32)

    def _split_joints(self, joint_angles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Split full joint vector into (body_q, right_arm_q) using config indices."""
        joint_angles = np.asarray(joint_angles, dtype=np.float32)
        body_q = joint_angles[self.body_indices]
        right_arm_q = joint_angles[self.right_arm_indices]
        return body_q, right_arm_q

    def _generate_synthetic_image(self) -> np.ndarray:
        """Generate a synthetic RGB image."""
        # Create a simple test pattern
        img = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)
        
        # Add some color gradients and patterns
        for i in range(self.image_height):
            for j in range(self.image_width):
                img[i, j, 0] = (i * 255) // self.image_height  # Red gradient
                img[i, j, 1] = (j * 255) // self.image_width   # Green gradient
                img[i, j, 2] = 128  # Constant blue
                
        # Add some noise for realism
        noise = np.random.randint(-20, 20, size=(self.image_height, self.image_width, 3))
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return img

    def _generate_synthetic_depth(self) -> np.ndarray:
        """Generate a synthetic depth image."""
        # Create a simple depth pattern (distance field)
        depth = np.zeros((self.image_height, self.image_width), dtype=np.float32)
        
        center_x, center_y = self.image_width // 2, self.image_height // 2
        for i in range(self.image_height):
            for j in range(self.image_width):
                # Distance from center, normalized and scaled
                dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
                depth[i, j] = 1.0 + 2.0 * dist / max(self.image_width, self.image_height)
                
        # Add some noise
        depth += 0.1 * np.random.randn(self.image_height, self.image_width)
        depth = np.clip(depth, 0.1, 5.0)  # Reasonable depth range
        
        return depth

    # ------------ observation ------------

    def get_raw_observation(self) -> RawObservation:
        """Generate a synthetic observation."""
        if not self.is_connected:
            raise RuntimeError("[FakeRobot] Cannot get observation - robot not connected")
        
        # Update simulation
        self._update_joint_simulation()
        
        # Generate joint data
        body_q, right_arm_q = self._split_joints(self.current_joint_angles)
        
        # Generate end-effector pose
        ee_pose_right = self._simulate_forward_kinematics()
        
        # Generate synthetic images
        rgb = self._generate_synthetic_image()
        
        # Generate depth images if available
        head_depth = None
        right_arm_depth = None
        
        if self.head_depth_available:
            head_depth = self._generate_synthetic_depth()
            
        if self.right_arm_depth_available:
            right_arm_depth = self._generate_synthetic_depth()
        else:
            # Right wrist depth cannot be grabbed -> use all zeros
            right_arm_depth = np.zeros((self.image_height, self.image_width), dtype=np.float32)

        return RawObservation(
            head_top_rgb=rgb.copy(),
            right_wrist_rgb=rgb.copy(),
            head_top_depth=head_depth,
            right_wrist_depth=right_arm_depth,
            right_arm_q=right_arm_q,
            body_q=body_q,
            right_arm_joint_names=self.right_arm_joint_names,
            body_joint_names=self.body_joint_names,
        )

    # ------------ control ------------

    def move_body_and_right_arm(self, body_q: np.ndarray, right_arm_q: np.ndarray, duration: float = 1.0) -> bool:
        """Simulate movement of body and right arm joints."""
        if not self.is_connected:
            raise RuntimeError("[FakeRobot] Cannot move - robot not connected")
        
        body_q = np.asarray(body_q, dtype=np.float32)
        right_arm_q = np.asarray(right_arm_q, dtype=np.float32)
        
        if len(body_q) != len(self.body_indices):
            raise ValueError(f"body_q length {len(body_q)} != body_indices {len(self.body_indices)}")
        if len(right_arm_q) != len(self.right_arm_indices):
            raise ValueError(f"right_arm_q length {len(right_arm_q)} != right_arm_indices {len(self.right_arm_indices)}")
        
        # Update target angles
        self.target_joint_angles[self.body_indices] = body_q
        self.target_joint_angles[self.right_arm_indices] = right_arm_q
        
        # Start movement simulation
        self.move_start_time = time.time()
        self.move_duration = duration
        self.move_start_angles = self.current_joint_angles.copy()
        
        print(f"[FakeRobot] Starting movement (duration: {duration}s)")
        print(f"[FakeRobot] Target body_q: {body_q}")
        print(f"[FakeRobot] Target right_arm_q: {right_arm_q}")
        
        return True

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

    # ------------ additional utilities ------------

    def is_moving(self) -> bool:
        """Check if robot is currently executing a movement."""
        return self.move_start_time is not None

    def get_current_joint_angles(self) -> np.ndarray:
        """Get current joint angles."""
        self._update_joint_simulation()
        return self.current_joint_angles.copy()

    def wait_for_movement_completion(self, timeout: float = 10.0) -> bool:
        """Wait for current movement to complete."""
        start_time = time.time()
        while self.is_moving():
            if time.time() - start_time > timeout:
                print(f"[FakeRobot] Movement timeout after {timeout}s")
                return False
            time.sleep(0.01)  # Small sleep to avoid busy waiting
        return True

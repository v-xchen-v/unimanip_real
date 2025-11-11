"""
Robot SDK Wrapper

This module defines the RobotSDKWrapper class that provides a standardized interface
for different robot platforms. Users should implement the abstract methods for their
specific robot SDK.

The wrapper handles:
- Robot connection and disconnection
- Joint and head movement
- State reading (joint angles, poses, etc.)
- Camera image capture
- Camera calibration retrieval
"""

import time
from typing import Dict, Any
from dataclasses import dataclass
import numpy as np
import cv2


@dataclass
class RobotState:
    """Current state of the robot."""
    joint_angles: np.ndarray      # (num_joints,) 
    head_angles: np.ndarray       # (2,) - pan, tilt
    end_position: np.ndarray      # (3,) - x, y, z
    end_orientation: np.ndarray   # (4,) - quaternion w, x, y, z
    waist_angles: np.ndarray      # (2,) - waist pan, tilt
    timestamp: float


@dataclass
class CameraCalibration:
    """Camera calibration parameters."""
    intrinsic: np.ndarray         # (3, 3) intrinsic matrix
    camera_in_head: np.ndarray    # (4, 4) transformation matrix


class RobotSDKWrapper:
    """
    Wrapper class for robot SDK API calls.
    
    This is a base class that should be extended for specific robot platforms.
    Users should implement the abstract methods marked with TODO comments.
    """
    
    def __init__(self, robot_config: Dict[str, Any]):
        """
        Initialize robot SDK connection.
        
        Args:
            robot_config: Robot configuration parameters
        """
        self.config = robot_config
        self.is_connected = False
        self.num_joints = robot_config.get('num_joints', 14)  # Default to 14 joints
        
        # TODO: Initialize actual robot SDK here
        print("Initializing robot SDK...")
        
    def connect(self) -> bool:
        """
        Connect to the robot.
        
        Returns:
            True if connection successful
        """
        # TODO: Implement actual robot connection
        print("Connecting to robot...")
        self.is_connected = True
        return True
    
    def disconnect(self):
        """Disconnect from robot."""
        # TODO: Implement actual robot disconnection
        print("Disconnecting from robot...")
        self.is_connected = False
    
    def move_to_joint_angles(self, joint_angles: np.ndarray, duration: float = 1.0) -> bool:
        """
        Move robot to specified joint angles.
        
        Args:
            joint_angles: Target joint angles (num_joints,)
            duration: Time to reach target position
            
        Returns:
            True if movement successful
        """
        # TODO: Implement actual robot movement
        if len(joint_angles) != self.num_joints:
            raise ValueError(f"Expected {self.num_joints} joint angles, got {len(joint_angles)}")
        
        print(f"Moving to joint angles: {joint_angles[:3]}... over {duration}s")
        time.sleep(duration)  # Simulate movement time
        return True
    
    def move_head(self, pan: float, tilt: float, duration: float = 1.0) -> bool:
        """
        Move robot head to specified angles.
        
        Args:
            pan: Head pan angle in radians
            tilt: Head tilt angle in radians
            duration: Time to reach target position
            
        Returns:
            True if movement successful
        """
        # TODO: Implement actual head movement
        print(f"Moving head to pan={pan:.3f}, tilt={tilt:.3f} over {duration}s")
        time.sleep(duration)  # Simulate movement time
        return True
    
    def get_current_state(self) -> RobotState:
        """
        Get current robot state.
        
        Returns:
            Current robot state
        """
        # TODO: Implement actual state reading
        # For now, return dummy data
        current_time = time.time()
        
        return RobotState(
            joint_angles=np.random.uniform(-np.pi, np.pi, self.num_joints),
            head_angles=np.random.uniform(-np.pi/4, np.pi/4, 2),
            end_position=np.random.uniform(-1.0, 1.0, 3),
            end_orientation=np.array([1.0, 0.0, 0.0, 0.0]),  # Identity quaternion
            waist_angles=np.random.uniform(-np.pi/4, np.pi/4, 2),
            timestamp=current_time
        )
    
    def capture_image(self) -> np.ndarray:
        """
        Capture image from robot's camera.
        
        Returns:
            RGB image as numpy array (H, W, 3)
        """
        # TODO: Implement actual image capture
        # For now, return synthetic image
        height, width = 480, 640
        image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        
        # Add some pattern to make it recognizable
        cv2.rectangle(image, (50, 50), (150, 150), (255, 0, 0), 2)
        cv2.putText(image, f"t={time.time():.1f}", (200, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return image
    
    def get_camera_calibration(self) -> CameraCalibration:
        """
        Get camera calibration parameters.
        
        Returns:
            Camera calibration data
        """
        # TODO: Implement actual calibration retrieval
        # Return typical camera parameters
        intrinsic = np.array([
            [525.0, 0.0, 320.0],
            [0.0, 525.0, 240.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)
        
        # Camera positioned 10cm forward and 5cm up from head center
        camera_in_head = np.eye(4, dtype=np.float32)
        camera_in_head[:3, 3] = [0.1, 0.0, 0.05]
        
        return CameraCalibration(
            intrinsic=intrinsic,
            camera_in_head=camera_in_head
        )
    
    def is_motion_complete(self) -> bool:
        """
        Check if robot has finished current motion.
        
        Returns:
            True if motion is complete
        """
        # TODO: Implement actual motion status check
        return True
    
    def home_robot(self) -> bool:
        """
        Move robot to home position.
        
        Returns:
            True if successful
        """
        # TODO: Implement actual homing
        print("Moving robot to home position...")
        home_angles = np.zeros(self.num_joints)
        return self.move_to_joint_angles(home_angles, duration=2.0)
    
    def enable_robot(self) -> bool:
        """
        Enable robot motors and systems.
        
        Returns:
            True if successful
        """
        # TODO: Implement actual robot enabling
        print("Enabling robot...")
        return True
    
    def disable_robot(self) -> bool:
        """
        Disable robot motors (safe mode).
        
        Returns:
            True if successful
        """
        # TODO: Implement actual robot disabling
        print("Disabling robot...")
        return True
    
    def emergency_stop(self) -> bool:
        """
        Emergency stop - immediately halt all motion.
        
        Returns:
            True if successful
        """
        # TODO: Implement actual emergency stop
        print("EMERGENCY STOP!")
        return True
    
    def get_joint_limits(self) -> Dict[str, np.ndarray]:
        """
        Get joint angle limits.
        
        Returns:
            Dictionary with 'min' and 'max' joint limits
        """
        # TODO: Implement actual joint limits retrieval
        return {
            'min': np.full(self.num_joints, -np.pi),
            'max': np.full(self.num_joints, np.pi)
        }
    
    def validate_joint_angles(self, joint_angles: np.ndarray) -> bool:
        """
        Validate that joint angles are within limits.
        
        Args:
            joint_angles: Joint angles to validate
            
        Returns:
            True if all angles are within limits
        """
        limits = self.get_joint_limits()
        return np.all(joint_angles >= limits['min']) and np.all(joint_angles <= limits['max'])


class DryRunRobotSDK(RobotSDKWrapper):
    """
    Dry run robot SDK that generates dummy data for testing without hardware.
    
    This implementation simulates robot movements and generates synthetic data
    that follows realistic patterns, allowing full testing of the recording
    pipeline without requiring actual robot hardware.
    """
    
    def __init__(self, robot_config: Dict[str, Any]):
        super().__init__(robot_config)
        
        # Simulation state
        self.current_joint_angles = np.zeros(self.num_joints, dtype=np.float32)
        self.current_head_angles = np.zeros(2, dtype=np.float32)
        self.current_waist_angles = np.zeros(2, dtype=np.float32)
        self.target_joint_angles = np.zeros(self.num_joints, dtype=np.float32)
        self.target_head_angles = np.zeros(2, dtype=np.float32)
        
        # Movement simulation
        self.movement_start_time = 0.0
        self.movement_duration = 0.0
        self.is_moving = False
        self.start_joint_angles = np.zeros(self.num_joints, dtype=np.float32)
        self.start_head_angles = np.zeros(2, dtype=np.float32)
        
        # Image generation parameters
        self.image_counter = 0
        self.image_width = robot_config.get('image_width', 640)
        self.image_height = robot_config.get('image_height', 480)
        
        print("Dry run robot SDK initialized - no hardware required")
    
    def connect(self) -> bool:
        """Simulate robot connection."""
        print("Simulating robot connection...")
        time.sleep(0.5)  # Simulate connection delay
        self.is_connected = True
        print("Dry run robot connected successfully")
        return True
    
    def disconnect(self):
        """Simulate robot disconnection."""
        print("Simulating robot disconnection...")
        self.is_connected = False
    
    def move_to_joint_angles(self, joint_angles: np.ndarray, duration: float = 1.0) -> bool:
        """Simulate robot movement with smooth interpolation."""
        if len(joint_angles) != self.num_joints:
            raise ValueError(f"Expected {self.num_joints} joint angles, got {len(joint_angles)}")
        
        if not self.validate_joint_angles(joint_angles):
            print("Warning: Joint angles out of range in dry run mode")
            # Clamp to limits for simulation
            limits = self.get_joint_limits()
            joint_angles = np.clip(joint_angles, limits['min'], limits['max'])
        
        # Start movement simulation
        self.start_joint_angles = self.current_joint_angles.copy()
        self.target_joint_angles = joint_angles.copy()
        self.movement_start_time = time.time()
        self.movement_duration = duration
        self.is_moving = True
        
        print(f"Simulating movement to joint angles over {duration}s")
        # Don't sleep here - let the motion complete gradually
        return True
    
    def move_head(self, pan: float, tilt: float, duration: float = 1.0) -> bool:
        """Simulate head movement."""
        # Start head movement simulation
        self.start_head_angles = self.current_head_angles.copy()
        self.target_head_angles = np.array([pan, tilt], dtype=np.float32)
        
        print(f"Simulating head movement to pan={pan:.3f}, tilt={tilt:.3f}")
        return True
    
    def _update_simulation_state(self):
        """Update simulated robot state based on time."""
        current_time = time.time()
        
        if self.is_moving:
            # Calculate interpolation factor
            elapsed = current_time - self.movement_start_time
            t = min(elapsed / self.movement_duration, 1.0)
            
            # Smooth interpolation (ease-in-out)
            t_smooth = 3 * t * t - 2 * t * t * t
            
            # Interpolate joint angles
            self.current_joint_angles = (
                self.start_joint_angles + 
                t_smooth * (self.target_joint_angles - self.start_joint_angles)
            )
            
            # Interpolate head angles
            self.current_head_angles = (
                self.start_head_angles + 
                t_smooth * (self.target_head_angles - self.start_head_angles)
            )
            
            # Check if movement is complete
            if t >= 1.0:
                self.is_moving = False
                self.current_joint_angles = self.target_joint_angles.copy()
                self.current_head_angles = self.target_head_angles.copy()
    
    def get_current_state(self) -> RobotState:
        """Get simulated robot state."""
        self._update_simulation_state()
        
        current_time = time.time()
        
        # Simulate end effector position based on joint angles
        # Simple approximation: end effector moves with arm joints
        arm_extension = np.mean(self.current_joint_angles[:3]) * 0.5 + 0.3
        end_position = np.array([
            arm_extension * np.cos(self.current_joint_angles[0]),
            arm_extension * np.sin(self.current_joint_angles[0]),
            0.5 + self.current_joint_angles[1] * 0.2
        ], dtype=np.float32)
        
        # Simple end effector orientation (identity quaternion with slight rotation)
        end_orientation = np.array([
            np.cos(self.current_joint_angles[2] * 0.5),
            0.0,
            0.0,
            np.sin(self.current_joint_angles[2] * 0.5)
        ], dtype=np.float32)
        
        return RobotState(
            joint_angles=self.current_joint_angles.copy(),
            head_angles=self.current_head_angles.copy(),
            end_position=end_position,
            end_orientation=end_orientation,
            waist_angles=self.current_waist_angles.copy(),
            timestamp=current_time
        )
    
    def capture_image(self) -> np.ndarray:
        """Generate synthetic camera image."""
        self._update_simulation_state()
        
        # Create base image with gradient background
        image = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)
        
        # Create gradient background
        for y in range(self.image_height):
            for x in range(self.image_width):
                image[y, x, 0] = int(50 + (x / self.image_width) * 100)  # Red gradient
                image[y, x, 1] = int(30 + (y / self.image_height) * 80)  # Green gradient
                image[y, x, 2] = 120  # Constant blue
        
        # Add moving elements based on joint angles
        joint_sum = np.sum(np.abs(self.current_joint_angles))
        circle_x = int(320 + np.sin(joint_sum) * 100)
        circle_y = int(240 + np.cos(joint_sum) * 80)
        cv2.circle(image, (circle_x, circle_y), 30, (255, 255, 0), -1)
        
        # Add head-dependent rectangle
        head_x = int(160 + self.current_head_angles[0] * 200)
        head_y = int(120 + self.current_head_angles[1] * 100)
        cv2.rectangle(image, 
                     (head_x - 20, head_y - 15), 
                     (head_x + 20, head_y + 15), 
                     (0, 255, 255), 2)
        
        # Add frame counter and timestamp
        cv2.putText(image, f"Frame: {self.image_counter}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(image, f"Time: {time.time():.1f}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(image, "DRY RUN MODE", 
                   (self.image_width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Add joint angle visualization
        joint_viz_y = 90
        for i in range(min(5, self.num_joints)):  # Show first 5 joints
            angle_text = f"J{i}: {self.current_joint_angles[i]:.2f}"
            cv2.putText(image, angle_text, 
                       (10, joint_viz_y + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        self.image_counter += 1
        return image
    
    def get_camera_calibration(self) -> CameraCalibration:
        """Return simulated camera calibration."""
        # Realistic camera parameters for the simulated camera
        focal_length = 525.0
        cx = self.image_width / 2.0
        cy = self.image_height / 2.0
        
        intrinsic = np.array([
            [focal_length, 0.0, cx],
            [0.0, focal_length, cy],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)
        
        # Camera positioned relative to head
        camera_in_head = np.eye(4, dtype=np.float32)
        camera_in_head[:3, 3] = [0.08, 0.0, 0.03]  # 8cm forward, 3cm up
        
        return CameraCalibration(
            intrinsic=intrinsic,
            camera_in_head=camera_in_head
        )
    
    def is_motion_complete(self) -> bool:
        """Check if simulated motion is complete."""
        self._update_simulation_state()
        return not self.is_moving
    
    def home_robot(self) -> bool:
        """Simulate moving to home position."""
        print("Simulating robot homing...")
        home_angles = np.zeros(self.num_joints)
        return self.move_to_joint_angles(home_angles, duration=2.0)
    
    def enable_robot(self) -> bool:
        """Simulate enabling robot."""
        print("Simulating robot enable...")
        return True
    
    def disable_robot(self) -> bool:
        """Simulate disabling robot."""
        print("Simulating robot disable...")
        return True
    
    def emergency_stop(self) -> bool:
        """Simulate emergency stop."""
        print("Simulating EMERGENCY STOP!")
        self.is_moving = False
        return True


class A2DRobotSDK(RobotSDKWrapper):
    """
    A2D Robot SDK implementation using the a2d_sdk.robot.RobotDds API.
    
    This implementation uses the actual A2D robot SDK for controlling the humanoid robot.
    """
    
    def __init__(self, robot_config: Dict[str, Any]):
        super().__init__(robot_config)
        
        try:
            from a2d_sdk.robot import RobotDds as Robot
            self.robot_api = Robot()
            self.initialization_delay = robot_config.get('initialization_delay', 5.0)
            print(f"A2D Robot SDK initialized, waiting {self.initialization_delay}s for robot initialization...")
        except ImportError:
            print("Warning: a2d_sdk not found. Please install the A2D SDK or use simulation mode.")
            self.robot_api = None
        
    def connect(self) -> bool:
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
    
    def move_to_joint_angles(self, joint_angles: np.ndarray, duration: float = 1.0) -> bool:
        """Move robot arms using A2D SDK."""
        if not self.validate_joint_angles(joint_angles):
            print("Joint angles out of range!")
            return False
        
        if self.robot_api is None:
            print("Robot API not available")
            return False
            
        try:
            # Convert to list for API compatibility
            arm_positions = joint_angles.tolist()
            
            # Use reset method for precise positioning (as shown in execute_traj.py)
            self.robot_api.reset(
                arm_positions=arm_positions,
                gripper_positions=[0.0, 0.0],  # Keep grippers closed
                hand_positions=None,
                waist_positions=None,  # Will use current waist position
                head_positions=None    # Will use current head position
            )
            
            # Wait for movement to complete
            time.sleep(duration)
            print(f"Moved {self.num_joints} arm joints to target positions")
            return True
        except Exception as e:
            print(f"Arm movement failed: {e}")
            return False
    
    def move_head(self, pan: float, tilt: float, duration: float = 1.0) -> bool:
        """Move robot head using A2D SDK."""
        if self.robot_api is None:
            print("Robot API not available")
            return False
            
        try:
            head_pos = [pan, tilt]  # yaw (pan), pitch (tilt)
            self.robot_api.move_head(head_pos)
            time.sleep(duration)
            print(f"Moved head to pan={pan:.3f}, tilt={tilt:.3f}")
            return True
        except Exception as e:
            print(f"Head movement failed: {e}")
            return False
    
    def get_current_state(self) -> RobotState:
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
            
            # For end effector position and orientation, we would need forward kinematics
            # For now, provide placeholder values based on joint angles
            end_position = np.array([0.3, 0.0, 0.5], dtype=np.float32)  # Placeholder
            end_orientation = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)  # Identity quaternion
            
            return RobotState(
                joint_angles=joint_angles,
                head_angles=head_angles,
                end_position=end_position,
                end_orientation=end_orientation,
                waist_angles=waist_angles,
                timestamp=current_time
            )
        except Exception as e:
            print(f"Failed to get robot state: {e}")
            # Return dummy data as fallback
            return super().get_current_state()
    
    def capture_image(self) -> np.ndarray:
        """Capture image from robot camera."""
        # TODO: Implement camera capture when camera API is available
        # For now, return synthetic image
        try:
            # If camera API becomes available:
            # image = self.robot_api.get_camera_image()
            # return image
            
            print("Camera capture not yet implemented, returning synthetic image")
            return super().capture_image()
        except Exception as e:
            print(f"Failed to capture image: {e}")
            return super().capture_image()
    
    def home_robot(self) -> bool:
        """Move robot to home position using A2D SDK."""
        if self.robot_api is None:
            print("Robot API not available")
            return False
            
        try:
            print("Moving robot to home position...")
            
            # Home position for 14 arm joints (7 left + 7 right)
            home_arm_angles = [0.0] * 14
            
            # Home position for head [yaw=0, pitch=0]
            home_head_angles = [0.0, 0.0]
            
            # Home position for waist [pitch=0, height=27cm]
            home_waist_angles = [0.0, 27.0]
            
            # Use reset method to go to home position
            self.robot_api.reset(
                arm_positions=home_arm_angles,
                gripper_positions=[0.0, 0.0],
                hand_positions=None,
                waist_positions=home_waist_angles,
                head_positions=home_head_angles
            )
            
            time.sleep(3.0)  # Wait for homing to complete
            print("Robot homed successfully")
            return True
        except Exception as e:
            print(f"Homing failed: {e}")
            return False
    
    def move_waist(self, waist_angles: np.ndarray, duration: float = 1.0) -> bool:
        """
        Move robot waist using A2D SDK.
        
        Args:
            waist_angles: [pitch, height] where height is in meters
            duration: Time to reach target position
            
        Returns:
            True if movement successful
        """
        if self.robot_api is None:
            print("Robot API not available")
            return False
            
        try:
            # Convert height from meters to centimeters for API
            waist_pos = [waist_angles[0], waist_angles[1] * 100.0]
            self.robot_api.move_waist(waist_pos)
            time.sleep(duration)
            print(f"Moved waist to pitch={waist_angles[0]:.3f}, height={waist_angles[1]:.3f}m")
            return True
        except Exception as e:
            print(f"Waist movement failed: {e}")
            return False
    
    def move_gripper(self, gripper_positions: np.ndarray, duration: float = 1.0) -> bool:
        """
        Move robot grippers using A2D SDK.
        
        Args:
            gripper_positions: [left, right] gripper positions (0-1)
            duration: Time to reach target position
            
        Returns:
            True if movement successful
        """
        if self.robot_api is None:
            print("Robot API not available")
            return False
            
        try:
            gripper_pos = gripper_positions.tolist()
            self.robot_api.move_gripper(gripper_pos)
            time.sleep(duration)
            print(f"Moved grippers to positions: {gripper_pos}")
            return True
        except Exception as e:
            print(f"Gripper movement failed: {e}")
            return False
    
    def get_joint_limits(self) -> Dict[str, np.ndarray]:
        """Get joint limits for A2D robot."""
        # TODO: Get actual joint limits from robot specification
        # For now, use conservative limits
        return {
            'min': np.array([-2.5] * 14, dtype=np.float32),  # -2.5 rad for all joints
            'max': np.array([2.5] * 14, dtype=np.float32)    # +2.5 rad for all joints
        }


# Enhanced ExampleRobotSDK with better simulation features
class ExampleRobotSDK(RobotSDKWrapper):
    """
    Enhanced example implementation for testing and reference.
    
    This provides a more complete simulation that mimics the A2D robot behavior
    without requiring the actual hardware or SDK.
    """
    
    def __init__(self, robot_config: Dict[str, Any]):
        super().__init__(robot_config)
        
        # Simulate robot state
        self._current_joint_angles = np.zeros(self.num_joints, dtype=np.float32)
        self._current_head_angles = np.zeros(2, dtype=np.float32)  # pan, tilt
        self._current_waist_angles = np.array([0.0, 0.27], dtype=np.float32)  # pitch, height(m)
        self._current_gripper_positions = np.zeros(2, dtype=np.float32)
        
        print("Example robot SDK initialized (enhanced simulation mode)")
        
    def connect(self) -> bool:
        """Connect to example robot."""
        print("Connected to example robot (enhanced simulation)")
        self.is_connected = True
        return True
    
    def move_to_joint_angles(self, joint_angles: np.ndarray, duration: float = 1.0) -> bool:
        """Simulate robot arm movement."""
        if not self.validate_joint_angles(joint_angles):
            print("Joint angles out of range!")
            return False
        
        try:
            print(f"[SIM] Moving {self.num_joints} joints to target positions: {joint_angles[:3]}...")
            
            # Simulate gradual movement
            start_angles = self._current_joint_angles.copy()
            steps = max(10, int(duration * 10))  # 10 steps per second
            
            for i in range(steps):
                # Linear interpolation
                alpha = (i + 1) / steps
                self._current_joint_angles = (1 - alpha) * start_angles + alpha * joint_angles
                time.sleep(duration / steps)
            
            self._current_joint_angles = joint_angles.copy()
            print(f"[SIM] Joint movement completed")
            return True
        except Exception as e:
            print(f"[SIM] Movement failed: {e}")
            return False
    
    def move_head(self, pan: float, tilt: float, duration: float = 1.0) -> bool:
        """Simulate head movement."""
        try:
            print(f"[SIM] Moving head to pan={pan:.3f}, tilt={tilt:.3f}")
            
            # Simulate gradual movement
            start_angles = self._current_head_angles.copy()
            target_angles = np.array([pan, tilt], dtype=np.float32)
            steps = max(5, int(duration * 10))
            
            for i in range(steps):
                alpha = (i + 1) / steps
                self._current_head_angles = (1 - alpha) * start_angles + alpha * target_angles
                time.sleep(duration / steps)
            
            self._current_head_angles = target_angles
            print(f"[SIM] Head movement completed")
            return True
        except Exception as e:
            print(f"[SIM] Head movement failed: {e}")
            return False
    
    def move_waist(self, waist_angles: np.ndarray, duration: float = 1.0) -> bool:
        """Simulate waist movement."""
        try:
            print(f"[SIM] Moving waist to pitch={waist_angles[0]:.3f}, height={waist_angles[1]:.3f}m")
            
            # Validate height range (2cm to 53cm converted to meters)
            if not (0.02 <= waist_angles[1] <= 0.53):
                print(f"Waist height {waist_angles[1]:.3f}m out of range [0.02, 0.53]")
                return False
            
            start_angles = self._current_waist_angles.copy()
            steps = max(5, int(duration * 10))
            
            for i in range(steps):
                alpha = (i + 1) / steps
                self._current_waist_angles = (1 - alpha) * start_angles + alpha * waist_angles
                time.sleep(duration / steps)
            
            self._current_waist_angles = waist_angles.copy()
            print(f"[SIM] Waist movement completed")
            return True
        except Exception as e:
            print(f"[SIM] Waist movement failed: {e}")
            return False
    
    def get_current_state(self) -> RobotState:
        """Get simulated robot state."""
        try:
            current_time = time.time()
            
            # Add small random noise to simulate sensor readings
            noise_scale = 0.001  # 0.001 radians ≈ 0.06 degrees
            
            joint_angles = self._current_joint_angles + np.random.normal(0, noise_scale, self.num_joints)
            head_angles = self._current_head_angles + np.random.normal(0, noise_scale, 2)
            waist_angles = self._current_waist_angles + np.random.normal(0, noise_scale, 2)
            
            # Simulate end effector position based on joint angles (very simplified)
            # In reality, this would require forward kinematics
            end_position = np.array([
                0.3 + 0.1 * np.sin(joint_angles[0]),  # X varies with first joint
                0.2 * np.sin(joint_angles[1]),        # Y varies with second joint  
                0.5 + 0.1 * np.cos(joint_angles[2])   # Z varies with third joint
            ], dtype=np.float32)
            
            # Simple orientation (identity quaternion with small rotation)
            end_orientation = np.array([1.0, 0.01, 0.01, 0.01], dtype=np.float32)
            end_orientation = end_orientation / np.linalg.norm(end_orientation)  # Normalize
            
            return RobotState(
                joint_angles=joint_angles.astype(np.float32),
                head_angles=head_angles.astype(np.float32),
                end_position=end_position,
                end_orientation=end_orientation,
                waist_angles=waist_angles.astype(np.float32),
                timestamp=current_time
            )
        except Exception as e:
            print(f"[SIM] Failed to get state: {e}")
            return super().get_current_state()
    
    def capture_image(self) -> np.ndarray:
        """Generate realistic simulated camera image."""
        try:
            # Create more realistic simulation image
            height, width = 480, 640
            
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
            
            # Add timestamp and joint angle info
            timestamp_str = f"t={time.time():.1f}"
            joint_info = f"J0={self._current_joint_angles[0]:.2f}"
            head_info = f"H=({self._current_head_angles[0]:.2f},{self._current_head_angles[1]:.2f})"
            
            cv2.putText(image, timestamp_str, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(image, joint_info, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(image, head_info, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            return image
        except Exception as e:
            print(f"[SIM] Failed to capture image: {e}")
            return super().capture_image()
    
    def home_robot(self) -> bool:
        """Move robot to home position."""
        try:
            print("[SIM] Moving robot to home position...")
            
            home_joint_angles = np.zeros(self.num_joints)
            home_head_angles = np.array([0.0, 0.0])
            home_waist_angles = np.array([0.0, 0.27])  # 27cm height
            
            # Simulate homing sequence
            success = True
            success &= self.move_to_joint_angles(home_joint_angles, duration=2.0)
            success &= self.move_head(home_head_angles[0], home_head_angles[1], duration=1.0)
            success &= self.move_waist(home_waist_angles, duration=1.5)
            
            if success:
                print("[SIM] Robot homed successfully")
            else:
                print("[SIM] Homing failed")
            
            return success
        except Exception as e:
            print(f"[SIM] Homing failed: {e}")
            return False
    
    def get_joint_limits(self) -> Dict[str, np.ndarray]:
        """Get realistic joint limits."""
        # More realistic joint limits for a humanoid robot
        # Left arm (7 joints) + Right arm (7 joints)
        min_limits = np.array([
            -2.8, -1.5, -2.8, -2.0, -2.8, -1.0, -2.8,  # Left arm
            -2.8, -1.5, -2.8, -2.0, -2.8, -1.0, -2.8   # Right arm
        ], dtype=np.float32)
        
        max_limits = np.array([
            2.8, 1.5, 2.8, 2.0, 2.8, 1.0, 2.8,  # Left arm  
            2.8, 1.5, 2.8, 2.0, 2.8, 1.0, 2.8   # Right arm
        ], dtype=np.float32)
        
        return {
            'min': min_limits,
            'max': max_limits
        }


# Factory function to create robot SDK instances
def create_robot_sdk(robot_type: str, robot_config: Dict[str, Any]) -> RobotSDKWrapper:
    """
    Factory function to create robot SDK instances.
    
    Args:
        robot_type: Type of robot ('a2d', 'example', 'simulation', etc.)
        robot_config: Robot configuration parameters
        
    Returns:
        RobotSDKWrapper instance
    """
    robot_type = robot_type.lower()
    
    if robot_type == 'a2d':
        return A2DRobotSDK(robot_config)
    elif robot_type == 'example':
        return ExampleRobotSDK(robot_config)
    elif robot_type == 'simulation':
        return RobotSDKWrapper(robot_config)  # Use base class for basic simulation
    elif robot_type == 'dry_run' or robot_type == 'dryrun' or robot_type == 'dry-run':
        return DryRunRobotSDK(robot_config)
    else:
        # Add your robot types here
        # elif robot_type == 'your_robot':
        #     return YourRobotSDK(robot_config)
        print(f"Warning: Unknown robot type '{robot_type}'. Supported types: 'a2d', 'example', 'simulation', 'dry_run'")
        print("Falling back to example robot SDK...")
        return ExampleRobotSDK(robot_config)


if __name__ == "__main__":
    # Test both robot SDKs
    config = {
        'num_joints': 14,
        'robot_type': 'a2d',
        'initialization_delay': 5.0
    }
    
    # print("=" * 60)
    # print("Testing Robot SDK Implementations")
    # print("=" * 60)
    
    # # Test A2D Robot SDK
    # print("\n1. Testing A2D Robot SDK...")
    # try:
    #     a2d_robot = create_robot_sdk('a2d', config)
        
    #     if a2d_robot.connect():
    #         print("✓ A2D Robot connected successfully")
            
    #         # Test joint movement
    #         test_angles = np.array([0.1, -0.1, 0.2, -0.2, 0.0, 0.1, -0.1] * 2, dtype=np.float32)  # 14 joints
    #         success = a2d_robot.move_to_joint_angles(test_angles, duration=1.0)
    #         print(f"✓ Joint movement: {'Success' if success else 'Failed'}")
            
    #         # Test head movement
    #         success = a2d_robot.move_head(0.2, 0.1, duration=0.5)
    #         print(f"✓ Head movement: {'Success' if success else 'Failed'}")
            
    #         # Test state reading
    #         state = a2d_robot.get_current_state()
    #         print(f"✓ State reading: {state.joint_angles.shape} joints, head={state.head_angles}")
            
    #         # Test image capture
    #         image = a2d_robot.capture_image()
    #         print(f"✓ Image capture: {image.shape}")
            
    #         # Test homing
    #         success = a2d_robot.home_robot()
    #         print(f"✓ Homing: {'Success' if success else 'Failed'}")
            
    #         a2d_robot.disconnect()
    #     else:
    #         print("✗ Failed to connect to A2D robot")
    # except Exception as e:
    #     print(f"✗ A2D Robot test failed: {e}")
    
    # Test Example Robot SDK
    print("\n2. Testing Example Robot SDK (Enhanced Simulation)...")
    try:
        example_robot = create_robot_sdk('example', config)
        
        if example_robot.connect():
            print("✓ Example Robot connected successfully")
            
            # Test joint movement with gradual motion
            test_angles = np.array([0.3, -0.3, 0.5, -0.5, 0.2, 0.3, -0.2] * 2, dtype=np.float32)
            success = example_robot.move_to_joint_angles(test_angles, duration=0.5)
            print(f"✓ Joint movement: {'Success' if success else 'Failed'}")
            
            # Test head movement
            success = example_robot.move_head(0.5, -0.2, duration=0.3)
            print(f"✓ Head movement: {'Success' if success else 'Failed'}")
            
            # Test waist movement
            success = example_robot.move_waist(np.array([0.1, 0.35]), duration=0.4)
            print(f"✓ Waist movement: {'Success' if success else 'Failed'}")
            
            # Test state reading
            state = example_robot.get_current_state()
            print(f"✓ State reading: joints={state.joint_angles[:3]}, head={state.head_angles}, waist={state.waist_angles}")
            
            # Test enhanced image capture
            image = example_robot.capture_image()
            print(f"✓ Enhanced image capture: {image.shape}")
            
            # Test homing sequence
            success = example_robot.home_robot()
            print(f"✓ Homing sequence: {'Success' if success else 'Failed'}")
            
            example_robot.disconnect()
        else:
            print("✗ Failed to connect to example robot")
    except Exception as e:
        print(f"✗ Example Robot test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Robot SDK Tests Completed")
    print("=" * 60)
    
    print("\nUsage examples:")
    print("1. A2D Robot:")
    print("   robot = create_robot_sdk('a2d', config)")
    print("   robot.connect()")
    print("   robot.move_to_joint_angles(angles)")
    print()
    print("2. Example/Simulation Robot:")  
    print("   robot = create_robot_sdk('example', config)")
    print("   robot.connect()")
    print("   robot.move_to_joint_angles(angles)")
    print()
    print("3. Basic Simulation:")
    print("   robot = create_robot_sdk('simulation', config)")
    print("   robot.connect()")
    print("   robot.move_to_joint_angles(angles)")
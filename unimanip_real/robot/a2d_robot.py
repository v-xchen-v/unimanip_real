from .base_robot import BaseRobotSDK
import time
from typing import Dict, Any
import numpy as np
from dataclasses import dataclass
from ..constrants import get_reset_joint_cfg
from ..control.observation import RawObservation



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
    def __init__(self, config=None, sim_only=False):
        super().__init__(config or {})
        self.sim_only = sim_only  # Flag to enable simulation-only mode
        self.simulated_joints = {}  # Store simulated joint positions
        self.initialization_delay = 3.0  # Default initialization delay
        self.is_connected = False
        try:
            # Initialize A2D SDK robot here
            from a2d_sdk.robot import RobotDds
            self.robot_api = RobotDds()
            print(f"A2D Robot SDK initialized, waiting {self.initialization_delay}s for robot initialization...")
        
            from a2d_sdk.robot import CosineCamera as Camera
            self.robot_camera_api = Camera([
                "head", # head top rgb
                "head_depth", # head depth
                "hand_right", # right hand rgb
            ])
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
        
        self.left_arm_joint_names = [
            "idx21_arm_l_joint1",
            "idx22_arm_l_joint2",
            "idx23_arm_l_joint3",
            "idx24_arm_l_joint4",
            "idx25_arm_l_joint5",
            "idx26_arm_l_joint6",
            "idx27_arm_l_joint7",
        ]
        self.arm_joint_names = self.left_arm_joint_names + self.right_arm_joint_names
        
        self.waist_joint_names = [
            "idx01_body_joint1",  # waist pan
            "idx02_body_joint2",  # waist height
        ]
        
        self.head_joint_names = [
            "idx11_head_joint1",  # head yaw
            "idx12_head_joint2",  # head pitch
        ]

        self.gripper_joint_names = [
            "idx41_gripper_l_outer_joint1",  # left gripper
            "idx81_gripper_r_outer_joint1",  # right gripper
        ]
        self.activate_joint_names = self.right_arm_joint_names
        self.chain_joint_names = self.waist_joint_names + self.right_arm_joint_names
        self.default_left_arm_q = get_reset_joint_cfg("open_laptop", left_arm_only=True)
        
        # Initialize simulated joint positions to zero
        if self.sim_only:
            self._initialize_simulated_joints()
            
        # initialize a urdf inspector for visualization if needed
        from robot_kinematics.urdf.inspector import FullURDFInspector
        # Use urdf inspector for simulation
        #TODO: make urdf path in configuration
        self.urdf_inspector = FullURDFInspector(
            urdf_path="/home/xichen/Documents/repos/unimanip_real/assets/g1/G1_120s/urdf/G1_120s.urdf"
        )
            
    def _initialize_simulated_joints(self):
        """Initialize simulated joint positions with default values."""
        self.simulated_joints = {}
        # # Initialize all joints to zero
        # for joint_name in (self.arm_joint_names + self.head_joint_names + 
        #                   self.waist_joint_names + self.gripper_joint_names):
        #     self.simulated_joints[joint_name] = 0.0
        # as reset pose
        reset_cfg = get_reset_joint_cfg("open_laptop")
        for joint_name in (self.arm_joint_names + self.head_joint_names + 
                          self.waist_joint_names + self.gripper_joint_names):
            self.simulated_joints[joint_name] = reset_cfg.get(joint_name, 0.0)
            
    def connect(self):
        """Connect to A2D robot."""
        if self.sim_only:
            print("Running in simulation mode - no actual robot connection")
            self.is_connected = True
            return True
            
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
            
        if self.robot_camera_api is not None:
            self.robot_camera_api.close() # close camera after diconnect
            print("Disconnected from A2D robot camera")
    
        if self.robot_api is not None:
            print("Disconnected from A2D robot")
            self.is_connected = False
    def move_joints(self, joint_positions: Dict[str, float]) -> bool:
        """Move robot joints to specified positions or simulate movement."""
        # get_reset_joint_cfg("open_laptop")
        # curr_q = get_reset_joint_cfg("open_laptop")
        # new_q = joint_positions
        # self._animate_cur_and_new_q(curr_q, new_q)
        if self.sim_only:
            print(f"Simulating joint movement: {joint_positions}")
            # Update simulated joint positions
            curr_q = self.simulated_joints.copy()
            new_q = joint_positions
            self._animate_cur_and_new_q(curr_q, new_q)
            self.simulated_joints.update(joint_positions)
            # self.urdf_inspector.show_robot(self.simulated_joints)
            

            return True
            
        else:
            # comment now to ensure real robot not moving when debugging other parts
            return self._move_joint_real(joint_positions)
            pass
        

    def _animate_cur_and_new_q(self, current_q: Dict[str, float], new_q: Dict[str, float]):
        """
        Visualize the joint movement trajectory using urdf inspector.
        """
        """cfg_trajectory={
        ...     'shoulder_pan_joint' : [-np.pi / 4, np.pi / 4],
        ...     'shoulder_lift_joint' : [0.0, -np.pi / 2.0],
        ...     'elbow_joint' : [0.0, np.pi / 2.0]
        ... })"""

        # fill new q with current_q for missing joints
        for name in self.arm_joint_names + self.head_joint_names + self.waist_joint_names + self.gripper_joint_names:
            if name not in new_q:
                new_q[name] = current_q[name]
        # pair, current_q, and new_q dict to cfg_trajectory format to anim
        cfg_trajectory = {
            name: [current_q[name], new_q[name]] for name in self.arm_joint_names + self.head_joint_names + self.waist_joint_names + self.gripper_joint_names
        }
        self.urdf_inspector.animate_robot(cfg_trajectory)   
    
    def _move_joint_real(self, joint_positions: Dict[str, float], visualization:bool=False) -> bool:
        """Move real robot to target joinst:
            - right arm joints
            - right gripper joint
            
            not moving:
            - left arm joints (keep current position)
            - head joints (keep current position)
            - waist joints (keep current position)
            - left gripper joint (keep current position, closed)
        """
        
        if self.robot_api is None:
            print("Robot API not available, cannot move joints")
            return False
        
        current_q = self.get_current_joints()
        if current_q is None:
            print("Cannot get current joints, abort move")
            return False
        
        left_arm_q = {name: current_q[name] for name in self.left_arm_joint_names}
        head_q = {name: current_q[name] for name in self.head_joint_names}
        waist_q = {name: current_q[name] for name in self.waist_joint_names}
        left_gripper_q = {"idx41_gripper_l_outer_joint1": current_q["idx41_gripper_l_outer_joint1"]}
        
        new_right_arm_q = {name: joint_positions[name] for name in self.right_arm_joint_names}
        new_gripper_q = {name: joint_positions[name] for name in ["idx81_gripper_r_outer_joint1"] if name in joint_positions}
        
        # Combine all joint positions
        new_q = {**left_arm_q, **head_q, **waist_q, **new_right_arm_q, **new_gripper_q, **left_gripper_q}
        
        if visualization:
            # pretty print the curr_q new_q delta of them for each joint
            for name in list(current_q.keys()):
                print(f"{name}: {current_q[name]}->{new_q[name]}: delta:{np.rad2deg(np.abs(current_q[name]-new_q[name]))}")
            self._animate_cur_and_new_q(current_q, new_q)

        try:
            # Implement actual robot joint movement here
            print(f"Moving robot joints: {new_q}")
            
            # self.robot_api.move_arm([new_q[name] for name in self.arm_joint_names])
            # self.robot_api.move_gripper(
            #     [
            #         np.clip(new_q['idx41_gripper_l_outer_joint1'], 0, 1),
            #         np.clip(new_q['idx81_gripper_r_outer_joint1'], 0, 1)
            #     ]
            # )
            self.robot_api.reset(
                arm_positions=[new_q[name] for name in self.arm_joint_names],
                gripper_positions=[
                    new_q["idx41_gripper_l_outer_joint1"],
                    new_q["idx81_gripper_r_outer_joint1"]
                ],
                hand_positions=None, # keep still
                waist_positions=list(waist_q.values()), # keep still
                head_positions=None, # keep still
            )
            return True
        except Exception as e:
            print(f"Failed to move joints: {e}")
            return False

    def get_current_joints(self) -> Dict[str, float]:
        """Get current state from A2D robot or simulated state."""
        if self.sim_only:
            print("Returning simulated joint positions")
            return self.simulated_joints.copy()
            
        if self.robot_api is None:
            print("Robot API not available, returning empty joint dict")
            return {}
            
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
            # /120, since it's value is from 35-120
            gripper_states = (np.array(gripper_states)/120).tolist()
            
            
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

            right_gripper_joint_cfg = {
                "idx81_gripper_r_outer_joint1": gripper_states[1],
                "idx41_gripper_l_outer_joint1": gripper_states[0]
            }
            
            joint_cfg = {
                **arm_joints_cfg,
                **head_joints_cfg,
                **waist_joints_cfg,
                **right_gripper_joint_cfg
            }
            return joint_cfg
            
        except Exception as e:
            print(f"Failed to get robot state: {e}")
            # Return dummy data as fallback
            # return super().get_current_state()
            return None
        
    def reset(self, reset_joint_cfg):
        """Move head/waist/and right arm to reset pose, left arm do not move."""
        if self.sim_only:
            print("Simulating robot reset")
            # Update simulated joints with reset configuration
            self.simulated_joints.update(reset_joint_cfg)
            self.urdf_inspector.show_robot(self.simulated_joints)
            return True
        else:
            # comment now to ensure real robot not moving when debugging other parts
            return self._reset_real_robot(reset_joint_cfg)
            pass
            
        
    def _reset_real_robot(self, reset_joint_cfg, visualize=False):
        if self.robot_api is None:
            print("Robot API not available, cannot reset")
            return False
        
        try:
            # Use current left arm joint to left arm fixed
            current_q = self.get_current_joints()
            current_left_arm_q = {
                name: current_q[name] for name in self.left_arm_joint_names
            }
            
            # User right arm reset joints from reset_joint_cfg
            right_arm_reset_q = {
                name: reset_joint_cfg[name] for name in self.right_arm_joint_names
            }
            # combine left arm current q and right arm reset q
            arm_positions = []
            for name in self.left_arm_joint_names:
                arm_positions.append(current_left_arm_q[name])
            for name in self.right_arm_joint_names:
                arm_positions.append(right_arm_reset_q[name])
                
            head_positions = [
                reset_joint_cfg[name] for name in self.head_joint_names
            ]
            waist_positions = [
                reset_joint_cfg[name] for name in self.waist_joint_names
            ]
            
            
            # gripper_positions = [
            #     reset_joint_cfg[name] for name in self.gripper_joint_names
            # ]
            
            self.robot_api.reset(
                arm_positions=arm_positions,
                gripper_positions=[0.0, 1.0],  # Keep left grippers closed, right gripper open
                hand_positions=None,
                waist_positions=waist_positions,  
                head_positions=head_positions  
            )
            return True
        except Exception as e:
            print(f"Failed to reset robot: {e}")
            return False
    def get_raw_observation(self) -> RawObservation:
        """Get the current observation from the robot."""
        # return None
        raw_obs = RawObservation(
            head_top_rgb=self._get_head_rgb_image(),
            right_wrist_rgb=self._get_right_wrist_rgb_image(),
            head_top_depth=self._get_head_depth_image(),
            right_wrist_depth=self._get_right_wrist_depth_image(),
        )
        return raw_obs
    
    
    def _get_head_rgb_image(self) -> np.ndarray:
        """Simulate getting an RGB image from the head camera."""
        # # For simulation, return a dummy image (e.g., all zeros)
        # return np.zeros((1280, 720, 3), dtype=np.uint8)
        raw_head_top_rgb, _ = self.robot_camera_api.get_latest_image("head")
        return raw_head_top_rgb
        
    def _get_right_wrist_rgb_image(self) -> np.ndarray:
        """Simulate getting an RGB image from the right wrist camera."""
        # # For simulation, return a dummy image (e.g., all zeros)
        # return np.zeros((480, 848, 3), dtype=np.uint8)
        raw_right_wrist_rgb, _ = self.robot_camera_api.get_latest_image("hand_right")
        return raw_right_wrist_rgb

    def _get_head_depth_image(self) -> np.ndarray:
        """Simulate getting a depth image from the head camera."""
        # # For simulation, return a dummy depth image (e.g., all zeros)
        # return np.zeros((1280, 720, 1), dtype=np.float32)
        raw_head_top_depth, _ = self.robot_camera_api.get_latest_image("head_depth")
        return raw_head_top_depth

    def _get_right_wrist_depth_image(self) -> np.ndarray:
        """Simulate getting a depth image from the right wrist camera."""
        # No depth image of right wrist, return a dummy depth image (e.g., all zeros) instead
        return np.zeros((480, 848, 1), dtype=np.float32)

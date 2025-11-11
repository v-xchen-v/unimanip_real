import numpy as np
from typing import Dict, Any

def construct_example_robot_config() -> Dict[str, Any]:
    """
    Construct a default configuration dictionary for the ExampleRobotSDK.
    This can be used for testing or as a template for real configurations.
    """
    config = {
        "robot": {
            "sdk_type": "example",
            "num_joints": 14,
            "joint_mapping": {
                "right_arm_indices": [7, 8, 9, 10, 11, 12, 13],  # Example indices for right arm joints
                "body_indices": [0, 1],
                "right_arm_joint_names": [
                    "idx61_arm_r_joint1",
                    "idx62_arm_r_joint2",
                    "idx63_arm_r_joint3",
                    "idx64_arm_r_joint4",
                    "idx65_arm_r_joint5",
                    "idx66_arm_r_joint6",
                    "idx67_arm_r_joint7"
                ],
                "body_joint_names": [
                    "idx01_body_joint1",
                    "idx02_body_joint2"
                ],
            },
            "sensors": {
                "head_depth_available": True,
                "right_wrist_depth_available": False
            },
            
        },
        "control": {
                "dt": 0.02  # control timestep in seconds
        }
    }
    return config


from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
import sys
sys.path.append(str(PROJECT_ROOT))

from unimanip_real.configs.config_loader import load_config
from unimanip_real.robot.sdk_robot import SDKRobot
from unimanip_real.control.loop import InferenceLoop

def fake_model_client():
    class FakeModelClient:
        def predict(self, model_input):
            # Return zero action for testing
            return {
                "joint_deltas": [0.0] * len(model_input["joint_angles"])
            }
    return FakeModelClient()

def main():
    # Load configuration
    robot_cfg = construct_example_robot_config()
    task_config_path = Path(__file__).parent.parent / "configs" / "task_config.yaml"
    task_cfg = load_config(task_config_path)

    # Initialize fake robot
    example_robot = SDKRobot(robot_cfg, task_cfg)

    # fake model client
    model_client = fake_model_client()
    
    # Initialize control loop
    control_loop = InferenceLoop(
        robot=example_robot,
        model_client=model_client,
        config=robot_cfg,
    )

    # Run interactive control loop
    control_loop.run_interactive()
    
if __name__ == "__main__":
    main()
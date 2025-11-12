# A script to run the fake robot control loop using a specified configuration file for easy debugging
# - The inference loop will run in interactive mode, allowing step-by-step execution
# - Obs Preprocessing and action postprocessing are included
# - Others exception real model inference, robot executation



from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
import sys
sys.path.append(str(PROJECT_ROOT))

from unimanip_real.configs.config_loader import load_config
from unimanip_real.robot.a2d_robot import A2DRobotSDK
from unimanip_real.control.loop import InferenceLoop

def fake_model_client():
    class FakeModelClient:
        def predict(self, model_input):
            # a fake action pose [x, y, z, rw, rx, ry, rz]
            import numpy as np
            from scipy.spatial.transform import Rotation as R
            # quat_wxyz = R.from_euler('xyz', [0, 0, 0]).as_quat(scalar_first=True)
            euler_angles = [0, 0, 0]
            xyz = [0.05, 0.05, 0.05]
            gripper = [0.5]
            action_delta_pose = xyz + euler_angles+ gripper

            # Return zero action for testing
            return {
                # "joint_deltas": [0.0] * len(model_input["joint_angles"])
                "action": action_delta_pose
            }
    return FakeModelClient()

def main():
    # Load configuration
    # config_path = Path(__file__).parent.parent / "configs" / "fake_robot_config.yaml"
    # robot_cfg = load_config(config_path)
    robot_cfg = {}

    # Initialize fake robot
    robot_api = A2DRobotSDK(robot_cfg, sim_only=True)

    # fake model client
    model_client = fake_model_client()
    
    # Initialize control loop
    control_loop = InferenceLoop(
        robot=robot_api,
        model_client=model_client,
        config=robot_cfg,
    )

    # Run interactive control loop
    control_loop.run_interactive()
    
if __name__ == "__main__":
    main()
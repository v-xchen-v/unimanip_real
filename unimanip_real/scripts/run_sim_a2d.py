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

from unimanip_real.model.vla_client import fake_model_client
from unimanip_real.model.vla_client import VlaModelClient
    

def main():
    # Load configuration
    # config_path = Path(__file__).parent.parent / "configs" / "fake_robot_config.yaml"
    # robot_cfg = load_config(config_path)
    robot_cfg = {}

    # Initialize fake robot
    robot_api = A2DRobotSDK(robot_cfg, sim_only=True)

    # fake model client
    # model_client = fake_model_client() # for debugging
    model_client = VlaModelClient()
    
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
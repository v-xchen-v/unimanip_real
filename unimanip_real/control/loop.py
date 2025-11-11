import time
from typing import Dict, Any
from ..robot.sdk_robot import SDKRobot
from ..model.vla_client import APICClient
from .observation import build_model_input
from .action_postproc import action_to_joint_targets
from ..constrants import get_reset_joint_cfg
from ..robot.base_robot import BaseRobotSDK

class InferenceLoop:
    def __init__(
        self,
        robot: BaseRobotSDK,
        model_client: APICClient,
        config: Dict[str, Any],
        task_name: str = "open_laptop",
    ):
        self.robot = robot
        self.model_client = model_client
        self.config = config
        self.dt = float(config["control"].get("dt", 0.1))
        self.log_every = int(config["control"].get("log_every", 10))
        
        # Task-specific setup can be added here if needed
        self.task_reset_joint_cfg = get_reset_joint_cfg(task_name)

    def step_once(self, step_idx: int) -> None:
        # 1) get observation from robot
        obs = self.robot.get_raw_observation()

        # 2) pack into model input
        model_input = build_model_input(obs)

        # 3) call model
        action = self.model_client.predict(model_input)

        # 4) convert to joint targets
        q_target = action_to_joint_targets(
            action=action,
            current_q={},
            config=self.config,
        )

        # 5) send to robot
        self.robot.move_joints(q_target)

        if step_idx % self.log_every == 0:
            print(f"[Loop] step {step_idx} done.")

    def run_interactive(self) -> None:
        """
        Keyboard commands:
          r: reset robot using init joints
          n: run one step
          m: enter auto mode (continuous steps until Ctrl+C)
          q: quit
        """
        self.robot.connect()
        try:
            print("Commands: [r]=reset, [n]=next step, [m]=auto run, [q]=quit")
            step_idx = 0
            while True:
                cmd = input("Command (r/n/m/q): ").strip().lower()
                if cmd == "r":
                    print("[Loop] Resetting robot...")
                    self.robot.reset(self.task_reset_joint_cfg)
                elif cmd == "n":
                    print("[Loop] Running one step...")
                    self.step_once(step_idx)
                    step_idx += 1
                elif cmd == "m":
                    print("[Loop] Auto mode: running until Ctrl+C...")
                    try:
                        while True:
                            self.step_once(step_idx)
                            step_idx += 1
                            time.sleep(self.dt)
                        # break by Ctrl+C
                    except KeyboardInterrupt:
                        print("\n[Loop] Auto mode interrupted, back to manual.")
                elif cmd == "q":
                    print("[Loop] Quitting.")
                    break
                else:
                    print("[Loop] Unknown command, use r/n/m/q.")
        finally:
            self.robot.disconnect()

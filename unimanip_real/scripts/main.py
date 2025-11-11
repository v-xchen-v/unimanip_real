# somewhere in setup
from unimanip_real.robot.sdk_robot import SDKRobot
from unimanip_real.control.observation import preprocess_raw_observation



sdk_robot = SDKRobot(cfg)
sdk_robot.connect()

# in the loop:
raw_obs = sdk_robot.get_raw_observation()
model_input = preprocess_raw_observation(raw_obs, cfg)
action = model_client.predict(model_input)

# postprocess action -> concatenated joints [body(2), right_arm(7)]
q_target = action_to_joint_targets(
    action=action,
    current_q=raw_obs.full_joint_vector,
    config=cfg,
)

sdk_robot.move_full_concatenated_joints(q_target, duration=cfg["control"].get("move_duration", 0.5))

def get_reset_joint_cfg(task_name: str, left_arm_only=False) -> dict:
    """Get the reset joint configuration for a given task."""
    if left_arm_only:
        return {name: reset_joint_cfg[task_name][name] for name in left_arm_joint_names}
    
    return reset_joint_cfg.get(task_name, {})


left_arm_joint_names = [
    "idx21_arm_l_joint1",
    "idx22_arm_l_joint2",
    "idx23_arm_l_joint3",
    "idx24_arm_l_joint4",
    "idx25_arm_l_joint5",
    "idx26_arm_l_joint6",
    "idx27_arm_l_joint7",
]
right_arm_joint_names = [
    "idx61_arm_r_joint1",
    "idx62_arm_r_joint2",
    "idx63_arm_r_joint3",
    "idx64_arm_r_joint4",
    "idx65_arm_r_joint5",
    "idx66_arm_r_joint6",
    "idx67_arm_r_joint7",
]
arm_joint_names = left_arm_joint_names + right_arm_joint_names

reset_joint_cfg = {
    "open_laptop": {
        # Body
        "idx01_body_joint1": 0.0,
        "idx02_body_joint2": 0.0,
        # Head
        "idx11_head_joint1": 0.0,
        "idx12_head_joint2": 0.6,
        # Right arm
        "idx61_arm_r_joint1": 0.4,
        "idx62_arm_r_joint2": -1.4,
        "idx63_arm_r_joint3": -0.2,
        "idx64_arm_r_joint4": 1.2,
        "idx65_arm_r_joint5": -2.9,
        "idx66_arm_r_joint6": 0.0,
        "idx67_arm_r_joint7": 0.0,
        # Right hand
        # "idx71_gripper_r_inner_joint1": 0.0,
        # "idx72_gripper_r_inner_joint3": 0.0,
        # "idx73_gripper_r_inner_joint4": 0.0,
        # "idx94_gripper_r_inner_joint0": 0.0,
        "idx81_gripper_r_outer_joint1": 1.0,
        # "idx82_gripper_r_outer_joint3": 0.0,
        # "idx83_gripper_r_outer_joint4": 0.0,
        # "idx93_gripper_r_outer_joint0": 0.0,
        # Left arm
        "idx21_arm_l_joint1": 0.0,
        "idx22_arm_l_joint2": 1.4,
        "idx23_arm_l_joint3": 0.0,
        "idx24_arm_l_joint4": 0.0,
        "idx25_arm_l_joint5": 0.0,
        "idx26_arm_l_joint6": 0.0,
        "idx27_arm_l_joint7": 0.0,
        # # Left hand
        # "idx31_gripper_l_inner_joint1": 0.0,
        # "idx32_gripper_l_inner_joint3": 0.0,
        # "idx33_gripper_l_inner_joint4": 0.0,
        # "idx54_gripper_l_inner_joint0": 0.0,
        "idx41_gripper_l_outer_joint1": 0.0,
        # "idx42_gripper_l_outer_joint3": 0.0,
        # "idx43_gripper_l_outer_joint4": 0.0,
        # "idx53_gripper_l_outer_joint0": 0.0,
    }
}
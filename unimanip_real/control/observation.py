from typing import Dict, Any
from ..core.types import RawObservation
from .rawobs_preproc import resize_images, convert_images_to_pil

def build_model_input(obs: RawObservation) -> Dict[str, Any]:
    # in obs, find head_top_rgb, head_depth, right_wrist_rgb, right_wrist_depth if have,
    # and construct to a image list in order
    
    required_view_names = [
        "head_top_rgb",
        "head_depth",
        "right_wrist_rgb",
        "right_wrist_depth",
    ]
    images = []
    for view_name in required_view_names:
        img = getattr(obs, view_name, None)
        if img is not None:
            images.append(img)
    
    # preprocess of images, resize images, then convert to pil
    resized_images = resize_images(images)
    pil_images = convert_images_to_pil(resized_images)
    
    
    model_input = {
        "images": pil_images,
        # "joint_angles": obs.right_arm_q.tolist() + obs.body_q.tolist(),
        # "ee_pose_right": obs.ee_pose_right.tolist(),
    }
    # if obs.head_top_depth is not None:
    #     model_input["head_top_depth"] = obs.head_top_depth.tolist()
    # if obs.right_wrist_depth is not None:
    #     model_input["right_wrist_depth"] = obs.right_wrist_depth.tolist()
    return model_input
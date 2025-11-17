from typing import Dict, Any
from ..core.types import RawObservation
from .rawobs_preproc import resize_images, convert_images_to_pil
from .rawobs_preproc import normalize_depth, duplicate_depth_channel
import numpy as np

def build_model_input(obs: RawObservation, save_log=True) -> Dict[str, Any]:
    # in obs, find head_top_rgb, head_depth, right_wrist_rgb, right_wrist_depth if have,
    # and construct to a image list in order
    
    required_view_names = [
        "head_top_rgb",
        "head_top_depth",
        "right_wrist_rgb",
        "right_wrist_depth",
    ]
    images = []
    for view_name in required_view_names:
        img = getattr(obs, view_name, None)
        if img is not None:
            images.append(img)
    
    # normalize depth image of head_top_depth
    for idx, view_name in enumerate(required_view_names):
        if "depth" in view_name:
            images[idx] = normalize_depth(images[idx])
            
    # duplicate depth channel if single channel
    for idx, view_name in enumerate(required_view_names):
        if "depth" in view_name:
            images[idx] = duplicate_depth_channel(images[idx])
    
    # preprocess of images, resize images, then convert to pil
    resized_images = resize_images(images)
    pil_images = convert_images_to_pil(resized_images)
    
    # Check the all image are shape as (520, 520, 3)
    for idx, img in enumerate(pil_images):
        if img.size != (520, 520):
            raise ValueError(f"Image at index {idx} has size {img.size}, expected (520, 520)")
    
    model_input = {
        "images": pil_images,
        "task_description": "open laptop",
        # "task_description": "pick up the bottle on table",
        "state": np.zeros((6, ), dtype=np.float32).tolist(),  # dummy state
    }
    # if obs.head_top_depth is not None:
    #     model_input["head_top_depth"] = obs.head_top_depth.tolist()
    # if obs.right_wrist_depth is not None:
    #     model_input["right_wrist_depth"] = obs.right_wrist_depth.tolist()
    if save_log:
        # save the images to disk for debugging
        import os
        from PIL import Image
        log_dir = "debug_logs"
        os.makedirs(log_dir, exist_ok=True)
        for idx, img in enumerate(pil_images):
            img.save(os.path.join(log_dir, f"input_image_{idx}.png"))
            
        # save the other parts as json
        import json
        with open(os.path.join(log_dir, "model_input.json"), "w") as f:
            json.dump({
                "task_description": model_input["task_description"],
                "state": model_input["state"],
            }, f, indent=4)
    return model_input
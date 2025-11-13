import os
from datetime import datetime
from typing import Dict, Any
from PIL import Image


class ImageLogger:
    """Handles image logging for inference runs.
    debug_logs/run_20251112_143025/
    ├── head_top_0.png
    ├── head_top_depth_0.png
    ├── right_wrist_0.png
    ├── right_wrist_depth_0.png
    ├── head_top_1.png
    ├── head_top_depth_1.png
    └── ...
    """
    
    def __init__(self, base_log_dir: str = "debug_logs"):
        self.base_log_dir = base_log_dir
        self.log_dir = self._create_log_directory()
        print(f"[ImageLogger] Logging images to: {self.log_dir}")
    
    def _create_log_directory(self) -> str:
        """Create a new log directory for this run."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join(self.base_log_dir, f"run_{timestamp}")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def reset(self) -> None:
        """Reset the logger with a new log directory.
        
        First session: debug_logs/run_20251113_090000/
        ├── head_top_0.png, head_top_1.png, head_top_2.png...

        [Press 'r' to reset]

        Second session: debug_logs/run_20251113_090245/
        ├── head_top_0.png, head_top_1.png, head_top_2.png...  # Fresh start!
        """
        self.log_dir = self._create_log_directory()
        print(f"[ImageLogger] Reset - new logging directory: {self.log_dir}")
    
    def save_images(self, model_input: Dict[str, Any], step_idx: int) -> None:
        """Save images from model_input to log directory."""
        if "images" not in model_input or len(model_input["images"]) < 4:
            print(f"[ImageLogger] Warning: Expected 4 images, got {len(model_input.get('images', []))}")
            return
        
        images = model_input["images"]
        image_names = [
            f"head_top_{step_idx}.png",
            f"head_top_depth_{step_idx}.png", 
            f"right_wrist_{step_idx}.png",
            f"right_wrist_depth_{step_idx}.png"
        ]
        
        for i, (image, name) in enumerate(zip(images, image_names)):
            if isinstance(image, Image.Image):
                image_path = os.path.join(self.log_dir, name)
                image.save(image_path)
                print(f"[ImageLogger] Saved {name}")
            else:
                print(f"[ImageLogger] Warning: Image {i} is not a PIL Image, got {type(image)}")

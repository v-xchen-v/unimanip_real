from typing import Dict, Any
from vla_serving.sdk import VLAClient

class APICClient:
    def predict(self, model_input: Dict[str, Any]) -> Dict[str, Any]:
        # Implement the API call to VLA here
        pass
    
class VlaModelClient:
    def __init__(self, base_url: str="http://10.150.240.101:5600") -> None:
        self.client = VLAClient(base_url=base_url)

    def predict(self, model_input: Dict[str, Any]) -> Dict[str, Any]:
        """Call VLA API to get prediction.
        
         model_input = {
            "images": pil_images,
            "task_description": "open laptop",
            "state": np.zeros((6, ), dtype=np.float32).tolist(),  # dummy state
        }
        """
        """client.infer(
            images=image_list,
            task_description=task_description,
            state=state
        )"""
        
        response = self.client.infer(**model_input)
        return response
    
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
                "action": [action_delta_pose]
            }
    return FakeModelClient()
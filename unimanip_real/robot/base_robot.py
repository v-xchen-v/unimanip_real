from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
import numpy as np
from ..control.observation import RawObservation

# TODO: use this contract to fake_robot and sdk_robot
class BaseRobotSDK(ABC):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        
    @abstractmethod
    def connect(self) -> None:
        """Connect to the robot hardware or simulator."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the robot hardware or simulator."""
        pass
    
    @abstractmethod
    def reset(self, reset_joint_cfg: Dict[str, float]) -> None:
        """Reset the robot to its initial state."""
        pass
    
    @abstractmethod
    def get_raw_observation(self) -> RawObservation: # Dict[str, Any]:
        """Get the current observation from the robot."""
        pass
    
    @abstractmethod
    def move_joints(self, joint_cfg: Dict[str, float]) -> None:
        """Move the robot joints to the specified positions."""
        pass
    
    @abstractmethod
    def get_current_joints(self) -> Dict[str, float]:
        """Get the current joint positions of the robot."""
        pass
    
    @abstractmethod
    def move_wheel(self, distance_cm: float, speed_cm_s: float) -> bool:
        """Move the robot base wheels by a certain distance at a specified speed."""
        pass